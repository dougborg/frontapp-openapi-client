# Run the Frontapp MCP server in Claude Desktop — dev mode

This doc covers running the MCP server **directly off your local checkout** of
`frontapp-openapi-client`, so your edits are picked up immediately without
rebuild/republish. Use this for dogfooding new tools and verticals before they ship to
PyPI.

For the production install path (`uvx frontapp-mcp-server` from PyPI), see the Claude
Desktop section in [README.md](README.md). The package isn't on PyPI yet (issue #10), so
dev mode is currently the only option.

For Cursor IDE, see [MCP_CURSOR_SETUP.md](MCP_CURSOR_SETUP.md).

## Prerequisites

- Claude Desktop installed (macOS, Windows, or Linux)
- This repo checked out somewhere — paths in this doc assume
  `/Users/<you>/Projects/frontapp-openapi-client`; substitute your actual path.
- `uv` on PATH (or you know its absolute path — `which uv`).
- Your Front API token. Generate one in Front's UI: **Settings → Developers → API
  Tokens**. The token needs the scopes for whatever tools you plan to use — for full
  coverage, grant all read/write scopes.

## 1. Set up the API token

Create a `.env` file at the repo root:

```bash
cd /Users/<you>/Projects/frontapp-openapi-client
cp .env.example .env
```

Edit `.env` and replace `your_api_key_here` with your Front token. The MCP server's
`lifespan` calls `load_dotenv()` at startup, so any process launched with this repo as
its cwd picks up the key.

> **Why .env, not the Claude Desktop config?** Embedding the API token in
> `claude_desktop_config.json` works but spreads it across additional files that may be
> backed up or sync'd. Keeping the token in `.env` (which is gitignored) keeps the
> secret in one place.

## 2. Sync dependencies

```bash
uv sync --all-extras
```

This installs the project's deps and the editable `frontapp-mcp-server` console script
into `.venv/`.

## 3. Sanity-check the server runs locally

```bash
uv run python -m frontapp_mcp
```

Expected output: a FastMCP banner + structured logs ending with `server_ready`. The
process blocks on stdin (waiting for an MCP client) — kill it with **Ctrl-C**.

If you see `authentication_failed: FRONTAPP_API_KEY environment variable is required`,
your `.env` file isn't being picked up — verify the file is at the repo root and
contains `FRONTAPP_API_KEY=fk_...`.

## 4. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) — Windows
uses `%APPDATA%\Claude\claude_desktop_config.json`, Linux uses
`~/.config/Claude/claude_desktop_config.json`.

Add an `mcpServers` entry pointing at this checkout:

```json
{
  "mcpServers": {
    "frontapp-dev": {
      "command": "/Users/<you>/.nix-profile/bin/uv",
      "args": [
        "run",
        "--directory",
        "/Users/<you>/Projects/frontapp-openapi-client",
        "python",
        "-m",
        "frontapp_mcp"
      ]
    }
  }
}
```

Substitute the absolute path to `uv` (run `which uv` to find it) and your repo path.
**Use absolute paths** — Claude Desktop's launch environment doesn't include the same
`PATH` as your shell.

If the file already has other top-level keys (e.g. `preferences`), add `mcpServers` as a
sibling — don't replace the existing JSON. Example combined shape:

```json
{
  "preferences": {
    "...": "..."
  },
  "mcpServers": {
    "frontapp-dev": {
      "command": "/Users/<you>/.nix-profile/bin/uv",
      "args": [
        "run",
        "--directory",
        "/Users/<you>/Projects/frontapp-openapi-client",
        "python",
        "-m",
        "frontapp_mcp"
      ]
    }
  }
}
```

### Why `uv run --directory ...`

- `--directory` makes uv treat that path as the project root (resolves
  `pyproject.toml` + `.venv`) **and** sets it as the process's working directory (so
  `load_dotenv()` finds `.env` at that path).
- Auto-syncs deps on launch, so a fresh `git pull` is reflected the next time you
  restart Claude Desktop without an extra step.
- Mirrors how every other repo task runs (`uv run poe …`).

## 5. Restart Claude Desktop

