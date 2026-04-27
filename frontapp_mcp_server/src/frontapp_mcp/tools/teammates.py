"""MCP tools for Frontapp teammates.

Five tools — 4 cached reads + 1 mutation (two-step confirm). The
``frontapp://teammates`` resource still ships as the preferred name-to-id
lookup at session start; these tools are for programmatic
listing/filtering and the rare update operation.

Email and admin status are read-only via Front's API — managed in Front's
admin UI. ``update_teammate`` only flips username / first_name /
last_name / is_available / custom_fields.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.projections import ConversationSummary, to_summary
from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import (
    confirm_or_preview,
)
from frontapp_public_api_client.domain import Inbox, Teammate


def register_tools(mcp: FastMCP) -> None:
    """Register teammate-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="list_teammates",
        description=(
            "List every teammate in the workspace. Prefer the "
            "`frontapp://teammates` resource for name-to-id lookups; this "
            "tool is for programmatic listing."
        ),
    )
    async def list_teammates(context: Context) -> list[Teammate]:
        services = get_services(context)
        return await services.client.teammates.list()

    @mcp.tool(
        name="get_teammate",
        description="Fetch full details for one teammate by id (e.g. 'tea_abc').",
    )
    async def get_teammate(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id, e.g. 'tea_abc'")],
    ) -> Teammate:
        services = get_services(context)
        return await services.client.teammates.get(teammate_id)

    @mcp.tool(
        name="list_teammate_inboxes",
        description="List inboxes this teammate has access to.",
    )
    async def list_teammate_inboxes(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id")],
    ) -> list[Inbox]:
        services = get_services(context)
        return await services.client.teammates.list_inboxes(teammate_id)

    @mcp.tool(
        name="list_assigned_conversations",
        description=(
            "List conversations currently assigned to this teammate. Pass "
            "`q=` to filter with Front search syntax (e.g. 'status:open')."
        ),
    )
    async def list_assigned_conversations(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id")],
        q: Annotated[str | None, Field(description="Front search syntax")] = None,
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[ConversationSummary]:
        from frontapp_public_api_client.domain import Conversation

        services = get_services(context)
        items = await services.client.teammates.list_assigned_conversations(
            teammate_id, q=q, limit=limit, page_token=page_token
        )
        return [
            to_summary(Conversation.model_validate(item.to_dict())) for item in items
        ]

    # -- mutation (two-step confirm) ----------------------------------------

    @mcp.tool(
        name="update_teammate",
        description=(
            "Update a teammate's username / name / availability. Email and "
            "admin status are NOT changeable via this API — manage those "
            "in Front's admin UI. Two-step confirm."
        ),
    )
    async def update_teammate(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id")],
        username: Annotated[
            str | None, Field(description="New username (login)")
        ] = None,
        first_name: Annotated[str | None, Field(description="New first name")] = None,
        last_name: Annotated[str | None, Field(description="New last name")] = None,
        is_available: Annotated[
            bool | None,
            Field(description="Set the teammate's availability flag"),
        ] = None,
        custom_fields: Annotated[
            dict[str, Any] | None,
            Field(
                description=(
                    "Workspace-defined custom fields to set on the teammate. "
                    "Replaces the full custom_fields object."
                )
            ),
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        changes = {
            k: v
            for k, v in {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "is_available": is_available,
                "custom_fields": custom_fields,
            }.items()
            if v is not None
        }
        preview = {
            "action": "update_teammate",
            "teammate_id": teammate_id,
            "changes": changes,
        }
        if not changes:
            return {
                "preview": preview,
                "confirmed": False,
                "result": "no_changes_requested",
            }
        summary = ", ".join(f"{k}={v}" for k, v in changes.items())
        gate = await confirm_or_preview(
            context,
            preview=preview,
            confirm=confirm,
            elicit_message=f"Update teammate {teammate_id}: {summary}?",
        )
        if gate is not None:
            return gate

        success = await services.client.teammates.update(
            teammate_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_available=is_available,
            custom_fields=custom_fields,
        )
        return {"confirmed": True, "updated": success}


__all__ = ["register_tools"]
