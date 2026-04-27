"""MCP tools for the Frontapp API.

Each tool module exports a ``register_tools(mcp)`` function that registers its
tools on the FastMCP instance. ``register_all_tools`` is the single entry point
called by ``server.py``.
"""

from fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    """Register every tool module with the FastMCP instance."""
    from .analytics import register_tools as register_analytics_tools
    from .attachments import register_tools as register_attachments_tools
    from .contact_groups import register_tools as register_contact_groups_tools
    from .contact_lists import register_tools as register_contact_lists_tools
    from .contacts import register_tools as register_contacts_tools
    from .conversations import register_tools as register_conversations_tools
    from .drafts import register_tools as register_drafts_tools
    from .inboxes import register_tools as register_inboxes_tools
    from .messages import register_tools as register_messages_tools
    from .tags import register_tools as register_tags_tools
    from .teammates import register_tools as register_teammates_tools

    register_analytics_tools(mcp)
    register_attachments_tools(mcp)
    register_contacts_tools(mcp)
    register_contact_lists_tools(mcp)
    register_contact_groups_tools(mcp)
    register_conversations_tools(mcp)
    register_drafts_tools(mcp)
    register_inboxes_tools(mcp)
    register_messages_tools(mcp)
    register_tags_tools(mcp)
    register_teammates_tools(mcp)


__all__ = ["register_all_tools"]
