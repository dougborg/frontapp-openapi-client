"""Applications helper — partner-app event trigger.

The single endpoint under Front's ``applications`` tag is
``trigger_app_event`` (POST ``/applications/{application_uid}/events``).
It's a partner-integration primitive: a Front partner-built app
triggers a custom event from an external system, and Front routes it
through workflows / rules.

Niche use case for the typical agent — included here for completeness
of the workspace-admin partition (#16). The application catalog is
not enumerable via the API; partners need to know their app uid out
of band (it's surfaced in Front's app-management UI).
"""

from __future__ import annotations

from frontapp_public_api_client.helpers.base import Base


class Applications(Base):
    """Ergonomic operations over Front's ``/applications*`` endpoints."""

    async def trigger_event(
        self,
        application_uid: str,
        *,
        event_type: str,
        app_object_id: str | None = None,
        app_object_ext_link: str | None = None,
    ) -> bool:
        """Trigger an event on behalf of a Front partner application.

        Front's ``AppEvent`` payload requires ``event_type`` plus an
        ``app_object`` referencing either an internal ``id`` or an
        external link. At least one of ``app_object_id`` or
        ``app_object_ext_link`` should be provided; the helper passes
        through whichever is set.

        Returns ``True`` on Front's 204 No Content response. Raises
        ``APIError`` on failure.
        """
        from frontapp_public_api_client.api.applications import trigger_app_event
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.models.app_event import AppEvent
        from frontapp_public_api_client.models.app_event_app_object import (
            AppEventAppObject,
        )
        from frontapp_public_api_client.utils import is_success, unwrap

        app_object = AppEventAppObject(
            id=to_unset(app_object_id),
            ext_link=to_unset(app_object_ext_link),
        )
        body = AppEvent(event_type=event_type, app_object=app_object)
        response = await trigger_app_event.asyncio_detailed(
            application_uid, client=self._client, body=body
        )
        if is_success(response):
            return True
        unwrap(response)
        return False