Quit + relaunch (a window reload isn't enough — the server is started at app launch).
Open a new chat and look for the tool-icon (`🛠`) near the input — clicking it should
show the registered Frontapp tools (around 100 of them across conversations / drafts /
contacts / messages / tags / inboxes / teammates / contact_lists / contact_groups /
attachments / analytics / knowledge_bases / teams / applications).

Reference resources show up under the resource-icon (`📎` or similar depending on Claude
Desktop version): `frontapp://help`, `frontapp://me`, `frontapp://tags`,
`frontapp://inboxes`, `frontapp://teammates`, `frontapp://teams`,
`frontapp://custom_fields`, `frontapp://rules`, `frontapp://conversations/recent`.

## Smoke test

In Claude Desktop, ask:

> Read `frontapp://me` and `frontapp://tags`, then list my 5 most recent conversations.

Expected:

1. Reads the workspace identity (your `cmp_*` id and workspace name).
2. Reads the tag catalog.
3. Calls `list_conversations(limit=5)` and returns a summary of each.

If the workspace name doesn't match what you see in Front's UI, the token is bound to a
different workspace than you expected — verify the token in **Front Settings →
Developers → API Tokens**.

## Iterating

After editing source:

- For pure code changes, restart Claude Desktop. The next launch re-runs `uv run`, which
  picks up your edits.
- For dependency changes (`pyproject.toml`), `uv sync --all-extras` first, then restart
  Claude Desktop.

## Logs

Claude Desktop captures the MCP server's stderr at:

- macOS: `~/Library/Logs/Claude/mcp-server-frontapp-dev.log`
- Windows: `%APPDATA%\Claude\Logs\mcp-server-frontapp-dev.log`
- Linux: `~/.config/Claude/logs/mcp-server-frontapp-dev.log`

The file name matches the key you used under `mcpServers`. Tail it when debugging:

```bash
tail -f "$HOME/Library/Logs/Claude/mcp-server-frontapp-dev.log"
```

The MCP server logs in JSON. Useful events to grep for: `server_starting`,
`client_initialized`, `tool_invoked`, `tool_failed`, `authentication_failed`.

## Troubleshooting

### Tools don't appear after restart

1. Check the log file (above). If you see `authentication_failed`, `.env` isn't being
   picked up — verify the path with
   `ls /Users/<you>/Projects/frontapp-openapi-client/.env`.
2. Look for `command not found` or `ENOENT` in the log — your `uv` path is wrong.
   `which uv` and update the config.
3. Check `claude_desktop_config.json` parses as valid JSON
   (`jq . < ~/Library/Application\ Support/Claude/claude_desktop_config.json`).

### Tools appear but every call fails

1. Tail the log (above). Most failures are auth-related — `401 Unauthorized` means the
   token is invalid or revoked.
2. Run the server locally with the same env to reproduce:

   ```bash
   cd /Users/<you>/Projects/frontapp-openapi-client
   uv run python -m frontapp_mcp
   ```

   Then in another terminal, smoke-test against Front's API directly:

   ```bash
   uv run python -c "
   import asyncio
   from frontapp_public_api_client import FrontappClient
   async def main():
       async with FrontappClient() as c:
           convs = await c.conversations.list(limit=1)
           print(convs)
   asyncio.run(main())
   "
   ```

   If that works, the issue is in the MCP wrapper, not the API token. If it fails with
   the same error, fix the token first.

### Server crashes on startup

1. `tail` the log file — Python tracebacks usually point at the issue.
2. Run `uv run poe full-check` from the repo root to confirm the codebase is internally
   consistent.
3. If `pyproject.toml` was recently changed (a dep got bumped), `uv sync --all-extras`
   to update `.venv`.

### "Drafts only" — agent created a draft, where do I send it?

Drafts are not auto-sent. Open Front's web UI; the draft appears in the conversation.
Review it, edit if needed, and click **Send**. This is by design (ADR-0016 →
"Drafts-first outbound") — there is no programmatic `send_draft` tool. The same applies
to KB articles: `create_kb_article` always creates drafts; you publish them in Front's
UI.

## See also

- [README.md](README.md) — production install path + tool reference
- [MCP_CURSOR_SETUP.md](MCP_CURSOR_SETUP.md) — Cursor IDE setup
- [docs/LOGGING.md](docs/LOGGING.md) — log format + observability
- Project ADRs in
  [`frontapp_public_api_client/docs/adr/`](../frontapp_public_api_client/docs/adr/)
