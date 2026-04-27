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
| ``frontapp://me`` | Workspace company identity (id, name) — confirms the token works and which workspace it's bound to. |
| ``frontapp://custom_fields`` | All custom field schemas, grouped by scope (global / account / contact / conversation / inbox / link / teammate). |
| ``frontapp://teams`` | All workspace teams (id, name) — translate team names to ids. |
| ``frontapp://rules`` | All automation rules (read-only) — explain what automation might be firing on a conversation. |
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from fastmcp import Context, FastMCP
from pydantic import BaseModel

from frontapp_mcp.projections import to_summary
from frontapp_mcp.services import get_services
from frontapp_public_api_client.utils import unwrap, unwrap_as


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


class MeRef(BaseModel):
    """Identity of the workspace company the API token is bound to.

    Front's ``GET /me`` returns the company-level identity — id ``cmp_*``
    and the workspace's display name — not the teammate the token
    represents. There's no programmatic way to recover the token's
    teammate from the API; that mapping lives in Front's admin UI.
    Use this resource as a token-validity smoke check at session start
    and to display the workspace name for context.
    """

    id: str
    name: str | None = None


class TeamRef(BaseModel):
    id: str
    name: str | None = None


class CustomFieldRef(BaseModel):
    """Schema for one custom field on Front objects.

    Custom fields are grouped by scope at the top level of the resource
    response (``{"global": [...], "account": [...], ...}``). This model
    represents an individual field entry — there is no per-item ``scope``
    property; the dict key carries that information.
    """

    id: str
    name: str | None = None
    description: str | None = None
    type: str | None = None
    values: list[dict[str, Any]] | None = None


class RuleRef(BaseModel):
    """Compact projection of an automation rule.

    Front exposes rules as read-only via the API — they're created and
    edited in Front's UI. This catalog lets the LLM explain *what
    automation might be firing* on a conversation and avoid stepping on
    rule-driven actions.
    """

    id: str
    name: str | None = None
    actions: list[str] | None = None
    is_private: bool | None = None


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
        uri="frontapp://me",
        name="Workspace identity",
        description=(
            "Workspace company identity — `id` (cmp_*) and display name "
            "of the workspace this API token is bound to. Use as a "
            "session-start smoke test to confirm the token is valid, and "
            "for displaying workspace context. Note: this does NOT identify "
            "the teammate the token represents (Front doesn't expose that)."
        ),
        mime_type="application/json",
    )
    async def me_resource(context: Context) -> str:
        from frontapp_public_api_client.api.token_identity import api_token_details
        from frontapp_public_api_client.models.identity_response import (
            IdentityResponse,
        )

        services = get_services(context)
        response = await api_token_details.asyncio_detailed(client=services.client)
        identity = unwrap_as(response, IdentityResponse)
        return _dump([_project(MeRef, identity)])

    @mcp.resource(
        uri="frontapp://custom_fields",
        name="Custom fields (all scopes)",
        description=(
            "All custom field schemas in the workspace, grouped by scope "
            "(global / account / contact / conversation / inbox / link / "
            "teammate). Use to translate a custom field name into its "
            "`cf_*` id before reading or writing field values on objects."
        ),
        mime_type="application/json",
    )
    async def custom_fields_resource(context: Context) -> str:
        import asyncio

        from frontapp_public_api_client.api.custom_fields import (
            list_account_custom_fields,
            list_contact_custom_fields,
            list_conversation_custom_fields,
            list_custom_fields,
            list_inbox_custom_fields,
            list_link_custom_fields,
            list_teammate_custom_fields,
        )

        services = get_services(context)
        scopes: dict[str, Callable[..., Any]] = {
            "global": list_custom_fields.asyncio_detailed,
            "account": list_account_custom_fields.asyncio_detailed,
            "contact": list_contact_custom_fields.asyncio_detailed,
            "conversation": list_conversation_custom_fields.asyncio_detailed,
            "inbox": list_inbox_custom_fields.asyncio_detailed,
            "link": list_link_custom_fields.asyncio_detailed,
            "teammate": list_teammate_custom_fields.asyncio_detailed,
        }
        # Fan out the 7 list calls concurrently — sequential await would
        # add unnecessary latency on session start (the resource gets
        # consumed at session warm-up, before the first conversation tool).
        responses = await asyncio.gather(
            *(list_fn(client=services.client) for list_fn in scopes.values())
        )
        result: dict[str, list[dict[str, Any]]] = {}
        for scope, response in zip(scopes.keys(), responses, strict=True):
            parsed = unwrap(response)
            results = getattr(parsed, "field_results", None) or []
            result[scope] = [_project(CustomFieldRef, item) for item in results]
        return json.dumps(result, sort_keys=True)

    @mcp.resource(
        uri="frontapp://rules",
        name="Automation rules",
        description=(
            "All automation rules in the workspace (read-only — rules are "
            "created and edited in Front's UI). Use to explain what "
            "automation might be firing on a conversation, or to avoid "
            "stepping on a rule-driven action."
        ),
        mime_type="application/json",
    )
    async def rules_resource(context: Context) -> str:
        from frontapp_public_api_client.api.rules import list_rules

        return await _list_field_results(context, list_rules.asyncio_detailed, RuleRef)

    @mcp.resource(
        uri="frontapp://teams",
        name="Teams",
        description=(
            "All workspace teams (id, name). Use to translate a team name "
            "('Support', 'Sales') into a `tim_*` id before passing to "
            "team-scoped tools like `list_team_inboxes` or "
            "`create_team_signature`."
        ),
        mime_type="application/json",
    )
    async def teams_resource(context: Context) -> str:
        from frontapp_public_api_client.api.teams import list_teams

        return await _list_field_results(context, list_teams.asyncio_detailed, TeamRef)

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
