# Frontapp — API Client Ecosystem

Multi-language client ecosystem for the
[Frontapp API](https://api2.frontapp.com), a small REST API for **reading
and updating the status of orders**. The Frontapp API is used by merchants to expose
production progress to their customers (order received → in production → shipped, etc.)
and to update that status from their own systems.

This monorepo ships:

- A production-grade Python client with transport-layer retries, rate-limit awareness,
  and auto-pagination across all list endpoints.
- A TypeScript client generated from the same OpenAPI spec.
- An MCP server exposing Frontapp operations as tools to AI assistants like Claude
  Desktop.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![OpenAPI 3.1.0](https://img.shields.io/badge/OpenAPI-3.1.0-green.svg)](https://spec.openapis.org/oas/v3.1.0)

## Packages

| Package                                                  | Language   | Version | Description                                        |
| -------------------------------------------------------- | ---------- | ------- | -------------------------------------------------- |
| [frontapp-openapi-client](frontapp_public_api_client/) | Python     | 0.1.0   | API client with transport-layer resilience         |
| [frontapp-mcp-server](frontapp_mcp_server/)            | Python     | 0.1.0   | Model Context Protocol server for AI assistants    |
| [frontapp-client](packages/frontapp-client/)           | TypeScript | 0.1.0   | TypeScript/JavaScript client with full type safety |

## Features

| Feature                                     | Python | TypeScript | MCP Server              |
| ------------------------------------------- | ------ | ---------- | ----------------------- |
| Automatic retries (network + 5xx)           | Yes    | Yes        | Yes (via Python client) |
| Rate-limit retry with exponential backoff   | Yes    | Yes        | Yes                     |
| Auto-pagination (page + per_page with meta) | Yes    | Yes        | Yes                     |
| Two-step confirm on mutations               | —      | —          | Yes                     |
| Full type safety (attrs + Pydantic / TS)    | Yes    | Yes        | Yes                     |
| AI tool surface                             | —      | —          | Claude, Cursor, etc.    |

## Quick Start

### Python Client

```bash
pip install frontapp-openapi-client
```

```python
import asyncio
from frontapp_public_api_client import FrontappClient

async def main():
    async with FrontappClient() as client:
        orders = await client.orders.list(per_page=25)
        for order in orders:
            status = order.status.name if order.status else "(no status)"
            print(f"{order.name}: {status}")

asyncio.run(main())
```

### TypeScript Client

```bash
npm install frontapp-client
```

```typescript
import { FrontappClient } from "frontapp-client";

const client = await FrontappClient.create();
const response = await client.get("/orders");
const { data, meta } = await response.json();
console.log(`Found ${meta.total} orders (page ${meta.current_page}/${meta.last_page})`);
```

### MCP Server (Claude Desktop)

```bash
pip install frontapp-mcp-server
```

Add to Claude Desktop config
(`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "frontapp": {
      "command": "uvx",
      "args": ["frontapp-mcp-server"],
      "env": {
        "FRONTAPP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Configuration

All packages authenticate via bearer token:

1. **Environment variable**: `FRONTAPP_API_KEY`
1. **`.env` file**: `FRONTAPP_API_KEY=your-key`
1. **Direct parameter**: pass `api_key=...` to the client constructor
1. **`~/.netrc`**: `machine api2.frontapp.com` + `password your-key`

```bash
# .env
FRONTAPP_API_KEY=your-api-key-here
FRONTAPP_BASE_URL=https://api2.frontapp.com  # optional override
```

## API Coverage

The Frontapp API is intentionally small and focused on order status. All 7 endpoints
are covered:

| Tag      | Method | Path                           | Purpose                                                        |
| -------- | ------ | ------------------------------ | -------------------------------------------------------------- |
| Orders   | GET    | `/orders`                      | Paginated list with filters (search, status, tags, due date).  |
| Orders   | GET    | `/orders/{id}`                 | Full detail for one order including history.                   |
| Orders   | GET    | `/orders/lookup`               | Look up an order by order number + customer email.             |
| Orders   | GET    | `/orders/{id}/viable-statuses` | Statuses that are valid transitions from the current state.    |
| Orders   | POST   | `/orders/{id}/status`          | Change the status of a single order.                           |
| Orders   | POST   | `/orders/{id}/comment`         | Add a history comment (5/min rate limit).                      |
| Orders   | POST   | `/orders/{id}/due-date`        | Set or update the due date (single date or range).             |
| Orders   | POST   | `/orders/bulk-status`          | Update up to 50 orders at once (5/min, queued asynchronously). |
| Statuses | GET    | `/statuses`                    | Every status defined on the account (code, name, color).       |

**Conventions:**

- Bearer token auth on every endpoint (`Authorization: Bearer <FRONTAPP_API_KEY>`).
- `GET /orders` returns
  `{"data": [...], "meta": {current_page, last_page, per_page, total, from, to}}`.
- `GET /statuses` and `GET /orders/{id}/viable-statuses` return raw JSON arrays.
- Pagination uses `page` + `per_page` query params (`per_page` max 100).
- Rate limits are documented per-endpoint (60/min on most, 5/min on `/comment` and
  `/bulk-status`) but not surfaced in response headers.

## MCP Tools

The `frontapp-mcp-server` package maps each endpoint to a tool. Mutations use a
two-step confirm pattern: call with `confirm=false` for a preview, then `confirm=true`
to apply (the client elicits explicit user approval).

| Tool                       | Mutation? | Description                               |
| -------------------------- | --------- | ----------------------------------------- |
| `list_orders`              | no        | Filter + paginate orders                  |
| `get_order`                | no        | Full detail for one order                 |
| `lookup_order`             | no        | Find an order by number + customer email  |
| `list_statuses`            | no        | Full status catalog                       |
| `get_viable_statuses`      | no        | Valid transitions for an order            |
| `update_order_status`      | yes       | Change one order's status                 |
| `add_order_comment`        | yes       | Add a history comment                     |
| `update_order_due_date`    | yes       | Set or change the due date                |
| `bulk_update_order_status` | yes       | Change status for up to 50 orders at once |

Plus two resources:

- `frontapp://statuses` — JSON list of every status (cached read).
- `frontapp://help` — tool reference and recommended workflows.

## Resilience (Python client)

Every endpoint inherits these transport-layer behaviors automatically — no decorators or
wrappers needed:

- **Retries**: `httpx-retries` retries idempotent methods on 502/503/504 and any method
  on 429. Configurable via `max_retries`.
- **Rate-limit awareness**: `Retry-After` headers are honored when present; otherwise
  exponential backoff.
- **Auto-pagination**: `GET /orders` is walked to completion using `meta.last_page` as
  the stop condition, up to `max_pages` (default 100) or an explicit `max_items`
  override. Raw-array endpoints (`/statuses`, `/viable-statuses`) are never paginated.
- **Sensitive-data redaction**: Authorization headers and common secret field names
  (`api_key`, `password`, `email`, etc.) are scrubbed from log output.

## Project Structure

```text
frontapp-openapi-client/               # Monorepo root
├── pyproject.toml                      # Workspace configuration (uv)
├── uv.lock                             # Python lock file
├── pnpm-workspace.yaml                 # TS workspace
├── docs/
│   ├── frontapp-openapi.yaml          # OpenAPI 3.1.0 spec (source of truth)
│   └── *.md                            # Shared documentation
├── frontapp_public_api_client/        # Python client
│   ├── frontapp_client.py             # Resilient client + transport layer
│   ├── domain/                         # Hand-written Pydantic domain models
│   ├── helpers/                        # Ergonomic facades (client.orders, .statuses)
│   ├── utils.py                        # unwrap/unwrap_as/unwrap_data + error types
│   ├── api/, models/                   # Generated from the OpenAPI spec
│   └── docs/                           # Package documentation
├── frontapp_mcp_server/                # MCP server
│   └── src/frontapp_mcp/
│       ├── server.py                   # FastMCP server
│       ├── tools/                      # 9 tools (orders + statuses)
│       └── resources/                  # help + statuses resources
└── packages/
    └── frontapp-client/                # TypeScript client
        ├── src/
        │   └── generated/              # Generated from the same spec
        └── openapi-ts.config.ts
```

## Development

### Prerequisites

- **Python 3.12+** for Python packages
- **Node.js 18+** for TypeScript package
- **uv** ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **pnpm** ([install](https://pnpm.io/installation))

### Setup

```bash
git clone https://github.com/dougborg/frontapp-openapi-client.git
cd frontapp-openapi-client

uv sync --all-extras          # install Python deps
uv run pre-commit install     # install git hooks
pnpm install                  # install TS deps
cp .env.example .env          # add FRONTAPP_API_KEY
```

### Common Commands

```bash
uv run poe quick-check        # fast: format + lint
uv run poe check              # full: format + lint + typecheck + test
uv run poe test               # just tests (pytest -n 4)
uv run poe regenerate-client  # regenerate the Python client from docs/frontapp-openapi.yaml
uv run poe generate-pydantic  # regenerate Pydantic v2 models
pnpm --filter frontapp-client generate  # regenerate the TypeScript client
```

### Commit Standards

Conventional commits drive per-package semantic-release versioning:

```bash
git commit -m "feat(client): add helper for archived orders"
git commit -m "fix(client): handle empty viable-status responses"
git commit -m "feat(mcp): add tool for lookup by date range"
git commit -m "feat(ts): export pagination helpers"
git commit -m "docs: update quick-start"
```

Use `!` for breaking changes: `feat(client)!: drop Python 3.11 support`.

See [MONOREPO_SEMANTIC_RELEASE.md](docs/MONOREPO_SEMANTIC_RELEASE.md) for details.

## License

MIT License — see [LICENSE](LICENSE).

## Contributing

Contributions welcome. See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.
