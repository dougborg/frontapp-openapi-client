"""MCP tools for Front team-membership mutations.

Front exposes 4 endpoints under the ``teams`` tag — list / get reads
plus the membership pair (``add_teammates_to_team`` /
``remove_teammates_from_team``). The reads are surfaced via
``frontapp://teams`` (#82); these tools cover the mutations.

Concrete agent value: "reassign capacity to a team during a spike",
"onboard new teammate Alice to the support team". Both follow the
two-step ``confirm_or_preview`` pattern; the preview shows the count
+ ids of teammates being added/removed so the human sees what would
happen before approving the elicitation.

There is no ``create_team`` / ``delete_team`` in Front's API — teams
are workspace-admin primitives created in Front's UI.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import confirm_or_preview


def register_tools(mcp: FastMCP) -> None:
    """Register team-related tools with the FastMCP server."""

    @mcp.tool(
        name="add_team_members",
        description=(
            "Add one or more teammates to a team. Two-step confirm: "
            "confirm=False returns a preview of count + ids; "
            "confirm=True executes the membership change. Use "
            "frontapp://teams to translate a team name into a "
            "`tim_*` id and frontapp://teammates for `tea_*` ids."
        ),
    )
    async def add_team_members(
        context: Context,
        team_id: Annotated[str, Field(description="`tim_*` id")],
        teammate_ids: Annotated[
            list[str], Field(description="`tea_*` ids to add to the team.")
        ],
        confirm: Annotated[bool, Field(description="Must be true to apply.")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "add_team_members",
            "team_id": team_id,
            "teammate_count": len(teammate_ids),
            "teammate_ids": teammate_ids,
        }
        gate = await confirm_or_preview(
            context,
            preview=preview,
            confirm=confirm,
            elicit_message=(f"Add {len(teammate_ids)} teammate(s) to team {team_id}?"),
        )
        if gate is not None:
            return gate

        await services.client.teams.add_teammates(team_id, teammate_ids)
        return {
            "confirmed": True,
            "team_id": team_id,
            "added_count": len(teammate_ids),
        }

    @mcp.tool(
        name="remove_team_members",
        description=(
            "Remove one or more teammates from a team. Two-step "
            "confirm: confirm=False returns a preview of count + ids; "
            "confirm=True executes the change. Removing a teammate "
            "from their last team typically leaves them workspace-"
            "scoped only — verify with the user if that's intended."
        ),
    )
    async def remove_team_members(
        context: Context,
        team_id: Annotated[str, Field(description="`tim_*` id")],
        teammate_ids: Annotated[
            list[str], Field(description="`tea_*` ids to remove from the team.")
        ],
        confirm: Annotated[bool, Field(description="Must be true to apply.")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "remove_team_members",
            "team_id": team_id,
            "teammate_count": len(teammate_ids),
            "teammate_ids": teammate_ids,
        }
        gate = await confirm_or_preview(
            context,
            preview=preview,
            confirm=confirm,
            elicit_message=(
                f"Remove {len(teammate_ids)} teammate(s) from team {team_id}?"
            ),
        )
        if gate is not None:
            return gate

        await services.client.teams.remove_teammates(team_id, teammate_ids)
        return {
            "confirmed": True,
            "team_id": team_id,
            "removed_count": len(teammate_ids),
        }
