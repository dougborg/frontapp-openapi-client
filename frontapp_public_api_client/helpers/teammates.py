"""Teammates helper facade — ergonomic wrappers around generated teammate endpoints.

Exposes ``client.teammates`` covering the workspace teammate roster:

- ``list`` / ``get`` — read the workspace's teammates
- ``update`` — change a teammate's name / username / availability
- ``list_inboxes`` — inboxes a teammate has access to
- ``list_assigned_conversations`` / ``iter_assigned_conversations`` —
  conversations currently assigned to a teammate (paginated)

Quirks worth knowing:

- ``UpdateTeammate`` only accepts username / first_name / last_name /
  is_available / custom_fields. Email and admin status are read-only at
  this surface — managed via Front's admin UI.
- ``list_teammates`` and ``list_teammate_inboxes`` take no pagination
  params (Front returns the full set in one shot for both).
- The ``TeammateResponse`` ``type_`` field deserializes to ``type`` in
  the dict form; the ``Teammate`` Pydantic model uses ``type`` directly.
"""

from __future__ import annotations

import builtins
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from frontapp_public_api_client.helpers.base import Base

if TYPE_CHECKING:
    from frontapp_public_api_client.domain import Inbox, Teammate


class Teammates(Base):
    """Ergonomic operations over Frontapp's ``/teammates*`` surface."""

    # -- reads --------------------------------------------------------------

    async def list(self) -> builtins.list[Teammate]:
        """List every teammate in the workspace.

        No pagination params — Front returns the full set in one shot.
        """
        from frontapp_public_api_client.api.teammates import list_teammates
        from frontapp_public_api_client.domain import Teammate
        from frontapp_public_api_client.utils import unwrap

        response = await list_teammates.asyncio_detailed(client=self._client)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Teammate.model_validate(t.to_dict()) for t in results]

    async def get(self, teammate_id: str) -> Teammate:
        """Fetch one teammate by id (e.g. ``"tea_abc"``)."""
        from frontapp_public_api_client.api.teammates import get_teammate
        from frontapp_public_api_client.domain import Teammate
        from frontapp_public_api_client.models.teammate_response import TeammateResponse
        from frontapp_public_api_client.utils import unwrap_as

        response = await get_teammate.asyncio_detailed(
            teammate_id=teammate_id, client=self._client
        )
        teammate = unwrap_as(response, TeammateResponse)
        return Teammate.model_validate(teammate.to_dict())

    async def list_inboxes(self, teammate_id: str) -> builtins.list[Inbox]:
        """List inboxes this teammate has access to.

        No pagination — Front returns the full set in one shot.
        """
        from frontapp_public_api_client.api.teammates import list_teammate_inboxes
        from frontapp_public_api_client.domain import Inbox
        from frontapp_public_api_client.utils import unwrap

        response = await list_teammate_inboxes.asyncio_detailed(
            teammate_id=teammate_id, client=self._client
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Inbox.model_validate(i.to_dict()) for i in results]

    async def list_assigned_conversations(
        self,
        teammate_id: str,
        *,
        q: str | None = None,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Any]:
        """List conversations currently assigned to this teammate.

        Returns raw attrs ``ConversationResponse`` items.
        """
        from frontapp_public_api_client.api.teammates import (
            list_assigned_conversations,
        )
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "teammate_id": teammate_id}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_assigned_conversations.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def iter_assigned_conversations(
        self,
        teammate_id: str,
        *,
        q: str | None = None,
        limit: int | None = None,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[Any]:
        """Auto-paginated iterator over conversations assigned to this teammate.

        Yields raw attrs ``ConversationResponse`` items.
        """
        from frontapp_public_api_client.api.teammates import (
            list_assigned_conversations,
        )

        kwargs: dict[str, Any] = {"teammate_id": teammate_id}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit

        async for item in self._paginate(
            list_assigned_conversations.asyncio_detailed,
            max_items=max_items,
            max_pages=max_pages,
            **kwargs,
        ):
            yield item

    # -- mutations ----------------------------------------------------------

    async def update(
        self,
        teammate_id: str,
        *,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_available: bool | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> bool:
        """Update mutable fields on a teammate.

        Email and admin status are read-only at this API surface — those
        live in Front's admin UI. Returns True on the documented 204 No
        Content.
        """
        from frontapp_public_api_client.api.teammates import update_teammate
        from frontapp_public_api_client.models.update_teammate import UpdateTeammate
        from frontapp_public_api_client.utils import is_success

        kwargs: dict[str, Any] = {}
        if username is not None:
            kwargs["username"] = username
        if first_name is not None:
            kwargs["first_name"] = first_name
        if last_name is not None:
            kwargs["last_name"] = last_name
        if is_available is not None:
            kwargs["is_available"] = is_available
        if custom_fields is not None:
            kwargs["custom_fields"] = custom_fields

        body = UpdateTeammate(**kwargs)
        response = await update_teammate.asyncio_detailed(
            teammate_id=teammate_id, client=self._client, body=body
        )
        return is_success(response)


__all__ = ["Teammates"]
