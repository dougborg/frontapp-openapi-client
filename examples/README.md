# Examples

Runnable examples demonstrating the clients live alongside their package documentation
rather than in this directory:

- **Python client** — see recipes in
  [`frontapp_public_api_client/docs/cookbook.md`](../frontapp_public_api_client/docs/cookbook.md).
- **TypeScript client** — see
  [`packages/frontapp-client/docs/cookbook.md`](../packages/frontapp-client/docs/cookbook.md).
- **MCP server** — see
  [`frontapp_mcp_server/docs/examples.md`](../frontapp_mcp_server/docs/examples.md).

## Prerequisites

1. Install dependencies:

   ```bash
   uv sync --all-extras    # Python
   pnpm install            # TypeScript
   ```

1. Provide an API key in one of:
   - `.env`: `FRONTAPP_API_KEY=your_api_key_here`
   - Environment: `export FRONTAPP_API_KEY=your_api_key_here`
   - `~/.netrc`: `machine api2.frontapp.com` + `password your_api_key_here`

## Contributing

When you add a new example, put it in its package's `docs/cookbook.md` (or `examples.md`
for the MCP server) so it stays next to the rest of that package's documentation.
