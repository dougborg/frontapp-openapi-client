"""Shared schemas and annotations for Frontapp MCP tools.

This module contains helpers shared across multiple tool modules to ensure
consistency and avoid duplication.
"""

from typing import Any

from mcp.types import ToolAnnotations

# Canonical destructive-mutation annotation. Apply to every @mcp.tool decorator
# that takes a `confirm:` parameter so spec-compliant clients prompt the user
# natively before invoking. This is the client-side complement to the in-band
# two-call gate enforced by `confirm_or_preview` — see ADR-0016.
DESTRUCTIVE = ToolAnnotations(destructiveHint=True)


def confirm_or_preview(
    *,
    preview: dict[str, Any],
    confirm: bool,
) -> dict[str, Any] | None:
    """Standard preview-then-execute gate for mutating MCP tools.

    Returns the response dict the caller should return verbatim on the
    preview path (``confirm=False``), or ``None`` when the caller should
    proceed with the mutation (``confirm=True``).

    The contract is **two-call**: the LLM first invokes the tool with
    ``confirm=False`` to get the preview, surfaces it to the user, and
    only re-invokes with ``confirm=True`` after the user agrees. Mutation
    tools should also carry the MCP ``destructiveHint`` annotation
    (via ``DESTRUCTIVE`` in this module) so spec-compliant clients
    prompt natively.

    Why no server-side elicitation: ``ctx.elicit`` is unreliable across
    MCP clients (notably broken in Claude Desktop). Per the MCP Tools
    spec, clients SHOULD prompt; servers SHOULD NOT.

    Args:
        preview: The preview dict for the tool's planned action. Returned
            on the preview path so the agent can show the user what would
            have happened.
        confirm: The tool's ``confirm`` parameter. ``False`` short-circuits
            to the preview response.

    Returns:
        ``None`` when ``confirm=True`` — caller proceeds with the mutation.
        Otherwise a dict with ``preview`` and ``confirmed: False`` suitable
        for returning directly from the tool.

    Example:
        >>> preview = {"action": "update", "id": conversation_id}
        >>> gate = confirm_or_preview(preview=preview, confirm=confirm)
        >>> if gate is not None:
        ...     return gate
        >>> # ... proceed with mutation
    """
    if not confirm:
        return {"preview": preview, "confirmed": False}
    return None


__all__ = ["DESTRUCTIVE", "confirm_or_preview"]
