"""MCP reference resources for workspace lookup data.

These resources let an agent translate human-readable names into Front ids
without burning a tool call. The data is slow-changing and gets a 60s cache
from the existing ``ResponseCachingMiddleware``.

| URI | Purpose |
| --- | --- |
| ``frontapp://tags`` | All workspace tags (id, name, color, privacy). |
| ``frontapp://inboxes`` | All inboxes (id, name, privacy). |
| ``frontapp://teammates`` | All teammates (id, username, email, name, availability). |
| ``frontapp://conversations/recent`` | The 20 most recent conversations as light summaries. |
"""

from __future__ import annotations

import json
from typing import Any

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from frontapp_mcp.services import get_services
from frontapp_public_api_client.utils import unwrap


class TagRef(BaseModel):
    id: str
    name: str | None = None
    highlight: str | None = None
    is_private: bool | None = None


class InboxRef(BaseModel):
    id: str
    name: str | None = None
    is_private: bool | None = None
    is_public: bool | None = None


class TeammateRef(BaseModel):
    id: str
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_available: bool | None = None


class RecentConversationRef(BaseModel):
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


def _project(model: type[BaseModel], item: Any) -> dict[str, Any]:
    """Validate an attrs model's ``to_dict()`` output through a Pydantic projection."""
    return model.model_validate(item.to_dict()).model_dump(mode="json")


def register_resources(mcp: FastMCP) -> None:
    """Register the workspace reference resources."""

    @mcp.resource(
        uri="frontapp://tags",
        name="Tags",
        description=(
            "All workspace tags. Use to translate tag names ('urgent', 'vip') "
            "into ids before passing to update_conversation."
        ),
        mime_type="application/json",
    )
    async def tags_resource(context: Context) -> str:
        from frontapp_public_api_client.api.tags import list_tags

        services = get_services(context)
        response = await list_tags.asyncio_detailed(client=services.client)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return json.dumps([_project(TagRef, t) for t in results])

    @mcp.resource(
        uri="frontapp://inboxes",
        name="Inboxes",
        description=(
            "All inboxes. Use to translate an inbox name ('Support', 'Sales') "
            "into an id before listing or moving conversations."
        ),
        mime_type="application/json",
    )
    async def inboxes_resource(context: Context) -> str:
        from frontapp_public_api_client.api.inboxes import list_inboxes

        services = get_services(context)
        response = await list_inboxes.asyncio_detailed(client=services.client)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return json.dumps([_project(InboxRef, i) for i in results])

    @mcp.resource(
        uri="frontapp://teammates",
        name="Teammates",
        description=(
            "All teammates (human users). Use to translate a teammate name "
            "or email into an id before assigning a conversation."
        ),
        mime_type="application/json",
    )
    async def teammates_resource(context: Context) -> str:
        from frontapp_public_api_client.api.teammates import list_teammates

        services = get_services(context)
        response = await list_teammates.asyncio_detailed(client=services.client)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return json.dumps([_project(TeammateRef, t) for t in results])

    @mcp.resource(
        uri="frontapp://conversations/recent",
        name="Recent conversations",
        description=(
            "The 20 most recent conversations as compact summaries. Use to orient "
            "at the start of a session before drilling into a specific conversation "
            "with get_conversation."
        ),
        mime_type="application/json",
    )
    async def recent_conversations_resource(context: Context) -> str:
        services = get_services(context)
        conversations = await services.client.conversations.list(limit=20)
        return json.dumps(
            [
                RecentConversationRef(
                    id=c.id,
                    subject=c.subject,
                    status=c.status,
                    assignee_name=_format_name(c.assignee) if c.assignee else None,
                    recipient=c.recipient.handle if c.recipient else None,
                    tags=[t.name for t in c.tags if t.name],
                    is_private=c.is_private,
                    created_at=c.created_at.isoformat() if c.created_at else None,
                    updated_at=c.updated_at.isoformat() if c.updated_at else None,
                    waiting_since=(
                        c.waiting_since.isoformat() if c.waiting_since else None
                    ),
                ).model_dump(mode="json")
                for c in conversations
            ]
        )


def _format_name(assignee: Any) -> str | None:
    parts = [
        getattr(assignee, "first_name", None),
        getattr(assignee, "last_name", None),
    ]
    full = " ".join(p for p in parts if p)
    return full or getattr(assignee, "username", None)
