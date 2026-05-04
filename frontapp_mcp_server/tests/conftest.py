"""Shared pytest fixtures for MCP server tests."""

import os
from unittest.mock import MagicMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def frontapp_context():
    """Context fixture backed by a real FrontappClient for integration tests.

    Skipped when FRONTAPP_API_KEY is not set.
    """
    api_key = os.getenv("FRONTAPP_API_KEY")
    if not api_key:
        pytest.skip("FRONTAPP_API_KEY not set - skipping integration test")

    try:
        from frontapp_public_api_client import FrontappClient
    except ImportError:
        pytest.skip("frontapp_public_api_client not installed")

    context = MagicMock()
    mock_request_context = MagicMock()
    mock_lifespan_context = MagicMock()

    base_url = os.getenv("FRONTAPP_BASE_URL", "https://api2.frontapp.com")
    client = FrontappClient(
        api_key=api_key,
        base_url=base_url,
        timeout=30.0,
        max_retries=3,
    )

    mock_lifespan_context.client = client
    mock_request_context.lifespan_context = mock_lifespan_context
    context.request_context = mock_request_context

    yield context


def create_mock_context():
    """Build a mock FastMCP context for unit tests.

    Returns a (context, lifespan_context) tuple where the lifespan is the
    same mock the tool sees via ``context.request_context.lifespan_context``.
    Test cases assign ``lifespan.client = AsyncMock()`` (or similar) to
    stub the helpers the tool calls into.
    """
    context = MagicMock()
    mock_request_context = MagicMock()
    mock_lifespan_context = MagicMock()
    context.request_context = mock_request_context
    mock_request_context.lifespan_context = mock_lifespan_context
    return context, mock_lifespan_context


@pytest.fixture
def mock_context():
    """Mock FastMCP context fixture."""
    return create_mock_context()


@pytest.fixture
def mcp_tool_capture():
    """Factory: register a tools module against a fake FastMCP and return
    the captured ``{name: callable}`` dict.

    New tool test files should use this fixture. Existing per-vertical
    test files (test_contacts_tools, test_drafts_tools, test_messages_tools,
    test_tags_tools, test_inboxes_tools) still define their own copy of
    the same pattern — migration is tracked as follow-up cleanup so this
    PR doesn't churn 5 working test files.
    """

    def factory(register_tools_fn) -> dict[str, object]:
        captured: dict[str, object] = {}

        class FakeMCP:
            def tool(self, **kwargs: object):
                name = kwargs["name"]
                assert isinstance(name, str), (
                    f"tool name must be a str, got {type(name).__name__}"
                )

                def decorator(fn):
                    captured[name] = fn
                    return fn

                return decorator

        register_tools_fn(FakeMCP())
        return captured

    return factory
