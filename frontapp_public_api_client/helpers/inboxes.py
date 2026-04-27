"""Inboxes helper facade — ergonomic wrappers around generated inbox endpoints.

Exposes ``client.inboxes`` covering the workspace-level inbox catalog
(``inboxes/``). Inboxes are channel containers — every conversation belongs
to one — and they're workspace-shared reference data.

Reads cover the workspace, team-, and teammate-private list scopes plus
the per-inbox conversation/channel/access lookups. Mutations cover create
plus the teammate access grants/revokes.

Quirks worth knowing:

- The DELETE-access endpoint module is ``removes_inbox_access`` (with the
  ``removes_`` prefix flagged in ``api-facts.yaml``
  ``summary.module_name_quirks``). The helper renames it to the more
  conventional ``revoke_access``.
- ``InboxResponse`` carries every field as ``UNSET``-defaulted (including
  ``id`` and ``name``) — the ``Inbox`` Pydantic projection reflects that
  with all-Optional fields.
- Front has no ``update_inbox`` endpoint — only create + access
  grant/revoke after that. Inbox name and visibility are immutable post-
  creation.
- ``list_inboxes``, ``list_team_inboxes``, ``list_teammate_private_inboxes``,
  ``list_inbox_channels``, and ``list_inbox_access`` all take no
  pagination params — the generated endpoints return the full set in one
  shot.
"""

from __future__ import annotations

import builtins
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from frontapp_public_api_client.helpers.base import Base

if TYPE_CHECKING:
    from frontapp_public_api_client.domain import Inbox


