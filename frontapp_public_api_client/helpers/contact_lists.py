"""Contact lists helper facade — ergonomic wrappers around generated contact-list endpoints.

Exposes ``client.contact_lists`` covering the workspace / team / teammate
list catalog plus member listing and bulk membership mutations.

Quirks worth knowing:

- **No get-by-id, no update.** Front's spec does not expose
  ``GET /contact_lists/{id}`` or ``PATCH``; lists can't be renamed once
  created. The helper has list / list-by-scope / list_members / create /
  delete / add_contacts / remove_contacts only.
- **``create()`` (workspace-scoped) silently targets the oldest active
  workspace** the API token has access to (Front's spec note). Prefer
  ``create_for_team(team_id, name)`` when you have a specific team.
- **``remove_contacts()`` is capped at 50 contact_ids per call** by Front's
  server-side validation (``RemoveContactsFromList.maxItems``). Larger
  removals must be batched manually; the helper does no automatic
  splitting.
- **Membership operations accept resource aliases** (e.g.
  ``alt:email:foo@x.com``) in place of contact ids — Front resolves them
  server-side.
- **All mutations return HTTP 204 No Content.** Helper methods return
  ``True`` on success via ``is_success(response)``.
- **``list_members()`` returns ``Contact`` objects**, not ``ContactList``
  — the underlying ``list_contacts_in_contact_list`` endpoint reuses the
  same ``listOfContacts`` response shape as ``contacts.list``.
"""

from __future__ import annotations

import builtins
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from frontapp_public_api_client.helpers.base import Base
from frontapp_public_api_client.helpers.constants import (
    CONTACT_BUCKET_REMOVE_CAP,
    check_list_size_cap,
)

if TYPE_CHECKING:
    from frontapp_public_api_client.domain import Contact, ContactList


