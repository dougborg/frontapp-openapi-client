"""MCP tools for Frontapp messages.

Three tools for operating on individual messages by ``msg_*`` id outside the
context of a parent conversation — useful when an agent receives a message
id from a webhook, audit log, or external system.

- 2 reads (cached 30s): ``get_message`` / ``get_message_seen_status``
- 1 mutation (two-step confirm): ``mark_message_seen``

Outbound replies do **not** live here — use the drafts vertical
(``create_draft_reply``) or the conversations vertical's reply flow.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import (
    DESTRUCTIVE,
    confirm_or_preview,
)
from frontapp_public_api_client.domain.converters import unwrap_unset
from frontapp_public_api_client.models.message_response import MessageResponse
from frontapp_public_api_client.models.seen_receipt_response import SeenReceiptResponse


def _enum_value(field: Any) -> str | None:
    """Return ``.value`` of an attrs StrEnum field, or ``None`` if UNSET."""
    resolved = unwrap_unset(field, None)
    return resolved.value if resolved is not None else None


def _author_name(author: Any) -> str | None:
    """Render a teammate as ``"First Last"``, falling back to username."""
    if author is None:
        return None
    first = unwrap_unset(author.first_name, "")
    last = unwrap_unset(author.last_name, "")
    full = f"{first} {last}".strip()
    return full or unwrap_unset(author.username, None)


def _message_summary(message: MessageResponse) -> dict[str, Any]:
    """Compact dict projection of a generated ``MessageResponse``."""
    recipients = unwrap_unset(message.recipients, [])
    attachments = unwrap_unset(message.attachments, [])
    return {
        "id": unwrap_unset(message.id, None),
        "message_uid": unwrap_unset(message.message_uid, None),
        "type": _enum_value(message.type_),
        "is_inbound": unwrap_unset(message.is_inbound, None),
        "draft_mode": _enum_value(message.draft_mode),
        "error_type": unwrap_unset(message.error_type, None),
        "version": unwrap_unset(message.version, None),
        "created_at": unwrap_unset(message.created_at, None),
        "subject": unwrap_unset(message.subject, None),
        "blurb": unwrap_unset(message.blurb, None),
        "author_name": _author_name(unwrap_unset(message.author, None)),
        "recipients": [{"handle": r.handle, "role": r.role.value} for r in recipients],
        "text": unwrap_unset(message.text, None),
        "body": unwrap_unset(message.body, None),
        "attachment_filenames": [unwrap_unset(a.filename, None) for a in attachments],
    }


def _seen_receipt_summary(receipt: SeenReceiptResponse) -> dict[str, Any]:
    """Project a ``SeenReceiptResponse`` to a flat dict.

    ``first_seen_at`` is an ISO string (Front returns a formatted timestamp
    here, not a unix epoch like on most other resources).
    """
    return {
        "first_seen_at": receipt.first_seen_at,
        "seen_by": {
            "handle": receipt.seen_by.handle,
            "source": receipt.seen_by.source.value,
        },
    }


def register_tools(mcp: FastMCP) -> None:
    """Register message-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="get_message",
        description=(
            "Fetch one message by id (e.g. 'msg_abc'). Returns a compact "
            "dict — id, type, direction, subject, body, recipients, "
            "timestamps. Use list_conversation_messages first if you "
            "have a conversation id and want to browse."
        ),
    )
    async def get_message(
        context: Context,
        message_id: Annotated[str, Field(description="Message id, e.g. 'msg_abc'")],
    ) -> dict[str, Any]:
        services = get_services(context)
        message = await services.client.messages.get(message_id)
        return _message_summary(message)

    @mcp.tool(
        name="get_message_seen_status",
        description=(
            "List seen receipts for an outbound message. Returns 0..n "
            "receipts; each carries first_seen_at (ISO string) and the "
            "seen_by handle. Empty list when no receipts are available."
        ),
    )
    async def get_message_seen_status(
        context: Context,
        message_id: Annotated[str, Field(description="Message id, e.g. 'msg_abc'")],
    ) -> list[dict[str, Any]]:
        services = get_services(context)
        receipts = await services.client.messages.seen_status(message_id)
        return [_seen_receipt_summary(r) for r in receipts]

    # -- mutations (two-step confirm) ---------------------------------------

    @mcp.tool(
        name="mark_message_seen",
        description=(
            "Acknowledge that a message has been seen. RATE LIMITED: 10 "
            "requests per message per hour — Front intends this as a "
            "response to an actual end-user view, not a backfill job. "
            "Optional teammate_id attributes the seen event to a "
            "specific 'tea_*' teammate. Two-step confirm."
        ),
        annotations=DESTRUCTIVE,
    )
    async def mark_message_seen(
        context: Context,
        message_id: Annotated[str, Field(description="Message id, e.g. 'msg_abc'")],
        teammate_id: Annotated[
            str | None,
            Field(description="Optional teammate id ('tea_*') to attribute the seen"),
        ] = None,
        confirm: Annotated[
            bool, Field(description="Must be true to mark seen")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "mark_message_seen",
            "message_id": message_id,
            "teammate_id": teammate_id,
            "rate_limit": "10 req/msg/hour",
        }
        prompt = f"Mark message {message_id} seen"
        if teammate_id:
            prompt += f" as teammate {teammate_id}"
        prompt += "?"
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        success = await services.client.messages.mark_seen(
            message_id, teammate_id=teammate_id
        )
        return {"confirmed": True, "marked_seen": success}


__all__ = ["register_tools"]
