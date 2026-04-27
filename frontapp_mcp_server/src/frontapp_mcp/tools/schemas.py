"""Shared schemas for Frontapp MCP tools.

This module contains Pydantic models and helpers that are shared across multiple
tool modules to ensure consistency and avoid duplication.
"""

from enum import StrEnum
from typing import Any

from fastmcp import Context
from pydantic import BaseModel, Field


class ConfirmationSchema(BaseModel):
    """Schema for user confirmation via elicitation.

    This schema is used with FastMCP's `ctx.elicit()` to request explicit
    user confirmation before executing destructive operations.

    Attributes:
        confirm: Boolean indicating whether the user confirms the action
    """

    confirm: bool = Field(..., description="Confirm the action (true to proceed)")


class ConfirmationResult(StrEnum):
    """Result of a confirmation request."""

    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    DECLINED = "declined"


async def require_confirmation(context: Context, message: str) -> ConfirmationResult:
    """Request user confirmation via elicitation.

    Encapsulates the common elicitation pattern used across all confirm-mode tools.

    Args:
        context: FastMCP context for elicitation
        message: Confirmation message to display

    Returns:
        ConfirmationResult indicating user's decision
    """
    elicit_result = await context.elicit(message, ConfirmationSchema)

    if elicit_result.action != "accept":
        return ConfirmationResult.CANCELLED

    if not elicit_result.data.confirm:
        return ConfirmationResult.DECLINED

    return ConfirmationResult.CONFIRMED


async def confirm_or_preview(
    context: Context,
    *,
    preview: dict[str, Any],
    confirm: bool,
    elicit_message: str,
) -> dict[str, Any] | None:
    """Standard preview-then-elicit gate for mutating MCP tools.

    Encapsulates the preview/confirm/elicit cascade that every two-step-confirm
    tool runs. Returns the response dict the caller should return verbatim
    when the gate blocks execution, or ``None`` when the caller should
    proceed with the mutation.

    Args:
        context: FastMCP context — passed through to ``require_confirmation``.
        preview: The preview dict for the tool's planned action. Surfaced
            on both the preview path (``confirm=False``) and the
            declined-elicitation path so the agent can show the user
            what would have happened.
        confirm: The tool's ``confirm`` parameter. When ``False`` the gate
            short-circuits to the preview response without elicitation.
        elicit_message: Human-readable confirmation prompt for
            ``ctx.elicit`` (e.g. ``"Update conversation cnv_abc?"``).

    Returns:
        ``None`` if the user explicitly confirmed the action — caller proceeds.
        Otherwise a dict with ``confirmed: False`` (and optional
        ``preview`` / ``result`` keys) suitable for returning directly
        from the tool.

    Example:
        >>> preview = {"action": "update", "id": conversation_id}
        >>> gate = await confirm_or_preview(
        ...     context,
        ...     preview=preview,
        ...     confirm=confirm,
        ...     elicit_message=f"Update conversation {conversation_id}?",
        ... )
        >>> if gate is not None:
        ...     return gate
        >>> # ... proceed with mutation
    """
    if not confirm:
        return {"preview": preview, "confirmed": False}

    result = await require_confirmation(context, elicit_message)
    if result is not ConfirmationResult.CONFIRMED:
        return {"preview": preview, "confirmed": False, "result": result.value}

    return None


__all__ = [
    "ConfirmationResult",
    "ConfirmationSchema",
    "confirm_or_preview",
    "require_confirmation",
]
