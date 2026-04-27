"""MCP tools for Frontapp's deprecated contact-group surface.

**Front has deprecated all contact-group endpoints in favor of contact
lists.** Tool descriptions explicitly steer agents toward contact_lists
for new work; the tools exist so workspaces still using groups can
continue to manage them.

Same shape as contact_lists (the underlying primitives are nearly
identical) — same two-step confirm on every mutation, same 50-contact
cap on bulk removal.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.projections import (
    ContactListSummary,
    ContactSummary,
    to_contact_list_summary,
    to_contact_summary,
)
from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import ConfirmationResult, require_confirmation
from frontapp_public_api_client.helpers.constants import (
    CONTACT_BUCKET_REMOVE_CAP,
    CONTACT_BUCKET_REMOVE_OVER_CAP_MSG,
)

_DEPRECATION_NOTE = (
    "DEPRECATED: Front has deprecated contact groups in favor of contact "
    "lists. Use create_contact_list / add_contacts_to_contact_list etc. "
    "for new work."
)


def register_tools(mcp: FastMCP) -> None:
    """Register contact-group-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="list_contact_groups",
        description=(
            f"{_DEPRECATION_NOTE} List every contact group visible to the "
            "API token. Use to translate a group name into a 'grp_*' id."
        ),
    )
    async def list_contact_groups(context: Context) -> list[ContactListSummary]:
        services = get_services(context)
        items = await services.client.contact_groups.list()
        return [to_contact_list_summary(item) for item in items]

    @mcp.tool(
        name="list_team_contact_groups",
        description=f"{_DEPRECATION_NOTE} List contact groups owned by a specific team.",
    )
    async def list_team_contact_groups(
        context: Context,
        team_id: Annotated[str, Field(description="Team id, e.g. 'tim_abc123'")],
    ) -> list[ContactListSummary]:
        services = get_services(context)
        items = await services.client.contact_groups.list_for_team(team_id)
        return [to_contact_list_summary(item) for item in items]

    @mcp.tool(
        name="list_teammate_contact_groups",
        description=(
            f"{_DEPRECATION_NOTE} List contact groups owned by a specific "
            "teammate (private groups)."
        ),
    )
    async def list_teammate_contact_groups(
        context: Context,
        teammate_id: Annotated[
            str, Field(description="Teammate id, e.g. 'tea_abc123'")
        ],
    ) -> list[ContactListSummary]:
        services = get_services(context)
        items = await services.client.contact_groups.list_for_teammate(teammate_id)
        return [to_contact_list_summary(item) for item in items]

    @mcp.tool(
        name="list_contacts_in_group",
        description=(
            f"{_DEPRECATION_NOTE} List the contacts that belong to a "
            "given group. Returns ContactSummary objects. Cursor-paginated."
        ),
    )
    async def list_contacts_in_group(
        context: Context,
        contact_group_id: Annotated[
            str, Field(description="Contact group id, e.g. 'grp_abc123'")
        ],
        limit: Annotated[
            int | None, Field(description="Page size (max 100, default 50)")
        ] = None,
        page_token: Annotated[
            str | None,
            Field(description="Cursor from previous page's pagination.next"),
        ] = None,
    ) -> list[ContactSummary]:
        services = get_services(context)
        contacts = await services.client.contact_groups.list_members(
            contact_group_id, limit=limit, page_token=page_token
        )
        return [to_contact_summary(c) for c in contacts]

    # -- mutations (two-step confirm) ---------------------------------------

    @mcp.tool(
        name="create_contact_group",
        description=(
            f"{_DEPRECATION_NOTE} Create a workspace-scoped contact group. "
            "Front silently targets the oldest active workspace — prefer "
            "create_team_contact_group when the team is known. Two-step "
            "confirm."
        ),
    )
    async def create_contact_group(
        context: Context,
        name: Annotated[str, Field(description="Group name")],
        confirm: Annotated[
            bool, Field(description="Must be true to create the group")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {"action": "create_contact_group", "name": name}
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context, f"Create workspace-scoped contact group {name!r}?"
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_groups.create(name)
        return {"confirmed": True, "name": name}

    @mcp.tool(
        name="create_team_contact_group",
        description=(
            f"{_DEPRECATION_NOTE} Create a team-scoped contact group. Two-step confirm."
        ),
    )
    async def create_team_contact_group(
        context: Context,
        team_id: Annotated[str, Field(description="Team id")],
        name: Annotated[str, Field(description="Group name")],
        confirm: Annotated[
            bool, Field(description="Must be true to create the group")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_team_contact_group",
            "team_id": team_id,
            "name": name,
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context, f"Create contact group {name!r} for team {team_id}?"
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_groups.create_for_team(team_id, name)
        return {"confirmed": True, "team_id": team_id, "name": name}

    @mcp.tool(
        name="create_teammate_contact_group",
        description=(
            f"{_DEPRECATION_NOTE} Create a teammate-scoped (private) "
            "contact group. Two-step confirm."
        ),
    )
    async def create_teammate_contact_group(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id")],
        name: Annotated[str, Field(description="Group name")],
        confirm: Annotated[
            bool, Field(description="Must be true to create the group")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_teammate_contact_group",
            "teammate_id": teammate_id,
            "name": name,
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context,
            f"Create private contact group {name!r} for teammate {teammate_id}?",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_groups.create_for_teammate(teammate_id, name)
        return {"confirmed": True, "teammate_id": teammate_id, "name": name}

    @mcp.tool(
        name="delete_contact_group",
        description=(
            f"{_DEPRECATION_NOTE} Delete a contact group. Dissolves the "
            "group and all memberships, but does NOT delete the underlying "
            "contacts. Two-step confirm."
        ),
    )
    async def delete_contact_group(
        context: Context,
        contact_group_id: Annotated[str, Field(description="Contact group id")],
        confirm: Annotated[
            bool, Field(description="Must be true to delete the group")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "delete_contact_group",
            "contact_group_id": contact_group_id,
            "note": "Dissolves the group; contacts NOT deleted.",
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context,
            f"Delete contact group {contact_group_id}? (Members are kept.)",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_groups.delete(contact_group_id)
        return {"confirmed": True, "contact_group_id": contact_group_id}

    @mcp.tool(
        name="add_contacts_to_group",
        description=(
            f"{_DEPRECATION_NOTE} Add contacts to a group (bulk). "
            "contact_ids accepts both 'crd_*' ids and Front resource "
            "aliases. Two-step confirm."
        ),
    )
    async def add_contacts_to_group(
        context: Context,
        contact_group_id: Annotated[str, Field(description="Target contact group id")],
        contact_ids: Annotated[
            list[str], Field(description="Contact ids or aliases to add")
        ],
        confirm: Annotated[
            bool, Field(description="Must be true to apply the add")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "add_contacts_to_group",
            "contact_group_id": contact_group_id,
            "contact_ids": contact_ids,
            "count": len(contact_ids),
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context,
            f"Add {len(contact_ids)} contact(s) to group {contact_group_id}?",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_groups.add_contacts(contact_group_id, contact_ids)
        return {
            "confirmed": True,
            "contact_group_id": contact_group_id,
            "added_count": len(contact_ids),
        }

    @mcp.tool(
        name="remove_contacts_from_group",
        description=(
            f"{_DEPRECATION_NOTE} Remove contacts from a group (bulk). "
            "contact_ids accepts both 'crd_*' ids and Front resource "
            "aliases. CAPPED at 50 contact_ids per call. Two-step confirm."
        ),
    )
    async def remove_contacts_from_group(
        context: Context,
        contact_group_id: Annotated[str, Field(description="Target contact group id")],
        contact_ids: Annotated[
            list[str],
            Field(description="Contact ids or aliases to remove (max 50 per call)"),
        ],
        confirm: Annotated[
            bool, Field(description="Must be true to apply the remove")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "remove_contacts_from_group",
            "contact_group_id": contact_group_id,
            "contact_ids": contact_ids,
            "count": len(contact_ids),
        }
        if len(contact_ids) > CONTACT_BUCKET_REMOVE_CAP:
            return {
                "error": CONTACT_BUCKET_REMOVE_OVER_CAP_MSG.format(
                    count=len(contact_ids)
                ),
                "confirmed": False,
            }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context,
            f"Remove {len(contact_ids)} contact(s) from group {contact_group_id}?",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_groups.remove_contacts(
            contact_group_id, contact_ids
        )
        return {
            "confirmed": True,
            "contact_group_id": contact_group_id,
            "removed_count": len(contact_ids),
        }


__all__ = ["register_tools"]
