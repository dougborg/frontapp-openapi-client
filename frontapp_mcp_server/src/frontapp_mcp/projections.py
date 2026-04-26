"""Shared response projections used by MCP tools and resources.

When a tool returns a list of conversations and a reference resource also
exposes recent conversations, both paths want the same compact, LLM-friendly
shape. Defining the projection here lets the two surfaces share the schema
without one importing private symbols from the other.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from frontapp_public_api_client.domain import Conversation


class ConversationSummary(BaseModel):
    """Compact projection of a conversation for LLM responses.

    The full ``Conversation`` domain model carries more structure than is
    useful to an LLM on every list hit. Callers can still call
    ``get_conversation`` for full detail on a specific id.
    """

    id: str
    subject: str | None = None
    status: str | None = None
    assignee_name: str | None = None
    recipient: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_private: bool | None = None
    created_at: str | None = None
    updated_at: str | None = None
    waiting_since: str | None = None


def to_summary(conv: Conversation) -> ConversationSummary:
    """Project a ``Conversation`` domain model to a ``ConversationSummary``."""
    assignee_name: str | None = None
    if conv.assignee:
        parts = [conv.assignee.first_name, conv.assignee.last_name]
        assignee_name = " ".join(p for p in parts if p) or conv.assignee.username
    return ConversationSummary(
        id=conv.id,
        subject=conv.subject,
        status=conv.status,
        assignee_name=assignee_name,
        recipient=conv.recipient.handle if conv.recipient else None,
        tags=[t.name for t in conv.tags if t.name],
        is_private=conv.is_private,
        created_at=conv.created_at.isoformat() if conv.created_at else None,
        updated_at=conv.updated_at.isoformat() if conv.updated_at else None,
        waiting_since=conv.waiting_since.isoformat() if conv.waiting_since else None,
    )


__all__ = ["ConversationSummary", "to_summary"]
