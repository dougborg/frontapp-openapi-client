"""MCP tools for the Frontapp API.

Each tool module exports a ``register_tools(mcp)`` function that registers its
tools on the FastMCP instance. ``register_all_tools`` is the single entry point
called by ``server.py``.
"""

from fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    """Register every tool module with the FastMCP instance."""
    # Tool modules will be added here as they are implemented:
    #   from .conversations import register_tools as register_conversations_tools
    #   register_conversations_tools(mcp)
    pass


__all__ = ["register_all_tools"]
