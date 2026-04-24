# Frontapp — API Client Ecosystem

Multi-language client ecosystem for the
[Front](https://dev.frontapp.com/reference/introduction) customer-communication
platform. Front is a shared-inbox product that unifies email, SMS, chat, and social
channels into one place for support and sales teams. Their
[Core API](https://dev.frontapp.com/reference/introduction) exposes conversations,
messages, contacts, teammates, tags, inboxes, and more.

This monorepo ships:

- A production-grade **Python client** with transport-layer retries, rate-limit
  awareness, and pagination handling for Front's cursor-token paging.
- A **TypeScript client** generated from the same OpenAPI spec via
  [hey-api](https://heyapi.dev).
- An **MCP server** exposing Frontapp operations as tools to AI assistants like Claude
  Desktop and Cursor.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![OpenAPI 3.0.0](https://img.shields.io/badge/OpenAPI-3.0.0-green.svg)](https://spec.openapis.org/oas/v3.0.0)

The OpenAPI spec is vendored from
[frontapp/front-api-specs](https://github.com/frontapp/front-api-specs) and sanitized by
`scripts/vendor_spec.py` (strips binary attachment-download paths and normalizes a few
upstream quirks that trip the generators).

## Packages

| Package                                                | Language   | Version | Description                                                 |
| ------------------------------------------------------ | ---------- | ------- | ----------------------------------------------------------- |
| [frontapp-openapi-client](frontapp_public_api_client/) | Python     | 0.1.0   | API client with transport-layer resilience + domain helpers |
| [frontapp-mcp-server](frontapp_mcp_server/)            | Python     | 0.1.0   | Model Context Protocol server for AI assistants             |
| [frontapp-client](packages/frontapp-client/)           | TypeScript | 0.1.0   | Generated TypeScript/JavaScript client                      |

## Features

| Feature                                        | Python | TypeScript | MCP Server              |
| ---------------------------------------------- | ------ | ---------- | ----------------------- |
| Automatic retries (network + 5xx)              | Yes    | Yes        | Yes (via Python client) |
| Rate-limit retry with exponential backoff      | Yes    | Yes        | Yes                     |
| Cursor-token pagination helpers                | Yes    | Yes        | Yes                     |
| Two-step confirm on mutations (ctx.elicit)     | —      | —          | Yes                     |
| Full type safety (attrs + Pydantic / TS types) | Yes    | Yes        | Yes                     |
| AI tool surface                                | —      | —          | Claude Desktop, Cursor  |

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
        # List recent open conversations tagged "urgent"
        conversations = await client.conversations.list(
            q="status:open tag:urgent", limit=25
        )
        for conv in conversations:
            assignee = conv.assignee.username if conv.assignee else "unassigned"
            print(f"{conv.id}: {conv.subject!r} — {conv.status} ({assignee})")

asyncio.run(main())
```

### TypeScript Client

```bash
npm install frontapp-client
```

```typescript
import { FrontappClient } from "frontapp-client";

const client = await FrontappClient.create();
const { data } = await client.listConversations({ query: { q: "status:open" } });
console.log(`${data._results.length} open conversations`);
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

Get an API key at Front → Settings → Developers → API tokens.

## Configuration

All packages authenticate with a Front API token via bearer auth:

1. **Environment variable**: `FRONTAPP_API_KEY`
2. **`.env` file**: `FRONTAPP_API_KEY=your-key`
3. **Direct parameter**: `FrontappClient(api_key="...")`
4. **`~/.netrc`**: `machine api2.frontapp.com` + `password your-key`

```bash
# .env
FRONTAPP_API_KEY=your-api-key-here
FRONTAPP_BASE_URL=https://api2.frontapp.com  # optional override
```

## API Coverage

The generated clients cover Front's full Core API — **139 paths, 233 operations**
spanning conversations, messages, contacts, teammates, accounts, tags, inboxes,
channels, rules, custom fields, drafts, message templates, analytics, and more. Browse
`frontapp_public_api_client/api/` (Python) or
`packages/frontapp-client/src/generated/sdk.gen.ts` (TS) for the full surface.

Hand-written ergonomic helpers (Python `client.<resource>.…`) and MCP tools wrap the
highest-value subset. Current status:

| Resource                 | Python helper (`client.X.…`) | MCP tools                                                                          |
| ------------------------ | ---------------------------- | ---------------------------------------------------------------------------------- |
| Conversations            | ✅ `.conversations`          | list / get / search / list_messages / list_comments / reply / update / add_comment |
| Contacts                 | ⏳ planned                   | ⏳ planned                                                                         |
| Messages                 | ⏳ planned                   | ⏳ planned                                                                         |
| Tags, Inboxes, Teammates | ⏳ planned                   | ⏳ planned (also as `frontapp://` resources)                                       |
| Analytics                | ⏳ planned                   | ⏳ planned (create→poll recipe)                                                    |

See the [issue tracker](https://github.com/dougborg/frontapp-openapi-client/issues) for
the roadmap. The full generated surface is usable today via
`client.api.<tag>.<operation>` or direct imports from `frontapp_public_api_client.api` —
helpers and MCP tools just add ergonomic polish on top.

### Front Search Syntax

Conversation list/search endpoints accept Front's `q=` search syntax:

| Query               | Description                 |
| ------------------- | --------------------------- |
| `status:open`       | Open conversations          |
| `status:archived`   | Archived                    |
| `tag:urgent`        | Tagged urgent               |
| `assignee:me`       | Assigned to the token owner |
| `is:unassigned`     | Unassigned                  |
| `inbox:support`     | In a named inbox            |
| `after:2024-01-01`  | Updated after a date        |
| `before:2024-12-31` | Updated before a date       |

Combine with `AND` / `OR`: `status:open AND tag:urgent`.

## MCP Tools (conversations vertical)

Mutations use a two-step confirm pattern — call with `confirm=false` for a preview, then
`confirm=true` to apply (which also elicits explicit user approval via `ctx.elicit`).

| Tool                         | Mutation? | Description                                              |
| ---------------------------- | --------- | -------------------------------------------------------- |
| `list_conversations`         | no        | Filter + cursor-paginate, reverse chronological          |
| `get_conversation`           | no        | Full detail for one conversation                         |
| `search_conversations`       | no        | Full Front search syntax as the primary filter           |
| `list_conversation_messages` | no        | Messages inside a conversation (most recent first)       |
| `list_conversation_comments` | no        | Internal teammate comments on a conversation             |
| `reply_to_conversation`      | yes       | Send an outbound reply (uses the conversation's channel) |
| `update_conversation`        | yes       | Archive/reopen, reassign, retag, move inbox              |
| `add_conversation_comment`   | yes       | Add a teammate-only comment (never reaches the customer) |

Reads are cached for 30s via `ResponseCachingMiddleware`.

## Resilience (Python client)

Every endpoint inherits these transport-layer behaviors automatically — no decorators or
wrappers needed:

- **Retries**: `httpx-retries` retries idempotent methods on 502/503/504 and any method
  on 429 (safe because 429 means "not processed"). Configurable via `max_retries`.
- **Rate-limit awareness**: `Retry-After` headers are honored when present; otherwise
  exponential backoff.
- **Sensitive-data redaction**: `Authorization` headers and common secret field names
  (`api_key`, `password`, `token`, etc.) are scrubbed from log output.

Auto-pagination for Front's cursor-token paging is in progress — today, callers pass
`page_token` from `_pagination.next` back to the list endpoint.

## Project Structure

```text
frontapp-openapi-client/               # Monorepo root
├── pyproject.toml                      # uv workspace configuration
├── pnpm-workspace.yaml                 # pnpm TS workspace
├── scripts/vendor_spec.py              # download + sanitize Front's OpenAPI spec
├── docs/
│   ├── frontapp-openapi.yaml           # OpenAPI 3.0.0 spec (vendored + sanitized)
│   ├── FRONTAPP_API_ENDPOINTS.md       # Prioritization reference
│   └── *.md                            # Shared documentation
├── frontapp_public_api_client/         # Python client
│   ├── frontapp_client.py              # Resilient client + transport layer
│   ├── domain/                         # Pydantic domain models (Conversation, …)
│   ├── helpers/                        # Ergonomic facades (client.conversations)
│   ├── api_wrapper/                    # Registry + generic Resource wrapper
│   ├── utils.py                        # unwrap/is_success + error types
│   ├── api/, models/                   # Generated from the OpenAPI spec
│   └── docs/                           # Package documentation
├── frontapp_mcp_server/                # MCP server (FastMCP)
│   └── src/frontapp_mcp/
│       ├── server.py                   # Lifespan, auth, caching middleware
│       ├── tools/                      # MCP tool modules (conversations, …)
│       └── resources/                  # help + workspace-orientation resources
└── packages/
    └── frontapp-client/                # TypeScript client (hey-api)
        ├── src/
        │   ├── client.ts               # createClient + transport stack
        │   ├── transport/              # resilient.ts, pagination.ts
        │   └── generated/              # Generated from the same spec
        └── openapi-ts.config.ts
```

## Development

### Prerequisites

- **Python 3.12+** for Python packages
- **Node.js 18+** for the TypeScript package
- **uv** ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **pnpm** ([install](https://pnpm.io/installation))

### Setup

```bash
git clone https://github.com/dougborg/frontapp-openapi-client.git
cd frontapp-openapi-client

uv sync --extra dev          # install Python deps including dev tools
uv run pre-commit install    # install git hooks
pnpm install                 # install TS deps
cp .env.example .env         # add FRONTAPP_API_KEY
```

### Common Commands

```bash
uv run python scripts/vendor_spec.py      # refresh docs/frontapp-openapi.yaml from upstream
uv run poe regenerate-client              # regenerate the Python client from the spec
pnpm --filter frontapp-client generate    # regenerate the TypeScript client
uv run poe test                           # pytest -n 4
uv run poe quick-check                    # format + lint
uv run poe check                          # format + lint + typecheck + test
```

### Commit Standards

Conventional commits drive per-package semantic-release versioning:

```bash
git commit -m "feat(client): add contacts helper"
git commit -m "fix(client): handle empty paginated response"
git commit -m "feat(mcp): add tools for tag management"
git commit -m "feat(ts): export retry middleware"
git commit -m "docs: update quick-start"
```

Use `!` for breaking changes: `feat(client)!: drop Python 3.11 support`.

See [MONOREPO_SEMANTIC_RELEASE.md](docs/MONOREPO_SEMANTIC_RELEASE.md) for details.

## Acknowledgements

- Scaffolding pattern lifted from
  [dougborg/statuspro-openapi-client](https://github.com/dougborg/statuspro-openapi-client)
  and
  [dougborg/katana-openapi-client](https://github.com/dougborg/katana-openapi-client),
  which established the shape of this ecosystem (Python + TS client + FastMCP server,
  transport-layer resilience, two-step confirm mutations, etc.).
- OpenAPI spec from
  [frontapp/front-api-specs](https://github.com/frontapp/front-api-specs).

## License

MIT License — see [LICENSE](LICENSE).

## Contributing

Contributions welcome. See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.
