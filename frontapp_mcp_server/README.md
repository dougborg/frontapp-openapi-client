# Frontapp MCP Server

Model Context Protocol (MCP) server for [Front](https://dev.frontapp.com), the
shared-inbox customer-communication platform. Exposes Front operations as tools so AI
assistants (Claude Desktop, Claude.ai, Cursor, etc.) can read and act on conversations,
messages, contacts, and more through natural language.

Built on top of [`frontapp-openapi-client`](../frontapp_public_api_client), which wraps
Front's Core API (233 operations) with transport-layer retries, rate-limit awareness,
and cursor pagination.

## Features

- **Conversations vertical live today** — 8 tools: list / get / search / list_messages /
  list_comments / reply / update / add_comment. More verticals (contacts, messages,
  tags, inboxes, analytics) are tracked as GitHub issues.
- **Two-step confirmation**: mutations are gated behind `confirm=false` (preview only) →
  `confirm=true` (execute). The agent must surface the preview to the user before
  re-invoking with `confirm=true`.
- **Built-in resilience**: automatic retries, 429 rate-limit handling with exponential
  backoff, and cursor-paginated list helpers inherited from the
  `frontapp-openapi-client` transport layer.
- **Environment-based authentication**: Front API token via `FRONTAPP_API_KEY` (env var,
  `.env`, or `~/.netrc`).
- **Response caching** for read-only tools (30s TTL) via FastMCP's response caching
  middleware.
- **Structured logging** with sensitive-data redaction.

## Installation

```bash
pip install frontapp-mcp-server
```

## Quick Start

### 1. Get your Front API token

Create a developer token at **Front → Settings → Developers → API tokens**. Any personal
or team token with the scopes you need will work.

### 2. Configure environment

```bash
export FRONTAPP_API_KEY=your-api-key-here
```

Or create a `.env`:

```
FRONTAPP_API_KEY=your-api-key-here
FRONTAPP_BASE_URL=https://api2.frontapp.com  # optional override
```

### 3. Choose a transport

| Transport         | Use case                    | Command                                           |
| ----------------- | --------------------------- | ------------------------------------------------- |
| `stdio` (default) | Claude Desktop, Claude Code | `frontapp-mcp-server`                             |
| `streamable-http` | Claude.ai, remote clients   | `frontapp-mcp-server --transport streamable-http` |
| `sse`             | Cursor IDE                  | `frontapp-mcp-server --transport sse`             |
| `http`            | Generic HTTP clients        | `frontapp-mcp-server --transport http`            |

### 4. Use with Claude Desktop (stdio)

**Recommended: install the `.mcpb` bundle** — Claude Desktop has built-in support for
[MCP Bundles](https://github.com/anthropics/mcpb), which install local MCP servers in
one click and prompt for the API key via UI (no JSON editing).

1. Download `frontapp-mcp-server-<version>.mcpb` from the
   [latest GitHub release](https://github.com/dougborg/frontapp-openapi-client/releases?q=mcp-v).
1. Drag the `.mcpb` file into Claude Desktop, or open it from the Finder.
1. Confirm install in the dialog. Claude Desktop prompts for your Frontapp API key
   (stored securely; never written to a config file by hand).

The bundle ships the server source plus a manifest that declares the runtime
requirements; UV handles dep resolution on first launch.

**Manual `uvx` install (fallback)** — if you'd rather edit
`~/Library/Application Support/Claude/claude_desktop_config.json` directly:

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

Either path: restart Claude Desktop and the Frontapp tools will appear.

> **Running off a local checkout (dev mode)?** The package isn't on PyPI yet (issue
> #10), and both the `.mcpb` bundle and `uvx` resolve from PyPI. To dogfood from a local
> clone, see [MCP_CLAUDE_DESKTOP_DEV.md](MCP_CLAUDE_DESKTOP_DEV.md) — it covers the
> `uv run --directory <repo>` config + `.env` setup.

### 5. Use with Claude.ai (streamable-http)

Claude.ai requires **HTTPS** and a **publicly reachable URL**. For local development,
use a tunnel like [ngrok](https://ngrok.com):

```bash
# Terminal 1: Start the MCP server with hot-reload
uv run poe dev

# Terminal 2: Create an HTTPS tunnel
ngrok http 8765
# → gives you https://abc123.ngrok-free.app
```

Then in Claude.ai:

1. Go to **Customize > Connectors**
1. Select **"Add custom connector"**
1. Paste your ngrok HTTPS URL

For production, run the Docker image behind a reverse proxy with TLS:

```bash
docker run -p 8765:8765 \
  -e FRONTAPP_API_KEY=your-key \
  ghcr.io/dougborg/frontapp-mcp-server:latest
```

### 6. Run standalone (optional)

```bash
export FRONTAPP_API_KEY=your-api-key
frontapp-mcp-server
```

## Tools (conversations vertical)

Mutations use a two-step confirm pattern: call with `confirm=false` first to get a
preview, then `confirm=true` to execute.

### Conversations

| Tool                         | Mutation? | Endpoint                            | Purpose                                                 |
| ---------------------------- | --------- | ----------------------------------- | ------------------------------------------------------- |
| `list_conversations`         | no        | `GET /conversations`                | Cursor-paginated list; supports Front `q=` syntax       |
| `get_conversation`           | no        | `GET /conversations/{id}`           | Full detail for one conversation                        |
| `search_conversations`       | no        | `GET /conversations/search/{query}` | Front search syntax as the primary filter               |
| `list_conversation_messages` | no        | `GET /conversations/{id}/messages`  | Messages inside a conversation                          |
| `list_conversation_comments` | no        | `GET /conversations/{id}/comments`  | Internal teammate comments                              |
| `update_conversation`        | yes       | `PATCH /conversations/{id}`         | Archive/reopen, reassign, retag, move inbox             |
| `add_conversation_comment`   | yes       | `POST /conversations/{id}/comments` | Internal note (teammates only — never reaches customer) |

### Drafts (drafts-first outbound)

There is no direct "send a reply" tool — outbound replies always go through drafts.
Agents draft, humans review and click send in Front's UI.

| Tool                       | Mutation? | Endpoint                             | Purpose                                          |
| -------------------------- | --------- | ------------------------------------ | ------------------------------------------------ |
| `list_conversation_drafts` | no        | `GET /conversations/{id}/drafts`     | Existing drafts on a conversation                |
| `create_draft_on_channel`  | yes       | `POST /channels/{channel_id}/drafts` | New outbound draft on a channel                  |
| `create_draft_reply`       | yes       | `POST /conversations/{id}/drafts`    | Draft a reply on an existing conversation        |
| `edit_draft`               | yes       | `PATCH /drafts/{id}/`                | Full-replacement edit (body + channel_id needed) |
| `delete_draft`             | yes       | `DELETE /drafts/{id}`                | Discard a draft                                  |

More verticals (contacts, tags, inboxes, teammates, messages, analytics) are tracked as
open issues on the repo.

### Example: find, read, and draft a reply to a conversation

```
list_conversations(q="status:open tag:urgent", limit=10)
  → [{id: cnv_abc, subject: "Order #1234 still missing", …}, …]

list_conversation_messages(conversation_id="cnv_abc")
  → [{body: "Hi, my order hasn't arrived…", author: …}, …]

create_draft_reply(
  conversation_id="cnv_abc",
  body="Thanks for reaching out — we're tracking it down now.",
  channel_id="cha_xyz",
  confirm=False
)
  → Preview: draft reply on cnv_abc (body previewed, no draft created)
  → ...confirm=true to create the draft

# The human reviews the draft in Front and clicks send. There is no
# programmatic send_draft.
```

### Front search syntax

The `q=` parameter accepts Front's query DSL:

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

## Resources

Resources expose stable, read-only reference data so AI agents can orient themselves
without calling mutating tools.

- `frontapp://help` — tool reference and recommended workflows (Markdown).

Additional workspace-orientation resources (`frontapp://tags`, `frontapp://inboxes`,
`frontapp://teammates`, `frontapp://conversations/recent`) are planned — see the repo
issue tracker.

## Configuration

### Environment variables

- `FRONTAPP_API_KEY` (required) — your bearer token.
- `FRONTAPP_BASE_URL` (optional) — defaults to `https://api2.frontapp.com`.
- `FRONTAPP_MCP_LOG_LEVEL` (optional) — `DEBUG` / `INFO` / `WARNING` / `ERROR` (default
  `INFO`).
- `FRONTAPP_MCP_LOG_FORMAT` (optional) — `json` or `text` (default `json`).

### Endpoint authentication (HTTP transport)

When running over `http`, `sse`, or `streamable-http`, the MCP endpoint is
**unauthenticated by default**. Pick one of:

**Bearer token** (simple, for dev/personal use):

```bash
export MCP_AUTH_TOKEN=your-secret-token
```

Clients must send `Authorization: Bearer your-secret-token`. In Claude.ai, enter the
token in the connector's Advanced Settings.

**GitHub OAuth** (production):

```bash
export MCP_GITHUB_CLIENT_ID=your-github-client-id
export MCP_GITHUB_CLIENT_SECRET=your-github-client-secret
export MCP_BASE_URL=https://your-public-url.ngrok-free.app
```

Create a GitHub OAuth App at https://github.com/settings/developers with the callback
URL set to `<MCP_BASE_URL>/auth/callback`.

Auth is **not required** for stdio transport (local only).

### Logging

```bash
# Development
export FRONTAPP_MCP_LOG_LEVEL=DEBUG
export FRONTAPP_MCP_LOG_FORMAT=text
frontapp-mcp-server

# Production
export FRONTAPP_MCP_LOG_LEVEL=INFO
export FRONTAPP_MCP_LOG_FORMAT=json
frontapp-mcp-server
```

## Troubleshooting

### "FRONTAPP_API_KEY environment variable is required"

Set the variable or add it to `.env`:

```bash
export FRONTAPP_API_KEY=your-api-key-here
```

### 401 Unauthorized

Your API token is invalid or expired. Rotate it at Front → Settings → Developers → API
tokens.

### Tools not showing in Claude Desktop

1. Check `~/Library/Logs/Claude/mcp*.log`.
1. Verify the config file is valid JSON.
1. Test standalone: `frontapp-mcp-server` (should start with no errors).
1. Restart Claude Desktop.

### Persistent 429 rate limiting

The client retries 429s with exponential backoff automatically. Front enforces
per-endpoint rate limits; check Front's API reference for your plan's specific caps. If
you hit persistent rate limits, reduce request frequency or batch reads through larger
`limit=` pages.

## Development

### Prerequisites

- **uv** package manager
  ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **Python 3.12+**

### Install from source

```bash
git clone https://github.com/dougborg/frontapp-openapi-client.git
cd frontapp-openapi-client/frontapp_mcp_server
uv sync
```

### Run tests

```bash
# Unit tests only (no API key needed)
uv run pytest tests/ -m "not integration"

# All tests (requires FRONTAPP_API_KEY)
export FRONTAPP_API_KEY=your-key
uv run pytest tests/
```

### Hot-reload development

```bash
# Install mcp-hmr (requires Python 3.12+)
uv pip install mcp-hmr

# Run with hot reload
uv run mcp-hmr src/frontapp_mcp/server.py:mcp
```

Claude Desktop config for development:

```json
{
  "mcpServers": {
    "frontapp-dev": {
      "command": "/Users/YOUR_USERNAME/.local/bin/uv",
      "args": ["run", "mcp-hmr", "src/frontapp_mcp/server.py:mcp"],
      "cwd": "/absolute/path/to/frontapp-openapi-client/frontapp_mcp_server",
      "env": {
        "FRONTAPP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Build and install locally

```bash
uv build
pipx install --force dist/frontapp_mcp_server-*.whl
```

## Links

- **Repo**: https://github.com/dougborg/frontapp-openapi-client
- **Issues**: https://github.com/dougborg/frontapp-openapi-client/issues
- **PyPI**: https://pypi.org/project/frontapp-mcp-server/
- **Frontapp API docs**: https://api2.frontapp.com

## License

MIT License — see [LICENSE](../LICENSE).