class ContactLists(Base):
    """Ergonomic operations over Frontapp's contact-list surface."""

    # -- reads --------------------------------------------------------------

    async def list(self) -> builtins.list[ContactList]:
        """List all contact lists in the workspace.

        Returns lists from every scope (workspace, team, teammate) the API
        token has visibility into. For scope-specific listings use
        ``list_for_team`` / ``list_for_teammate``.
        """
        from frontapp_public_api_client.api.contact_lists import list_contact_lists
        from frontapp_public_api_client.domain import ContactList
        from frontapp_public_api_client.utils import unwrap

        response = await list_contact_lists.asyncio_detailed(client=self._client)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [ContactList.model_validate(item.to_dict()) for item in results]

    async def list_for_team(self, team_id: str) -> builtins.list[ContactList]:
        """List contact lists owned by a specific team."""
        from frontapp_public_api_client.api.contact_lists import (
            list_team_contact_lists,
        )
        from frontapp_public_api_client.domain import ContactList
        from frontapp_public_api_client.utils import unwrap

        response = await list_team_contact_lists.asyncio_detailed(
            team_id=team_id, client=self._client
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [ContactList.model_validate(item.to_dict()) for item in results]

    async def list_for_teammate(self, teammate_id: str) -> builtins.list[ContactList]:
        """List contact lists owned by a specific teammate (private lists)."""
        from frontapp_public_api_client.api.contact_lists import (
            list_teammate_contact_lists,
        )
        from frontapp_public_api_client.domain import ContactList
        from frontapp_public_api_client.utils import unwrap

        response = await list_teammate_contact_lists.asyncio_detailed(
            teammate_id=teammate_id, client=self._client
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [ContactList.model_validate(item.to_dict()) for item in results]

    async def list_members(
        self,
        contact_list_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Contact]:
        """List the contacts that are members of a given list.

        Returns ``Contact`` objects (not ``ContactList``) — the endpoint
        reuses Front's standard ``listOfContacts`` response shape.

        ``limit`` caps page size (max 100, default 50). For lists with
        many members use ``iter_members`` to walk pages automatically.
        """
        from frontapp_public_api_client.api.contact_lists import (
            list_contacts_in_contact_list,
        )
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {
            "contact_list_id": contact_list_id,
            "client": self._client,
        }
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_contacts_in_contact_list.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Contact.model_validate(item.to_dict()) for item in results]

    async def iter_members(
        self,
        contact_list_id: str,
        *,
        limit: int | None = None,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[Contact]:
        """Auto-paginated async iterator over every contact in a list.

        Use this when iterating every member — the cursor plumbing is
        hidden, and ``max_items`` / ``max_pages`` cap the walk to avoid
        unbounded fetches on enormous lists.
        """
        from frontapp_public_api_client.api.contact_lists import (
            list_contacts_in_contact_list,
        )
        from frontapp_public_api_client.domain import Contact

        kwargs: dict[str, Any] = {"contact_list_id": contact_list_id}
        if limit is not None:
            kwargs["limit"] = limit

        async for item in self._paginate(
            list_contacts_in_contact_list.asyncio_detailed,
            projector=lambda c: Contact.model_validate(c.to_dict()),
            max_items=max_items,
            max_pages=max_pages,
            **kwargs,
        ):
            yield item

    # -- mutations (all return True on 204 No Content) --------------------

    async def create(self, name: str) -> bool:
        """Create a workspace-scoped contact list.

        Returns ``True`` on success (204 No Content). Front does not echo
        the new list's id, so callers that need it must follow up with
        ``list()`` and match by name. Per Front's spec note this targets
        the oldest active workspace the token has access to — prefer
        ``create_for_team`` when you have a specific team.
        """
        from frontapp_public_api_client.api.contact_lists import create_contact_list
        from frontapp_public_api_client.models.create_contact_list import (
            CreateContactList,
        )
        from frontapp_public_api_client.utils import is_success

        response = await create_contact_list.asyncio_detailed(
            client=self._client, body=CreateContactList(name=name)
        )
        return is_success(response)

    async def create_for_team(self, team_id: str, name: str) -> bool:
        """Create a team-scoped contact list. Returns ``True`` on success."""
        from frontapp_public_api_client.api.contact_lists import (
            create_team_contact_list,
        )
        from frontapp_public_api_client.models.create_contact_list import (
            CreateContactList,
        )
        from frontapp_public_api_client.utils import is_success

        response = await create_team_contact_list.asyncio_detailed(
            team_id=team_id, client=self._client, body=CreateContactList(name=name)
        )
        return is_success(response)

    async def create_for_teammate(self, teammate_id: str, name: str) -> bool:
        """Create a teammate-scoped (private) contact list. Returns ``True`` on success."""
        from frontapp_public_api_client.api.contact_lists import (
            create_teammate_contact_list,
        )
        from frontapp_public_api_client.models.create_contact_list import (
            CreateContactList,
        )
        from frontapp_public_api_client.utils import is_success

        response = await create_teammate_contact_list.asyncio_detailed(
            teammate_id=teammate_id,
            client=self._client,
            body=CreateContactList(name=name),
        )
        return is_success(response)

    async def delete(self, contact_list_id: str) -> bool:
        """Delete a contact list.

        Dissolves the list and all memberships. Front does **not** delete
        the underlying contacts — they remain in the workspace. Returns
        ``True`` on success (204 No Content).
        """
        from frontapp_public_api_client.api.contact_lists import delete_contact_list
        from frontapp_public_api_client.utils import is_success

        response = await delete_contact_list.asyncio_detailed(
            contact_list_id=contact_list_id, client=self._client
        )
        return is_success(response)

    async def add_contacts(
        self, contact_list_id: str, contact_ids: builtins.list[str]
    ) -> bool:
        """Add contacts to a list (bulk).

        ``contact_ids`` accepts both ``crd_*`` ids and Front resource
        aliases (``alt:email:foo@example.com``, ``alt:phone:+15555550100``).
        Returns ``True`` on success (204 No Content). No documented per-
        call cap on add operations.
        """
        from frontapp_public_api_client.api.contact_lists import (
            add_contacts_to_contact_list,
        )
        from frontapp_public_api_client.models.add_contacts_to_list import (
            AddContactsToList,
        )
        from frontapp_public_api_client.utils import is_success

        response = await add_contacts_to_contact_list.asyncio_detailed(
            contact_list_id=contact_list_id,
            client=self._client,
            body=AddContactsToList(contact_ids=contact_ids),
        )
        return is_success(response)

    async def remove_contacts(
        self, contact_list_id: str, contact_ids: builtins.list[str]
    ) -> bool:
        """Remove contacts from a list (bulk).

        ``contact_ids`` accepts both ``crd_*`` ids and Front resource
        aliases (``alt:email:foo@example.com``) — same shape as
        ``add_contacts``. **Capped at 50 contact_ids per call** by Front's
        server-side validation. Larger removals must be batched by the
        caller — the helper does not auto-split. Returns ``True`` on
        success (204).
        """
        from frontapp_public_api_client.api.contact_lists import (
            remove_contacts_from_contact_list,
        )
        from frontapp_public_api_client.models.remove_contacts_from_list import (
            RemoveContactsFromList,
        )
        from frontapp_public_api_client.utils import is_success

        check_list_size_cap(
            contact_ids, cap=CONTACT_BUCKET_REMOVE_CAP, operation="remove_contacts"
        )

        response = await remove_contacts_from_contact_list.asyncio_detailed(
            contact_list_id=contact_list_id,
            client=self._client,
            body=RemoveContactsFromList(contact_ids=contact_ids),
        )
        return is_success(response)


__all__ = ["ContactLists"]
