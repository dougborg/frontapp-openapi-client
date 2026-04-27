"""MCP tools for Frontapp contact lists.

Contact lists are named buckets of contacts used for bulk operations
(broadcasts, segmentation). All mutations use the standard two-step
confirm pattern. ``delete_contact_list`` only dissolves the list — the
underlying contacts remain in the workspace.
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


def register_tools(mcp: FastMCP) -> None:
    """Register contact-list-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="list_contact_lists",
        description=(
            "List every contact list visible to the API token (workspace, "
            "team, and teammate scopes). Use to translate a list name "
            "(e.g. 'VIP') into a 'lst_*' id before adding/removing "
            "contacts."
        ),
    )
    async def list_contact_lists(context: Context) -> list[ContactListSummary]:
        services = get_services(context)
        items = await services.client.contact_lists.list()
        return [to_contact_list_summary(item) for item in items]

    @mcp.tool(
        name="list_team_contact_lists",
        description="List contact lists owned by a specific team.",
    )
    async def list_team_contact_lists(
        context: Context,
        team_id: Annotated[str, Field(description="Team id, e.g. 'tim_abc123'")],
    ) -> list[ContactListSummary]:
        services = get_services(context)
        items = await services.client.contact_lists.list_for_team(team_id)
        return [to_contact_list_summary(item) for item in items]

    @mcp.tool(
        name="list_teammate_contact_lists",
        description="List contact lists owned by a specific teammate (private lists).",
    )
    async def list_teammate_contact_lists(
        context: Context,
        teammate_id: Annotated[
            str, Field(description="Teammate id, e.g. 'tea_abc123'")
        ],
    ) -> list[ContactListSummary]:
        services = get_services(context)
        items = await services.client.contact_lists.list_for_teammate(teammate_id)
        return [to_contact_list_summary(item) for item in items]

    @mcp.tool(
        name="list_contacts_in_contact_list",
        description=(
            "List the contacts that belong to a given list. Returns "
            "ContactSummary objects (id, name, handles). Cursor-paginated "
            "— pass page_token from a previous response to fetch the next "
            "page; lists with thousands of members will need pagination."
        ),
    )
    async def list_contacts_in_contact_list(
        context: Context,
        contact_list_id: Annotated[
            str, Field(description="Contact list id, e.g. 'lst_abc123'")
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
        contacts = await services.client.contact_lists.list_members(
            contact_list_id, limit=limit, page_token=page_token
        )
        return [to_contact_summary(c) for c in contacts]

    # -- mutations (two-step confirm) ---------------------------------------

    @mcp.tool(
        name="create_contact_list",
        description=(
            "Create a workspace-scoped contact list. NOTE: Front silently "
            "targets the oldest active workspace the token has access to "
            "— prefer create_team_contact_list when you have a specific "
            "team. Two-step confirm. The new list's id is NOT returned by "
            "Front; follow up with list_contact_lists and match by name."
        ),
    )
    async def create_contact_list(
        context: Context,
        name: Annotated[str, Field(description="List name, e.g. 'VIP'")],
        confirm: Annotated[
            bool, Field(description="Must be true to create the list")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {"action": "create_contact_list", "name": name}
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context,
            f"Create workspace-scoped contact list {name!r}? (Targets the "
            "oldest active workspace.)",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_lists.create(name)
        return {"confirmed": True, "name": name}

    @mcp.tool(
        name="create_team_contact_list",
        description=(
            "Create a team-scoped contact list. Preferred over "
            "create_contact_list when the team is known. Two-step confirm."
        ),
    )
    async def create_team_contact_list(
        context: Context,
        team_id: Annotated[str, Field(description="Team id, e.g. 'tim_abc123'")],
        name: Annotated[str, Field(description="List name")],
        confirm: Annotated[
            bool, Field(description="Must be true to create the list")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_team_contact_list",
            "team_id": team_id,
            "name": name,
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context, f"Create contact list {name!r} for team {team_id}?"
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_lists.create_for_team(team_id, name)
        return {"confirmed": True, "team_id": team_id, "name": name}

    @mcp.tool(
        name="create_teammate_contact_list",
        description="Create a teammate-scoped (private) contact list. Two-step confirm.",
    )
    async def create_teammate_contact_list(
        context: Context,
        teammate_id: Annotated[
            str, Field(description="Teammate id, e.g. 'tea_abc123'")
        ],
        name: Annotated[str, Field(description="List name")],
        confirm: Annotated[
            bool, Field(description="Must be true to create the list")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_teammate_contact_list",
            "teammate_id": teammate_id,
            "name": name,
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context,
            f"Create private contact list {name!r} for teammate {teammate_id}?",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_lists.create_for_teammate(teammate_id, name)
        return {"confirmed": True, "teammate_id": teammate_id, "name": name}

    @mcp.tool(
        name="delete_contact_list",
        description=(
            "Delete a contact list. Dissolves the list and all "
            "memberships, but does NOT delete the underlying contacts — "
            "they remain in the workspace. Two-step confirm."
        ),
    )
    async def delete_contact_list(
        context: Context,
        contact_list_id: Annotated[str, Field(description="Contact list id to delete")],
        confirm: Annotated[
            bool, Field(description="Must be true to delete the list")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "delete_contact_list",
            "contact_list_id": contact_list_id,
            "note": "Dissolves the list; contacts NOT deleted.",
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context,
            f"Delete contact list {contact_list_id}? (Members are kept; "
            "only the list is removed.)",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_lists.delete(contact_list_id)
        return {"confirmed": True, "contact_list_id": contact_list_id}

    @mcp.tool(
        name="add_contacts_to_contact_list",
        description=(
            "Add contacts to a list (bulk). contact_ids accepts both "
            "'crd_*' ids and Front resource aliases like "
            "'alt:email:foo@example.com'. Two-step confirm."
        ),
    )
    async def add_contacts_to_contact_list(
        context: Context,
        contact_list_id: Annotated[str, Field(description="Target contact list id")],
        contact_ids: Annotated[
            list[str],
            Field(description="Contact ids or resource aliases to add"),
        ],
        confirm: Annotated[
            bool, Field(description="Must be true to apply the add")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "add_contacts_to_contact_list",
            "contact_list_id": contact_list_id,
            "contact_ids": contact_ids,
            "count": len(contact_ids),
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context,
            f"Add {len(contact_ids)} contact(s) to list {contact_list_id}?",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_lists.add_contacts(contact_list_id, contact_ids)
        return {
            "confirmed": True,
            "contact_list_id": contact_list_id,
            "added_count": len(contact_ids),
        }

    @mcp.tool(
        name="remove_contacts_from_contact_list",
        description=(
            "Remove contacts from a list (bulk). contact_ids accepts both "
            "'crd_*' ids and Front resource aliases like "
            "'alt:email:foo@example.com'. CAPPED at 50 contact_ids per "
            "call by Front's server-side validation — split larger "
            "removals into multiple calls. Two-step confirm."
        ),
    )
    async def remove_contacts_from_contact_list(
        context: Context,
        contact_list_id: Annotated[str, Field(description="Target contact list id")],
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
            "action": "remove_contacts_from_contact_list",
            "contact_list_id": contact_list_id,
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
            f"Remove {len(contact_ids)} contact(s) from list {contact_list_id}?",
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        await services.client.contact_lists.remove_contacts(
            contact_list_id, contact_ids
        )
        return {
            "confirmed": True,
            "contact_list_id": contact_list_id,
            "removed_count": len(contact_ids),
        }


__all__ = ["register_tools"]
