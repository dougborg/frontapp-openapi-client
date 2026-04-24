"""Frontapp MCP Server - FastMCP server with environment-based authentication.

This module implements the core MCP server for the Frontapp API, providing
tools and resources for looking up and updating order status.

Features:
- Environment-based authentication (FRONTAPP_API_KEY)
- Automatic client initialization with error handling
- Lifespan management for FrontappClient context
- Production-ready with transport-layer resilience
- Structured logging with observability
- Response caching for read-only tools (FastMCP 2.13+)
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from fastmcp.server.auth import AuthProvider  # pragma: no cover

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.middleware.caching import (
    CallToolSettings,
    ReadResourceSettings,
    ResponseCachingMiddleware,
)
from key_value.aio.stores.memory import MemoryStore

from frontapp_mcp import __version__
from frontapp_mcp._fastmcp_patches import apply_fastmcp_patches as _apply_patches
from frontapp_mcp.logging import get_logger, setup_logging
from frontapp_mcp.services import Services
from frontapp_public_api_client import FrontappClient

# Apply FastMCP patches for Pydantic 2.12+ compatibility BEFORE registering tools
_apply_patches()

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[Services]:
    """Manage server lifespan and FrontappClient lifecycle.

    This context manager:
    1. Loads environment variables from .env file
    2. Validates required configuration (FRONTAPP_API_KEY)
    3. Initializes FrontappClient with error handling
    4. Provides client to tools via ServerContext
    5. Ensures proper cleanup on shutdown

    Args:
        server: FastMCP server instance

    Yields:
        Services: Context object containing initialized FrontappClient

    Raises:
        ValueError: If FRONTAPP_API_KEY environment variable is not set
        Exception: If FrontappClient initialization fails
    """
    # Load environment variables
    load_dotenv()

    # Get configuration from environment
    api_key = os.getenv("FRONTAPP_API_KEY")
    base_url = os.getenv("FRONTAPP_BASE_URL", "https://api2.frontapp.com")

    # Validate required configuration
    if not api_key:
        logger.error(
            "authentication_failed",
            reason="FRONTAPP_API_KEY environment variable is required",
            message="Please set it in your .env file or environment.",
        )
        raise ValueError(
            "FRONTAPP_API_KEY environment variable is required for authentication"
        )

    logger.info("server_initializing", version=__version__, base_url=base_url)

    try:
        # Initialize FrontappClient with automatic resilience features
        async with FrontappClient(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,
            max_retries=5,
            max_pages=100,
        ) as client:
            logger.info(
                "client_initialized",
                timeout=30.0,
                max_retries=5,
                max_pages=100,
            )

            context = Services(client=client)
            logger.info("server_ready", version=__version__)
            yield context

    except ValueError as e:
        # Authentication or configuration errors
        logger.error("initialization_failed", error_type="ValueError", error=str(e))
        raise
    except Exception as e:
        # Unexpected errors during initialization
        # Note: exc_info intentionally omitted to avoid leaking file paths and
        # module internals in production logs. The exception is re-raised for
        # the caller to handle debugging.
        logger.error(
            "initialization_failed",
            error_type=type(e).__name__,
            error=str(e),
        )
        raise
    finally:
        logger.info("server_shutting_down")


def _build_auth() -> "AuthProvider | None":
    """Build auth provider from environment configuration.

    Supports two modes, selected by environment variables:
    - MCP_AUTH_TOKEN: Simple bearer token auth (dev/personal use)
    - MCP_GITHUB_CLIENT_ID + MCP_GITHUB_CLIENT_SECRET + MCP_BASE_URL: GitHub OAuth

    Returns None when no auth env vars are set (unauthenticated).
    """
    github_id = os.getenv("MCP_GITHUB_CLIENT_ID")
    github_secret = os.getenv("MCP_GITHUB_CLIENT_SECRET")
    base_url = os.getenv("MCP_BASE_URL")

    github_vars = {
        "MCP_GITHUB_CLIENT_ID": github_id,
        "MCP_GITHUB_CLIENT_SECRET": github_secret,
        "MCP_BASE_URL": base_url,
    }
    if all(github_vars.values()):
        from fastmcp.server.auth.providers.github import GitHubProvider

        return GitHubProvider(
            client_id=github_id,  # type: ignore[arg-type]
            client_secret=github_secret,  # type: ignore[arg-type]
            base_url=base_url,  # type: ignore[arg-type]
        )
    if any(github_vars.values()):
        missing = [k for k, v in github_vars.items() if not v]
        logger.warning(
            "incomplete_github_oauth_config",
            missing=missing,
            msg="Set all three vars for GitHub OAuth, or remove them for bearer token",
        )

    token = os.getenv("MCP_AUTH_TOKEN")
    if token:
        from fastmcp.server.auth import StaticTokenVerifier

        return StaticTokenVerifier(
            tokens={token: {"client_id": "frontapp-mcp", "scopes": ["all"]}},
        )

    return None


_auth = _build_auth()

# Initialize FastMCP server with lifespan management
mcp = FastMCP(
    name="frontapp",
    version=__version__,
    lifespan=lifespan,
    auth=_auth,
    instructions="""\
