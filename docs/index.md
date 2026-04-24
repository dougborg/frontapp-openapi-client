# Frontapp OpenAPI Client Documentation

Welcome to the **Frontapp OpenAPI Client** documentation. A modern, pythonic client for
Front's [Core API](https://dev.frontapp.com/reference/introduction) — the
customer-communication platform that unifies email, SMS, chat, and social inboxes — with
automatic resilience at the transport layer.

## Features

- **Transport-layer resilience**: retries, rate-limit awareness, and pagination helpers
  at the HTTP transport level, applied uniformly to every endpoint.
- **Type-safe**: full type hints, Pydantic domain models, and attrs-based generated
  request/response models.
- **Async/await**: built on httpx for modern Python async.
- **Domain helpers**: hand-written ergonomic facades (`client.conversations.…`) layered
  on top of the generated surface for the highest-value resources.
- **Zero-wrapper philosophy**: resilience is inherited automatically — all 233 generated
  API methods get it without any decorator plumbing.

## Quick Start

```python
import asyncio
from frontapp_public_api_client import FrontappClient

async def main():
    async with FrontappClient() as client:
        conversations = await client.conversations.list(
            q="status:open tag:urgent", limit=25
        )
        for conv in conversations:
            print(f"{conv.id}: {conv.subject!r} ({conv.status})")

asyncio.run(main())
```

## Architecture

The client uses a **transport-layer resilience** approach: retries, rate-limit
retry-after handling, and request/response observability live in the httpx transport
stack rather than as per-method decorators. This means:

- All 233 generated API methods get resilience automatically
- Regenerating the client from a new spec version preserves all behaviors
- Type safety is preserved end-to-end
- Overhead stays at the lowest reasonable level

On top of the generated API, hand-written **domain helpers** wrap the most-used
resources with ergonomic signatures and Pydantic domain models:

- `client.conversations.{list, get, search, update, reply, …}` — ✅ available today
- `client.contacts.…` — ⏳ planned (see issues)
- `client.messages.…` — ⏳ planned
- `client.tags.…`, `client.inboxes.…`, `client.teammates.…` — ⏳ planned

Anything without a helper yet is still accessible via `client.api.<tag>.<operation>(…)`
or direct imports from `frontapp_public_api_client.api`.

## Documentation Structure

```{toctree}
:maxdepth: 2
:caption: User Guides

client/guide
client/cookbook
client/testing
CONTRIBUTING
```

```{toctree}
:maxdepth: 2
:caption: MCP Server

mcp-server/README
mcp-server/development
mcp-server/deployment
```

```{toctree}
:maxdepth: 2
:caption: API Reference

autoapi/frontapp_public_api_client/index
```

```{toctree}
:maxdepth: 2
:caption: Development

RELEASE
MONOREPO_SEMANTIC_RELEASE
UV_USAGE
PYPI_SETUP
```

```{toctree}
:maxdepth: 2
:caption: Project Information

client/CHANGELOG
CODE_OF_CONDUCT
```

## Installation

```bash
pip install frontapp-openapi-client
```

## Configuration

```python
# Via environment variables (.env file)
FRONTAPP_API_KEY=your_api_key_here
FRONTAPP_BASE_URL=https://api2.frontapp.com  # optional override

# Via direct initialization
from frontapp_public_api_client import FrontappClient

async with FrontappClient(
    api_key="your_api_key_here",
    base_url="https://api2.frontapp.com",
    max_retries=5,
) as client:
    ...
```

Get an API token at **Front → Settings → Developers → API tokens**.

## Support

- **Documentation**: [GitHub Pages](https://dougborg.github.io/frontapp-openapi-client/)
- **Issues**:
  [GitHub Issues](https://github.com/dougborg/frontapp-openapi-client/issues)
- **Source**: [GitHub Repository](https://github.com/dougborg/frontapp-openapi-client)

## License

MIT License — see
[LICENSE](https://github.com/dougborg/frontapp-openapi-client/blob/main/LICENSE).
