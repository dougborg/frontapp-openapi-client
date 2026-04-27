"""Contact groups helper facade — ergonomic wrappers around generated contact-group endpoints.

**Front has deprecated this entire surface.** Every endpoint under
``/contact_groups*`` carries ``deprecated: true`` in the spec, with explicit
redirects to the equivalent ``/contact_lists*`` endpoint. This vertical
exists so workspaces still using groups can manage them programmatically;
new code should use ``client.contact_lists`` instead.

The shape mirrors ``client.contact_lists`` since groups and lists were
historically the same primitive — Front even reuses the same request body
models (``CreateContactList`` / ``AddContactsToList`` /
``RemoveContactsFromList``) for both. Same caveats apply:

- **No get-by-id, no update.** No way to rename a group once created.
- **``create()`` (workspace-scoped) silently targets the oldest active
  workspace** the API token has access to. Prefer ``create_for_team``.
- **``remove_contacts()`` is capped at 50 contact_ids per call** by Front's
  server-side validation.
- **All mutations return HTTP 204 No Content** — helpers return ``True``
  on success.
- **Domain shape is identical to contact_lists** — groups project to
  ``ContactGroupRef`` (in ``domain/contact.py``), lists project to the
  newer ``ContactList`` domain model. Both have the same field set
  (id + name + is_private); the projection class differs only because
  ``ContactGroupRef`` was already in the contacts vertical.
- **``list_members()`` returns ``Contact`` objects** via Front's standard
  ``listOfContacts`` response shape.
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
    from frontapp_public_api_client.domain import Contact, ContactGroupRef


class ContactGroups(Base):
    """Ergonomic operations over Frontapp's deprecated contact-group surface.

    Front has deprecated all contact-group endpoints in favor of contact
    lists; prefer ``client.contact_lists`` for new code.
    """

    # -- reads --------------------------------------------------------------

    async def list(self) -> builtins.list[ContactGroupRef]:
        """List all contact groups in the workspace.

        Returns a flat list across every scope (workspace, team, teammate)
        the API token has visibility into. For scope-specific listings use
        ``list_for_team`` / ``list_for_teammate``.
        """
        from frontapp_public_api_client.api.contact_groups import list_groups
        from frontapp_public_api_client.domain import ContactGroupRef
        from frontapp_public_api_client.utils import unwrap

        response = await list_groups.asyncio_detailed(client=self._client)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [ContactGroupRef.model_validate(item.to_dict()) for item in results]

    async def list_for_team(self, team_id: str) -> builtins.list[ContactGroupRef]:
        """List contact groups owned by a specific team."""
        from frontapp_public_api_client.api.contact_groups import list_team_groups
        from frontapp_public_api_client.domain import ContactGroupRef
        from frontapp_public_api_client.utils import unwrap

        response = await list_team_groups.asyncio_detailed(
            team_id=team_id, client=self._client
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [ContactGroupRef.model_validate(item.to_dict()) for item in results]

    async def list_for_teammate(
        self, teammate_id: str
    ) -> builtins.list[ContactGroupRef]:
        """List contact groups owned by a specific teammate (private groups)."""
        from frontapp_public_api_client.api.contact_groups import list_teammate_groups
        from frontapp_public_api_client.domain import ContactGroupRef
        from frontapp_public_api_client.utils import unwrap

        response = await list_teammate_groups.asyncio_detailed(
            teammate_id=teammate_id, client=self._client
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [ContactGroupRef.model_validate(item.to_dict()) for item in results]

    async def list_members(
        self,
        contact_group_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Contact]:
        """List the contacts that are members of a given group.

        Returns ``Contact`` objects (not ``ContactGroupRef``) — the
        endpoint reuses Front's standard ``listOfContacts`` shape.
        ``limit`` caps page size (max 100, default 50). For groups with
        many members use ``iter_members`` to walk pages automatically.
        """
        from frontapp_public_api_client.api.contact_groups import (
            list_contacts_in_group,
        )
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {
            "contact_group_id": contact_group_id,
            "client": self._client,
        }
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_contacts_in_group.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Contact.model_validate(item.to_dict()) for item in results]

    async def iter_members(
        self,
        contact_group_id: str,
        *,
        limit: int | None = None,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[Contact]:
        """Auto-paginated async iterator over every contact in a group."""
        from frontapp_public_api_client.api.contact_groups import (
            list_contacts_in_group,
        )
        from frontapp_public_api_client.domain import Contact

        kwargs: dict[str, Any] = {"contact_group_id": contact_group_id}
        if limit is not None:
            kwargs["limit"] = limit

        async for item in self._paginate(
            list_contacts_in_group.asyncio_detailed,
            projector=lambda c: Contact.model_validate(c.to_dict()),
            max_items=max_items,
            max_pages=max_pages,
            **kwargs,
        ):
            yield item

    # -- mutations (all return True on 204 No Content) --------------------

    async def create(self, name: str) -> bool:
        """Create a workspace-scoped contact group.

        Returns ``True`` on success (204 No Content). Per Front's spec this
        targets the oldest active workspace the token has access to —
        prefer ``create_for_team`` when you have a specific team. Front
        does not echo the new group's id; follow up with ``list()`` and
        match by name if you need it.
        """
        from frontapp_public_api_client.api.contact_groups import create_group
        from frontapp_public_api_client.models.create_contact_list import (
            CreateContactList,
        )
        from frontapp_public_api_client.utils import is_success

        response = await create_group.asyncio_detailed(
            client=self._client, body=CreateContactList(name=name)
        )
        return is_success(response)

    async def create_for_team(self, team_id: str, name: str) -> bool:
        """Create a team-scoped contact group. Returns ``True`` on success."""
        from frontapp_public_api_client.api.contact_groups import create_team_group
        from frontapp_public_api_client.models.create_contact_list import (
            CreateContactList,
        )
        from frontapp_public_api_client.utils import is_success

        response = await create_team_group.asyncio_detailed(
            team_id=team_id,
            client=self._client,
            body=CreateContactList(name=name),
        )
        return is_success(response)

    async def create_for_teammate(self, teammate_id: str, name: str) -> bool:
        """Create a teammate-scoped (private) contact group. Returns ``True`` on success."""
        from frontapp_public_api_client.api.contact_groups import create_teammate_group
        from frontapp_public_api_client.models.create_contact_list import (
            CreateContactList,
        )
        from frontapp_public_api_client.utils import is_success

        response = await create_teammate_group.asyncio_detailed(
            teammate_id=teammate_id,
            client=self._client,
            body=CreateContactList(name=name),
        )
        return is_success(response)

    async def delete(self, contact_group_id: str) -> bool:
        """Delete a contact group.

        Dissolves the group and all memberships. Front does **not** delete
        the underlying contacts. Returns ``True`` on success (204 No
        Content).
        """
        from frontapp_public_api_client.api.contact_groups import delete_group
        from frontapp_public_api_client.utils import is_success

        response = await delete_group.asyncio_detailed(
            contact_group_id=contact_group_id, client=self._client
        )
        return is_success(response)

    async def add_contacts(
        self, contact_group_id: str, contact_ids: builtins.list[str]
    ) -> bool:
        """Add contacts to a group (bulk).

        ``contact_ids`` accepts both ``crd_*`` ids and Front resource
        aliases (``alt:email:foo@example.com``). Returns ``True`` on
        success (204 No Content).
        """
        from frontapp_public_api_client.api.contact_groups import (
            add_contacts_to_group,
        )
        from frontapp_public_api_client.models.add_contacts_to_list import (
            AddContactsToList,
        )
        from frontapp_public_api_client.utils import is_success

        response = await add_contacts_to_group.asyncio_detailed(
            contact_group_id=contact_group_id,
            client=self._client,
            body=AddContactsToList(contact_ids=contact_ids),
        )
        return is_success(response)

    async def remove_contacts(
        self, contact_group_id: str, contact_ids: builtins.list[str]
    ) -> bool:
        """Remove contacts from a group (bulk).

        ``contact_ids`` accepts both ``crd_*`` ids and Front resource
        aliases (``alt:email:foo@example.com``) — same shape as
        ``add_contacts``. **Capped at 50 contact_ids per call** by Front's
        server-side validation. Returns ``True`` on success (204).
        """
        from frontapp_public_api_client.api.contact_groups import (
            remove_contacts_from_group,
        )
        from frontapp_public_api_client.models.remove_contacts_from_list import (
            RemoveContactsFromList,
        )
        from frontapp_public_api_client.utils import is_success

        check_list_size_cap(
            contact_ids, cap=CONTACT_BUCKET_REMOVE_CAP, operation="remove_contacts"
        )

        response = await remove_contacts_from_group.asyncio_detailed(
            contact_group_id=contact_group_id,
            client=self._client,
            body=RemoveContactsFromList(contact_ids=contact_ids),
        )
        return is_success(response)


__all__ = ["ContactGroups"]