class Inboxes(Base):
    """Ergonomic operations over Frontapp's inbox surface."""

    # -- reads --------------------------------------------------------------

    async def list(self) -> builtins.list[Inbox]:
        """List every inbox visible to the API token."""
        from frontapp_public_api_client.api.inboxes import list_inboxes
        from frontapp_public_api_client.domain import Inbox
        from frontapp_public_api_client.utils import unwrap

        response = await list_inboxes.asyncio_detailed(client=self._client)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Inbox.model_validate(i.to_dict()) for i in results]

    async def list_for_team(self, team_id: str) -> builtins.list[Inbox]:
        """List inboxes owned by a team (``"tim_abc"``)."""
        from frontapp_public_api_client.api.inboxes import list_team_inboxes
        from frontapp_public_api_client.domain import Inbox
        from frontapp_public_api_client.utils import unwrap

        response = await list_team_inboxes.asyncio_detailed(
            team_id=team_id, client=self._client
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Inbox.model_validate(i.to_dict()) for i in results]

    async def list_private_for_teammate(self, teammate_id: str) -> builtins.list[Inbox]:
        """List a teammate's private inboxes (``"tea_abc"``)."""
        from frontapp_public_api_client.api.inboxes import (
            list_teammate_private_inboxes,
        )
        from frontapp_public_api_client.domain import Inbox
        from frontapp_public_api_client.utils import unwrap

        response = await list_teammate_private_inboxes.asyncio_detailed(
            teammate_id=teammate_id, client=self._client
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Inbox.model_validate(i.to_dict()) for i in results]

    async def get(self, inbox_id: str) -> Inbox:
        """Fetch one inbox by id (e.g. ``"inb_abc"``)."""
        from frontapp_public_api_client.api.inboxes import get_inbox
        from frontapp_public_api_client.domain import Inbox
        from frontapp_public_api_client.models.inbox_response import InboxResponse
        from frontapp_public_api_client.utils import unwrap_as

        response = await get_inbox.asyncio_detailed(
            inbox_id=inbox_id, client=self._client
        )
        inbox = unwrap_as(response, InboxResponse)
        return Inbox.model_validate(inbox.to_dict())

    async def list_conversations(
        self,
        inbox_id: str,
        *,
        q: str | None = None,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Any]:
        """List conversations in this inbox. Returns raw attrs models."""
        from frontapp_public_api_client.api.inboxes import list_inbox_conversations
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "inbox_id": inbox_id}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_inbox_conversations.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def iter_conversations(
        self,
        inbox_id: str,
        *,
        q: str | None = None,
        limit: int | None = None,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[Any]:
        """Auto-paginated iterator over conversations in this inbox.

        Yields raw attrs ``ConversationResponse`` items.
        """
        from frontapp_public_api_client.api.inboxes import list_inbox_conversations

        kwargs: dict[str, Any] = {"inbox_id": inbox_id}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit

        async for item in self._paginate(
            list_inbox_conversations.asyncio_detailed,
            max_items=max_items,
            max_pages=max_pages,
            **kwargs,
        ):
            yield item

    async def list_channels(self, inbox_id: str) -> builtins.list[Any]:
        """List channels routing into this inbox. Returns raw attrs models."""
        from frontapp_public_api_client.api.inboxes import list_inbox_channels
        from frontapp_public_api_client.utils import unwrap

        response = await list_inbox_channels.asyncio_detailed(
            inbox_id=inbox_id, client=self._client
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def list_access(self, inbox_id: str) -> builtins.list[Any]:
        """List teammates with access to this inbox. Returns raw attrs models."""
        from frontapp_public_api_client.api.inboxes import list_inbox_access
        from frontapp_public_api_client.utils import unwrap

        response = await list_inbox_access.asyncio_detailed(
            inbox_id=inbox_id, client=self._client
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    # -- mutations ----------------------------------------------------------

    async def create(
        self,
        *,
        name: str,
        teammate_ids: builtins.list[str] | None = None,
        is_public: bool | None = None,
    ) -> Inbox:
        """Create a workspace-scoped inbox.

        Creates a new shared inbox container. Channels still need to be
        wired up separately. Workspace-wide change.
        """
        from frontapp_public_api_client.api.inboxes import create_inbox
        from frontapp_public_api_client.domain import Inbox
        from frontapp_public_api_client.models.create_inbox import CreateInbox
        from frontapp_public_api_client.models.inbox_response import InboxResponse
        from frontapp_public_api_client.utils import unwrap_as

        kwargs: dict[str, Any] = {"name": name}
        if teammate_ids is not None:
            kwargs["teammate_ids"] = teammate_ids
        if is_public is not None:
            kwargs["is_public"] = is_public

        body = CreateInbox(**kwargs)
        response = await create_inbox.asyncio_detailed(client=self._client, body=body)
        inbox = unwrap_as(response, InboxResponse)
        return Inbox.model_validate(inbox.to_dict())

    async def create_for_team(
        self,
        team_id: str,
        *,
        name: str,
        teammate_ids: builtins.list[str] | None = None,
        is_public: bool | None = None,
    ) -> Inbox:
        """Create an inbox owned by a team (``"tim_abc"``)."""
        from frontapp_public_api_client.api.inboxes import create_team_inbox
        from frontapp_public_api_client.domain import Inbox
        from frontapp_public_api_client.models.create_team_inbox import CreateTeamInbox
        from frontapp_public_api_client.models.inbox_response import InboxResponse
        from frontapp_public_api_client.utils import unwrap_as

        kwargs: dict[str, Any] = {"name": name}
        if teammate_ids is not None:
            kwargs["teammate_ids"] = teammate_ids
        if is_public is not None:
            kwargs["is_public"] = is_public

        body = CreateTeamInbox(**kwargs)
        response = await create_team_inbox.asyncio_detailed(
            team_id=team_id, client=self._client, body=body
        )
        inbox = unwrap_as(response, InboxResponse)
        return Inbox.model_validate(inbox.to_dict())

    async def grant_access(
        self, inbox_id: str, *, teammate_ids: builtins.list[str]
    ) -> bool:
        """Grant inbox access to one or more teammates."""
        from frontapp_public_api_client.api.inboxes import add_inbox_access
        from frontapp_public_api_client.models.teammate_ids import TeammateIds
        from frontapp_public_api_client.utils import is_success

        body = TeammateIds(teammate_ids=teammate_ids)
        response = await add_inbox_access.asyncio_detailed(
            inbox_id=inbox_id, client=self._client, body=body
        )
        return is_success(response)

    async def revoke_access(
        self, inbox_id: str, *, teammate_ids: builtins.list[str]
    ) -> bool:
        """Revoke inbox access from one or more teammates.

        Wraps the awkwardly-named generated module ``removes_inbox_access``.
        """
        from frontapp_public_api_client.api.inboxes import removes_inbox_access
        from frontapp_public_api_client.models.teammate_ids import TeammateIds
        from frontapp_public_api_client.utils import is_success

        body = TeammateIds(teammate_ids=teammate_ids)
        response = await removes_inbox_access.asyncio_detailed(
            inbox_id=inbox_id, client=self._client, body=body
        )
        return is_success(response)


__all__ = ["Inboxes"]
