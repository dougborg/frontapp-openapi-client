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
from collections.abc import Callable
from typing import Any

from fastmcp import Context, FastMCP
from pydantic import BaseModel

from frontapp_mcp.projections import to_summary
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


def _project(model: type[BaseModel], item: Any) -> dict[str, Any]:
    """Validate an attrs model's ``to_dict()`` output through a Pydantic projection."""
    return model.model_validate(item.to_dict()).model_dump(mode="json")


def _dump(items: list[dict[str, Any]]) -> str:
    """Serialize with stable key order so the 60s response-cache hits identical bytes."""
    return json.dumps(items, sort_keys=True)


async def _list_field_results(
    context: Context,
    list_fn: Callable[..., Any],
    model: type[BaseModel],
) -> str:
    """Boilerplate for `field_results`-shaped list endpoints.

    Three of the four reference resources (`tags`, `inboxes`, `teammates`)
    follow the identical shape: call ``list_*.asyncio_detailed``, unwrap
    ``field_results``, project each item through a Pydantic ref model,
    JSON-dump. Pass the ``asyncio_detailed`` function directly, e.g.
    ``_list_field_results(context, list_tags.asyncio_detailed, TagRef)``.
    """
    services = get_services(context)
    response = await list_fn(client=services.client)
    parsed = unwrap(response)
    results = getattr(parsed, "field_results", None) or []
    return _dump([_project(model, item) for item in results])


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

        return await _list_field_results(context, list_tags.asyncio_detailed, TagRef)

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

        return await _list_field_results(
            context, list_inboxes.asyncio_detailed, InboxRef
        )

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

        return await _list_field_results(
            context, list_teammates.asyncio_detailed, TeammateRef
        )

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
        # Goes through the helper (`client.conversations.list`) rather than the
        # raw api module — the helper returns Pydantic domain models, so we
        # share the same ConversationSummary projection used by the conversations
        # tool surface (frontapp_mcp.projections).
        services = get_services(context)
        conversations = await services.client.conversations.list(limit=20)
        return _dump([to_summary(c).model_dump(mode="json") for c in conversations])
