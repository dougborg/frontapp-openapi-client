"""MCP resources for the Frontapp API.

Resources expose stable, read-only reference data so AI agents can orient
themselves without calling mutating tools.
"""

from __future__ import annotations

from fastmcp import FastMCP


def register_all_resources(mcp: FastMCP) -> None:
    """Register all resources with the FastMCP server."""
    from .help import register_resources as register_help_resources
    from .reference import register_resources as register_reference_resources

    register_help_resources(mcp)
    register_reference_resources(mcp)


__all__ = ["register_all_resources"]
