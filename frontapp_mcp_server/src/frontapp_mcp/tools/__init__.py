"""MCP tools for the Frontapp API.

Each tool module exports a ``register_tools(mcp)`` function that registers its
tools on the FastMCP instance. ``register_all_tools`` is the single entry point
called by ``server.py``.
"""

from fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    """Register every tool module with the FastMCP instance."""
    from .contacts import register_tools as register_contacts_tools
    from .conversations import register_tools as register_conversations_tools
    from .drafts import register_tools as register_drafts_tools
    from .inboxes import register_tools as register_inboxes_tools
    from .messages import register_tools as register_messages_tools
    from .tags import register_tools as register_tags_tools
    from .teammates import register_tools as register_teammates_tools

    register_contacts_tools(mcp)
    register_conversations_tools(mcp)
    register_drafts_tools(mcp)
    register_inboxes_tools(mcp)
    register_messages_tools(mcp)
    register_tags_tools(mcp)
    register_teammates_tools(mcp)


__all__ = ["register_all_tools"]
