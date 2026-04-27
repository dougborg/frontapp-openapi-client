"""Teams helper facade — list/get + add/remove teammate mutations.

Front exposes 4 endpoints under the ``teams`` tag: ``list_teams`` /
``get_team`` (reads) and ``add_teammates_to_team`` /
``remove_teammates_from_team`` (membership mutations). The
``frontapp://teams`` MCP reference resource (#82) handles the read
catalog browsing path; this helper exposes the full surface for direct
Python callers and for the MCP mutation tools (#86) that need to
modify team membership.

There is no ``create_team`` / ``delete_team`` in Front's API — teams
are workspace-admin primitives created in Front's UI.
"""

from __future__ import annotations

import builtins

from frontapp_public_api_client.helpers.base import Base


class Teams(Base):
    """Ergonomic operations over Front's ``/teams*`` endpoints."""

    async def list(self):
        """List every team in the workspace (no pagination)."""
        from frontapp_public_api_client.api.teams import list_teams
        from frontapp_public_api_client.utils import unwrap

        response = await list_teams.asyncio_detailed(client=self._client)
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def get(self, team_id: str):
        """Fetch one team by id (returns full ``TeamResponse``)."""
        from frontapp_public_api_client.api.teams import get_team
        from frontapp_public_api_client.models.team_response import TeamResponse
        from frontapp_public_api_client.utils import unwrap_as

        response = await get_team.asyncio_detailed(team_id, client=self._client)
        return unwrap_as(response, TeamResponse)

    async def add_teammates(
        self, team_id: str, teammate_ids: builtins.list[str]
    ) -> bool:
        """Add teammates to a team (POST /teams/{id}/teammates).

        Returns ``True`` on success (Front returns 204 No Content).
        Raises an ``APIError`` subclass on failure.
        """
        from frontapp_public_api_client.api.teams import add_teammates_to_team
        from frontapp_public_api_client.models.teammate_ids import TeammateIds
        from frontapp_public_api_client.utils import is_success, unwrap

        body = TeammateIds(teammate_ids=teammate_ids)
        response = await add_teammates_to_team.asyncio_detailed(
            team_id, client=self._client, body=body
        )
        if is_success(response):
            return True
        # Re-route through unwrap to raise the typed APIError.
        unwrap(response)
        return False

    async def remove_teammates(
        self, team_id: str, teammate_ids: builtins.list[str]
    ) -> bool:
        """Remove teammates from a team (DELETE /teams/{id}/teammates).

        Returns ``True`` on success (Front returns 204 No Content).
        Raises an ``APIError`` subclass on failure.
        """
        from frontapp_public_api_client.api.teams import remove_teammates_from_team
        from frontapp_public_api_client.models.teammate_ids import TeammateIds
        from frontapp_public_api_client.utils import is_success, unwrap

        body = TeammateIds(teammate_ids=teammate_ids)
        response = await remove_teammates_from_team.asyncio_detailed(
            team_id, client=self._client, body=body
        )
        if is_success(response):
            return True
        unwrap(response)
        return False
