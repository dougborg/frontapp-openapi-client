"""Frontapp MCP Server.

A Model Context Protocol (MCP) server for the Frontapp API. Exposes order
status lookup and update operations as tools for AI assistants.

Key Features:
- 9 tools across Orders and Statuses
- Two-step confirm pattern on mutations
- Built on frontapp-openapi-client — inherits retries, rate-limit awareness,
  and auto-pagination for free

Example:
    Configure in Claude Desktop's MCP settings:

    ```json
    {
      "mcpServers": {
        "frontapp": {
          "command": "uvx",
          "args": ["frontapp-mcp-server"],
          "env": {
            "FRONTAPP_API_KEY": "your-api-key"
          }
        }
      }
    }
    ```

See https://github.com/dougborg/frontapp-openapi-client for docs.
"""

from importlib.metadata import version

__version__ = version("frontapp-mcp-server")

__all__ = ["__version__"]
