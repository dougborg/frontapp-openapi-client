"""MCP tool for partner-app event triggering.

Single endpoint — POST ``/applications/{application_uid}/events``.
Niche partner-integration use case: a Front partner-built app
triggers a custom event from an external system, and Front routes it
through workflows / rules.

The application catalog is not enumerable via the API. The agent
needs to know the application_uid out of band (it's surfaced in
Front's app-management UI, or passed in by the user).

Two-step ``confirm_or_preview`` gate — even though this is "just"
firing an event, it can trigger Front workflows that mutate
conversation state, so the safer path is to confirm before sending.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import confirm_or_preview


def register_tools(mcp: FastMCP) -> None:
    """Register the application event-trigger tool."""

    @mcp.tool(
        name="trigger_application_event",
        description=(
            "Trigger an event on behalf of a Front partner application. "
            "Niche partner-integration tool — the agent needs the "
            "`application_uid` (a `app_*` id surfaced in Front's "
            "app-management UI). The event payload references either "
            "an internal Front object id (`app_object_id`) or an "
            "external link (`app_object_ext_link`); pass at least one. "
            "Two-step confirm because the event may trigger workflows "
            "that mutate conversation state."
        ),
    )
    async def trigger_application_event(
        context: Context,
        application_uid: Annotated[
            str, Field(description="`app_*` uid of the partner application")
        ],
        event_type: Annotated[
            str,
            Field(
                description=(
                    "Event type the partner app declared. Routed to Front "
                    "workflows that match this type."
                )
            ),
        ],
        app_object_id: Annotated[
            str | None,
            Field(
                description=(
                    "Optional Front object id (e.g. `cnv_*`, `crd_*`) the "
                    "event is associated with."
                )
            ),
        ] = None,
        app_object_ext_link: Annotated[
            str | None,
            Field(
                description=(
                    "Optional external URL identifying the object. Pair "
                    "with `app_object_id` or use as a standalone reference."
                )
            ),
        ] = None,
        confirm: Annotated[
            bool, Field(description="Must be true to fire the event.")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "trigger_application_event",
            "application_uid": application_uid,
            "event_type": event_type,
            "app_object_id": app_object_id,
            "app_object_ext_link": app_object_ext_link,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        await services.client.applications.trigger_event(
            application_uid,
            event_type=event_type,
            app_object_id=app_object_id,
            app_object_ext_link=app_object_ext_link,
        )
        return {
            "confirmed": True,
            "application_uid": application_uid,
            "event_type": event_type,
        }
