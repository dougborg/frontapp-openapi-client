"""MCP tools for Frontapp inbox management.

Covers the workspace inbox catalog (``/inboxes*``).

- 7 reads (cached 30s): list / list_team / list_teammate_private / get /
  list_inbox_conversations / list_inbox_channels / list_inbox_access
- 4 mutations (two-step confirm): create_inbox / create_team_inbox /
  grant_inbox_access / revoke_inbox_access

Front exposes no general inbox PATCH — name and visibility are immutable
post-creation. The only post-create mutations are the access
grant/revoke pair, which take a list of teammate ids and the preview
includes the count + ids so the user can review.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.projections import (
    ConversationSummary,
    InboxSummary,
    to_inbox_summary,
    to_summary,
)
from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import confirm_or_preview


def register_tools(mcp: FastMCP) -> None:
    """Register inbox-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="list_inboxes",
        description=(
            "List every inbox visible to the API token. Prefer the "
            "`frontapp://inboxes` resource for name-to-id lookups; this "
            "tool is for programmatic listing."
        ),
    )
    async def list_inboxes(context: Context) -> list[InboxSummary]:
        services = get_services(context)
        inboxes = await services.client.inboxes.list()
        return [to_inbox_summary(i) for i in inboxes]

    @mcp.tool(
        name="list_team_inboxes",
        description="List inboxes owned by a team (`team_id` like 'tim_abc').",
    )
    async def list_team_inboxes(
        context: Context,
        team_id: Annotated[str, Field(description="Team id, e.g. 'tim_abc'")],
    ) -> list[InboxSummary]:
        services = get_services(context)
        inboxes = await services.client.inboxes.list_for_team(team_id)
        return [to_inbox_summary(i) for i in inboxes]

    @mcp.tool(
        name="list_teammate_private_inboxes",
        description="List a teammate's private inboxes (`teammate_id` like 'tea_abc').",
    )
    async def list_teammate_private_inboxes(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id, e.g. 'tea_abc'")],
    ) -> list[InboxSummary]:
        services = get_services(context)
        inboxes = await services.client.inboxes.list_private_for_teammate(teammate_id)
        return [to_inbox_summary(i) for i in inboxes]

    @mcp.tool(
        name="get_inbox",
        description="Fetch full details for one inbox by id (e.g. 'inb_abc').",
    )
    async def get_inbox(
        context: Context,
        inbox_id: Annotated[str, Field(description="Inbox id, e.g. 'inb_abc'")],
    ) -> InboxSummary:
        services = get_services(context)
        inbox = await services.client.inboxes.get(inbox_id)
        return to_inbox_summary(inbox)

    @mcp.tool(
        name="list_inbox_conversations",
        description=(
            "List conversations in this inbox. Pass `q=` to filter with "
            "Front search syntax."
        ),
    )
    async def list_inbox_conversations(
        context: Context,
        inbox_id: Annotated[str, Field(description="Inbox id")],
        q: Annotated[str | None, Field(description="Front search syntax")] = None,
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[ConversationSummary]:
        from frontapp_public_api_client.domain import Conversation

        services = get_services(context)
        items = await services.client.inboxes.list_conversations(
            inbox_id, q=q, limit=limit, page_token=page_token
        )
        return [
            to_summary(Conversation.model_validate(item.to_dict())) for item in items
        ]

    @mcp.tool(
        name="list_inbox_channels",
        description="List channels routing into this inbox. Returns raw dicts.",
    )
    async def list_inbox_channels(
        context: Context,
        inbox_id: Annotated[str, Field(description="Inbox id")],
    ) -> list[dict[str, Any]]:
        services = get_services(context)
        channels = await services.client.inboxes.list_channels(inbox_id)
        return [c.to_dict() for c in channels]

    @mcp.tool(
        name="list_inbox_access",
        description="List teammates with access to this inbox.",
    )
    async def list_inbox_access(
        context: Context,
        inbox_id: Annotated[str, Field(description="Inbox id")],
    ) -> list[dict[str, Any]]:
        services = get_services(context)
        teammates = await services.client.inboxes.list_access(inbox_id)
        return [t.to_dict() for t in teammates]

    # -- mutations (two-step confirm) ---------------------------------------

    @mcp.tool(
        name="create_inbox",
        description=(
            "Create a workspace-scoped inbox. Channels still need to be "
            "wired up separately. WORKSPACE-WIDE."
        ),
    )
    async def create_inbox(
        context: Context,
        name: Annotated[str, Field(description="Inbox name, e.g. 'Support'")],
        teammate_ids: Annotated[
            list[str] | None,
            Field(description="Teammates to grant access at creation time"),
        ] = None,
        is_public: Annotated[
            bool | None, Field(description="Publicly visible to the workspace")
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_inbox",
            "name": name,
            "teammate_count": len(teammate_ids) if teammate_ids else 0,
            "teammate_ids": teammate_ids,
            "is_public": is_public,
        }
        gate = await confirm_or_preview(
            context,
            preview=preview,
            confirm=confirm,
            elicit_message=f"Create workspace inbox '{name}'?",
        )
        if gate is not None:
            return gate

        inbox = await services.client.inboxes.create(
            name=name, teammate_ids=teammate_ids, is_public=is_public
        )
        return {"confirmed": True, "inbox": to_inbox_summary(inbox).model_dump()}

    @mcp.tool(
        name="create_team_inbox",
        description="Create an inbox owned by a team (`team_id` like 'tim_abc').",
    )
    async def create_team_inbox(
        context: Context,
        team_id: Annotated[str, Field(description="Team id, e.g. 'tim_abc'")],
        name: Annotated[str, Field(description="Inbox name")],
        teammate_ids: Annotated[
            list[str] | None,
            Field(description="Teammates to grant access at creation time"),
        ] = None,
        is_public: Annotated[
            bool | None, Field(description="Publicly visible to the workspace")
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_team_inbox",
            "team_id": team_id,
            "name": name,
            "teammate_count": len(teammate_ids) if teammate_ids else 0,
            "teammate_ids": teammate_ids,
            "is_public": is_public,
        }
        gate = await confirm_or_preview(
            context,
            preview=preview,
            confirm=confirm,
            elicit_message=f"Create team inbox '{name}' on team {team_id}?",
        )
        if gate is not None:
            return gate

        inbox = await services.client.inboxes.create_for_team(
            team_id, name=name, teammate_ids=teammate_ids, is_public=is_public
        )
        return {"confirmed": True, "inbox": to_inbox_summary(inbox).model_dump()}

    @mcp.tool(
        name="grant_inbox_access",
        description="Grant inbox access to one or more teammates.",
    )
    async def grant_inbox_access(
        context: Context,
        inbox_id: Annotated[str, Field(description="Inbox id")],
        teammate_ids: Annotated[
            list[str], Field(description="Teammate ids to grant access to (>=1)")
        ],
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "grant_inbox_access",
            "inbox_id": inbox_id,
            "teammate_count": len(teammate_ids),
            "teammate_ids": teammate_ids,
        }
        gate = await confirm_or_preview(
            context,
            preview=preview,
            confirm=confirm,
            elicit_message=(
                f"Grant inbox {inbox_id} access to {len(teammate_ids)} teammate(s)?"
            ),
        )
        if gate is not None:
            return gate

        success = await services.client.inboxes.grant_access(
            inbox_id, teammate_ids=teammate_ids
        )
        return {"confirmed": True, "granted": success}

    @mcp.tool(
        name="revoke_inbox_access",
        description=(
            "Revoke inbox access from one or more teammates. The named "
            "teammates lose visibility into this inbox immediately."
        ),
    )
    async def revoke_inbox_access(
        context: Context,
        inbox_id: Annotated[str, Field(description="Inbox id")],
        teammate_ids: Annotated[
            list[str], Field(description="Teammate ids to revoke access from (>=1)")
        ],
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "revoke_inbox_access",
            "inbox_id": inbox_id,
            "teammate_count": len(teammate_ids),
            "teammate_ids": teammate_ids,
        }
        gate = await confirm_or_preview(
            context,
            preview=preview,
            confirm=confirm,
            elicit_message=(
                f"Revoke inbox {inbox_id} access from {len(teammate_ids)} teammate(s)?"
            ),
        )
        if gate is not None:
            return gate

        success = await services.client.inboxes.revoke_access(
            inbox_id, teammate_ids=teammate_ids
        )
        return {"confirmed": True, "revoked": success}


__all__ = ["register_tools"]