Frontapp MCP Server — Read and act on Front customer-communication data.

## Domain Model

- **Conversations** (`cnv_*`) are email/SMS/chat threads. Each has a `status`
  (`open`, `archived`, `deleted`, `spam`), optional `assignee` (teammate),
  `tags`, and a `recipient` (customer handle). Conversations belong to an
  `inbox` and flow on a `channel`.
- **Messages** are individual emails/SMS/chat posts inside a conversation.
  Replying appends a message on the conversation's original channel.
- **Comments** are teammate-only internal notes on a conversation — never
  sent to the customer.
- **Teammates** (`tea_*`) are human users; **Contacts** are external parties.
- **Tags**, **inboxes**, and **teammates** are workspace-level reference data.

## Tool Selection Guide

**Finding conversations:**
  list_conversations (reverse-chronological, with q= search) |
  search_conversations (when q is the main filter) |
  get_conversation (full detail by id)

**Reading inside a conversation:**
  list_conversation_messages | list_conversation_comments

**Responding (all use two-step confirm):**
  reply_to_conversation — outbound message to the customer
  add_conversation_comment — internal note, teammates only
  update_conversation — archive/reopen, reassign, retag, move inbox

## Front Search Syntax (q parameter)

  status:open | status:archived | tag:urgent | assignee:me |
  is:unassigned | inbox:support | after:2024-01-01 | before:2024-12-31

Combine with AND / OR: `status:open AND tag:urgent`

## Safety Pattern

All mutation tools use a two-step confirm:
1. Call with confirm=false — returns a preview (no changes made)
2. Call with confirm=true — executes and prompts for explicit user approval
   via elicitation

## Rate Limits

Front enforces per-endpoint rate limits; the client retries 429 responses
automatically with exponential backoff. Expect ~60 req/min on most endpoints.
""",
)

# Add response caching middleware with TTLs for read-only tools
_READ_ONLY_TOOLS = [
    "list_conversations",
    "get_conversation",
    "search_conversations",
    "list_conversation_messages",
    "list_conversation_comments",
]

mcp.add_middleware(
    ResponseCachingMiddleware(
        cache_storage=MemoryStore(),
        call_tool_settings=CallToolSettings(
            ttl=30,
            included_tools=_READ_ONLY_TOOLS,
        ),
        read_resource_settings=ReadResourceSettings(ttl=60),
    )
)
logger.info(
    "middleware_added",
    middleware="ResponseCachingMiddleware",
    storage="MemoryStore",
    cached_tools=_READ_ONLY_TOOLS,
    tool_ttl=30,
    resource_ttl=60,
)

# Register all tools, resources, and prompts with the mcp instance
# This must come after mcp initialization
from frontapp_mcp.prompts import register_all_prompts  # noqa: E402
from frontapp_mcp.resources import register_all_resources  # noqa: E402
from frontapp_mcp.tools import register_all_tools  # noqa: E402

register_all_tools(mcp)
register_all_resources(mcp)
register_all_prompts(mcp)


def main(
    transport: Literal["stdio", "http", "sse", "streamable-http"] = "stdio",
    host: str = "127.0.0.1",
    port: int = 8765,
) -> None:
    """Main entry point for the Frontapp MCP Server.

    This function is called when running the server via:
    - uvx frontapp-mcp-server
    - python -m frontapp_mcp
    - frontapp-mcp-server (console script)

    Args:
        transport: Transport protocol ("stdio", "sse", or "http"). Default: "stdio"
        host: Host to bind to for HTTP/SSE transports. Default: "127.0.0.1"
        port: Port to bind to for HTTP/SSE transports. Default: 8765
    """
    logger.info(
        "server_starting",
        version=__version__,
        transport=transport,
        host=host,
        port=port,
    )
    if _auth is not None:
        provider = type(_auth).__name__
        logger.info("auth_configured", provider=provider)
    elif transport != "stdio":
        logger.warning(
            "no_auth_configured",
            transport=transport,
            msg="MCP endpoint is unauthenticated — set MCP_AUTH_TOKEN or "
            "MCP_GITHUB_CLIENT_ID + MCP_GITHUB_CLIENT_SECRET",
        )
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport=transport, host=host, port=port)


if __name__ == "__main__":
    main()
