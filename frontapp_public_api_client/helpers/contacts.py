"""Contacts helper facade — ergonomic wrappers around generated contact endpoints.

Exposes ``client.contacts`` covering three sibling generated tags:

- ``contacts/`` — list/get/create/update/delete + merge + team-/teammate-scoped
  create and list paths
- ``contact_handles/`` — add/remove a handle on a contact
- ``contact_notes/`` — list/add internal teammate notes on a contact

Patterns mirror ``helpers/conversations.py`` and ``helpers/drafts.py``: lazy
generated-module imports inside each method, ``unwrap_as`` / ``unwrap`` /
``is_success`` for response handling, ``Literal`` parameters for enum surfaces
that get converted internally to the generated ``StrEnum`` types.

Quirks worth knowing:

- The PATCH endpoint module is ``update_a_contact`` (with the ``_a_`` infix
  flagged in ``api-facts.yaml`` ``summary.module_name_quirks``); same for
  ``delete_a_contact``.
- The generated request model used by ``update_a_contact`` is named ``Contact``
  and is **narrower** than ``ContactResponse``: it lacks ``handles``,
  ``groups``/``lists``, and uses ``avatar: File`` instead of ``avatar_url``.
  Handle changes go through ``add_handle`` / ``delete_handle``.
- ``CreateContact.handles`` is required by Front (no default). ``create``,
  ``create_for_team``, and ``create_for_teammate`` all enforce this at the
  helper signature.
- ``CreateContactNote`` requires both ``author_id`` and ``body`` — Front
  needs explicit teammate attribution; there's no "default to token owner"
  fallback for notes.
- ``list_notes`` returns HTTP 202 (not 200). ``unwrap()`` dispatches on
  status, so it works, but anyone debugging an empty parsed body should
  check the status.
- ``search_by_email`` is a thin wrapper over ``list(q=email)`` — Front has
  no dedicated handle-resolve endpoint.
"""

from __future__ import annotations

import builtins
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Literal

from frontapp_public_api_client.helpers.base import Base

if TYPE_CHECKING:
    from frontapp_public_api_client.domain import Contact, ContactHandleSource


class Contacts(Base):
    """Ergonomic operations over Frontapp's contacts surface."""

    # -- reads --------------------------------------------------------------

    async def list(
        self,
        *,
        q: str | None = None,
        limit: int | None = None,
        page_token: str | None = None,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
    ) -> builtins.list[Contact]:
        """List contacts in the workspace.

        ``q`` is Front's contact-search syntax: a partial-match string that
        runs across handle values, names, and descriptions.
        """
        from frontapp_public_api_client.api.contacts import list_contacts
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.list_contacts_sort_order import (
            ListContactsSortOrder,
        )
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token
        if sort_by is not None:
            kwargs["sort_by"] = sort_by
        if sort_order is not None:
            kwargs["sort_order"] = ListContactsSortOrder(sort_order)

        response = await list_contacts.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Contact.model_validate(c.to_dict()) for c in results]

    async def iter_all(
        self,
        *,
        q: str | None = None,
        limit: int | None = None,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[Contact]:
        """Auto-paginated async iterator yielding every matching contact.

        See :meth:`list` for ``q`` / ``sort_*`` semantics. ``max_items``
        and ``max_pages`` are safety limits that stop iteration early
        without fetching further pages.
        """
        from frontapp_public_api_client.api.contacts import list_contacts
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.list_contacts_sort_order import (
            ListContactsSortOrder,
        )

        kwargs: dict[str, Any] = {}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit
        if sort_by is not None:
            kwargs["sort_by"] = sort_by
        if sort_order is not None:
            kwargs["sort_order"] = ListContactsSortOrder(sort_order)

        async for item in self._paginate(
            list_contacts.asyncio_detailed,
            projector=lambda c: Contact.model_validate(c.to_dict()),
            max_items=max_items,
            max_pages=max_pages,
            **kwargs,
        ):
            yield item

    async def search_by_email(self, email: str) -> builtins.list[Contact]:
        """Best-effort lookup of contacts by email.

        Wraps ``list(q=email)``. Front matches against handle values, so a
        contact whose email differs from the query (alias, partial match)
        may be missed. The result is a list — Front may return zero, one,
        or many contacts.
        """
        return await self.list(q=email)

    async def get(self, contact_id: str) -> Contact:
        """Fetch one contact by id (e.g. ``"crd_abc123"``)."""
        from frontapp_public_api_client.api.contacts import get_contact
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.contact_response import (
            ContactResponse,
        )
        from frontapp_public_api_client.utils import unwrap_as

        response = await get_contact.asyncio_detailed(
            contact_id=contact_id, client=self._client
        )
        contact = unwrap_as(response, ContactResponse)
        return Contact.model_validate(contact.to_dict())

    async def list_for_team(
        self,
        team_id: str,
        *,
        q: str | None = None,
        limit: int | None = None,
        page_token: str | None = None,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
    ) -> builtins.list[Contact]:
        """List contacts owned by a team (``team_id`` like ``"tim_abc"``)."""
        from frontapp_public_api_client.api.contacts import list_team_contacts
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.list_team_contacts_sort_order import (
            ListTeamContactsSortOrder,
        )
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "team_id": team_id}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token
        if sort_by is not None:
            kwargs["sort_by"] = sort_by
        if sort_order is not None:
            kwargs["sort_order"] = ListTeamContactsSortOrder(sort_order)

        response = await list_team_contacts.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Contact.model_validate(c.to_dict()) for c in results]

    async def list_for_teammate(
        self,
        teammate_id: str,
        *,
        q: str | None = None,
        limit: int | None = None,
        page_token: str | None = None,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
    ) -> builtins.list[Contact]:
        """List contacts owned by a single teammate (``"tea_abc"``)."""
        from frontapp_public_api_client.api.contacts import list_teammate_contacts
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.list_teammate_contacts_sort_order import (
            ListTeammateContactsSortOrder,
        )
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "teammate_id": teammate_id}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token
        if sort_by is not None:
            kwargs["sort_by"] = sort_by
        if sort_order is not None:
            kwargs["sort_order"] = ListTeammateContactsSortOrder(sort_order)

        response = await list_teammate_contacts.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Contact.model_validate(c.to_dict()) for c in results]

    async def list_conversations(
        self,
        contact_id: str,
        *,
        q: str | None = None,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Any]:
        """List conversations involving this contact. Returns raw attrs models."""
        from frontapp_public_api_client.api.contacts import list_contact_conversations
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "contact_id": contact_id}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_contact_conversations.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def list_notes(self, contact_id: str) -> builtins.list[Any]:
        """List internal teammate notes on a contact.

        Returns raw attrs ``ContactNoteResponses`` items. The endpoint
        responds with HTTP 202 (not 200) on success — ``unwrap()`` handles
        this via status-code dispatch.
        """
        from frontapp_public_api_client.api.contact_notes import list_notes
        from frontapp_public_api_client.utils import unwrap

        response = await list_notes.asyncio_detailed(
            contact_id=contact_id, client=self._client
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    # -- mutations ----------------------------------------------------------

    async def create(
        self,
        *,
        handles: builtins.list[Any],
        name: str | None = None,
        description: str | None = None,
        links: builtins.list[str] | None = None,
        group_names: builtins.list[str] | None = None,
        list_names: builtins.list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Contact:
        """Create a new workspace-scoped contact.

        ``handles`` is required by Front. Each item must be one of:

        - a ``(handle, source)`` tuple — e.g. ``("a@example.com", "email")``
        - a dict — e.g. ``{"handle": "a@example.com", "source": "email"}``
        - a generated ``models.contact_handle.ContactHandle`` instance

        ``source`` is one of ``email``, ``phone``, ``custom``, ``facebook``,
        ``front_chat``, ``intercom``, ``twitter``.

        Typed loosely as ``list[Any]`` because the runtime accepts three
        polymorphic shapes (validated in ``_to_handle_models``); a structural
        type would have been ``tuple | dict | ContactHandle`` but that's not
        useful for callers who just want IDE autocomplete.
        """
        from frontapp_public_api_client.api.contacts import create_contact
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.contact_response import ContactResponse
        from frontapp_public_api_client.models.create_contact import CreateContact
        from frontapp_public_api_client.utils import unwrap_as

        body = CreateContact(
            handles=_to_handle_models(handles),
            **_optional_contact_fields(
                name=name,
                description=description,
                links=links,
                group_names=group_names,
                list_names=list_names,
                custom_fields=custom_fields,
            ),
        )
        response = await create_contact.asyncio_detailed(client=self._client, body=body)
        contact = unwrap_as(response, ContactResponse)
        return Contact.model_validate(contact.to_dict())

    async def create_for_team(
        self,
        team_id: str,
        *,
        handles: builtins.list[Any],
        name: str | None = None,
        description: str | None = None,
        links: builtins.list[str] | None = None,
        group_names: builtins.list[str] | None = None,
        list_names: builtins.list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Contact:
        """Create a contact owned by a team (``"tim_abc"``)."""
        from frontapp_public_api_client.api.contacts import create_team_contact
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.contact_response import ContactResponse
        from frontapp_public_api_client.models.create_contact import CreateContact
        from frontapp_public_api_client.utils import unwrap_as

        body = CreateContact(
            handles=_to_handle_models(handles),
            **_optional_contact_fields(
                name=name,
                description=description,
                links=links,
                group_names=group_names,
                list_names=list_names,
                custom_fields=custom_fields,
            ),
        )
        response = await create_team_contact.asyncio_detailed(
            team_id=team_id, client=self._client, body=body
        )
        contact = unwrap_as(response, ContactResponse)
        return Contact.model_validate(contact.to_dict())

    async def create_for_teammate(
        self,
        teammate_id: str,
        *,
        handles: builtins.list[Any],
        name: str | None = None,
        description: str | None = None,
        links: builtins.list[str] | None = None,
        group_names: builtins.list[str] | None = None,
        list_names: builtins.list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Contact:
        """Create a contact owned by a teammate (``"tea_abc"``)."""
        from frontapp_public_api_client.api.contacts import create_teammate_contact
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.contact_response import ContactResponse
        from frontapp_public_api_client.models.create_contact import CreateContact
        from frontapp_public_api_client.utils import unwrap_as

        body = CreateContact(
            handles=_to_handle_models(handles),
            **_optional_contact_fields(
                name=name,
                description=description,
                links=links,
                group_names=group_names,
                list_names=list_names,
                custom_fields=custom_fields,
            ),
        )
        response = await create_teammate_contact.asyncio_detailed(
            teammate_id=teammate_id, client=self._client, body=body
        )
        contact = unwrap_as(response, ContactResponse)
        return Contact.model_validate(contact.to_dict())

    async def update(
        self,
        contact_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        links: builtins.list[str] | None = None,
        group_names: builtins.list[str] | None = None,
        list_names: builtins.list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> bool:
        """Update a contact's mutable scalar fields.

        Note: ``handles`` are NOT in this signature — Front's PATCH body
        (``Contact``, not ``ContactResponse``) doesn't accept handles. Use
        ``add_handle`` / ``delete_handle`` to manage them.
        """
        from frontapp_public_api_client.api.contacts import update_a_contact
        from frontapp_public_api_client.models.contact import Contact as ContactRequest
        from frontapp_public_api_client.utils import is_success

        body = ContactRequest(
            **_optional_contact_fields(
                name=name,
                description=description,
                links=links,
                group_names=group_names,
                list_names=list_names,
                custom_fields=custom_fields,
            )
        )
        response = await update_a_contact.asyncio_detailed(
            contact_id=contact_id, client=self._client, body=body
        )
        return is_success(response)

    async def delete(self, contact_id: str) -> bool:
        """Permanently delete a contact (204 No Content on success).

        Destructive: Front does not preserve the contact's handles, notes,
        or group memberships. Use with two-step confirm at the MCP layer.
        """
        from frontapp_public_api_client.api.contacts import delete_a_contact
        from frontapp_public_api_client.utils import is_success

        response = await delete_a_contact.asyncio_detailed(
            contact_id=contact_id, client=self._client
        )
        return is_success(response)

    async def merge(
        self,
        *,
        contact_ids: builtins.list[str],
        target_contact_id: str | None = None,
    ) -> Contact:
        """Merge multiple contacts into one. Irreversible.

        All conversations from the non-target contacts move to the target.
        If ``target_contact_id`` is omitted, Front picks the merge target.
        """
        from frontapp_public_api_client.api.contacts import merge_contacts
        from frontapp_public_api_client.domain import Contact
        from frontapp_public_api_client.models.contact_response import ContactResponse
        from frontapp_public_api_client.models.merge_contacts import MergeContacts
        from frontapp_public_api_client.utils import unwrap_as

        kwargs: dict[str, Any] = {"contact_ids": contact_ids}
        if target_contact_id is not None:
            kwargs["target_contact_id"] = target_contact_id

        body = MergeContacts(**kwargs)
        response = await merge_contacts.asyncio_detailed(client=self._client, body=body)
        contact = unwrap_as(response, ContactResponse)
        return Contact.model_validate(contact.to_dict())

    async def add_note(
        self,
        contact_id: str,
        *,
        body: str,
        author_id: str,
    ) -> Any:
        """Add an internal teammate note to a contact.

        ``author_id`` is required (Front needs explicit attribution).
        Returns the raw response — Front replies with the note id and body.
        """
        from frontapp_public_api_client.api.contact_notes import add_note
        from frontapp_public_api_client.models.create_contact_note import (
            CreateContactNote,
        )

        note = CreateContactNote(author_id=author_id, body=body)
        return await add_note.asyncio_detailed(
            contact_id=contact_id, client=self._client, body=note
        )

    async def add_handle(
        self,
        contact_id: str,
        *,
        handle: str,
        source: ContactHandleSource,
    ) -> bool:
        """Add a handle (email/phone/etc.) to an existing contact."""
        from frontapp_public_api_client.api.contact_handles import add_contact_handle
        from frontapp_public_api_client.models.contact_handle import ContactHandle
        from frontapp_public_api_client.models.contact_handle_source import (
            ContactHandleSource as _ContactHandleSource,
        )
        from frontapp_public_api_client.utils import is_success

        new_handle = ContactHandle(handle=handle, source=_ContactHandleSource(source))
        response = await add_contact_handle.asyncio_detailed(
            contact_id=contact_id, client=self._client, body=new_handle
        )
        return is_success(response)

    async def delete_handle(
        self,
        contact_id: str,
        *,
        handle: str,
        source: ContactHandleSource,
        force: bool | None = None,
    ) -> bool:
        """Remove a handle from a contact.

        ``force=True`` allows deleting the contact's last handle (would
        otherwise leave it unreachable).
        """
        from frontapp_public_api_client.api.contact_handles import (
            delete_contact_handle,
        )
        from frontapp_public_api_client.models.contact_handle_source import (
            ContactHandleSource as _ContactHandleSource,
        )
        from frontapp_public_api_client.models.delete_contact_handle import (
            DeleteContactHandle,
        )
        from frontapp_public_api_client.utils import is_success

        kwargs: dict[str, Any] = {
            "handle": handle,
            "source": _ContactHandleSource(source),
        }
        if force is not None:
            kwargs["force"] = force

        body = DeleteContactHandle(**kwargs)
        response = await delete_contact_handle.asyncio_detailed(
            contact_id=contact_id, client=self._client, body=body
        )
        return is_success(response)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _to_handle_models(handles: Any) -> Any:
    """Coerce an iterable of (handle, source) / dict / ContactHandle items
    into a list of generated ``ContactHandle`` instances."""
    from frontapp_public_api_client.models.contact_handle import ContactHandle
    from frontapp_public_api_client.models.contact_handle_source import (
        ContactHandleSource,
    )

    out: list[ContactHandle] = []
    for h in handles:
        if isinstance(h, ContactHandle):
            out.append(h)
        elif isinstance(h, dict):
            out.append(
                ContactHandle(
                    handle=h["handle"], source=ContactHandleSource(h["source"])
                )
            )
        elif isinstance(h, tuple) and len(h) == 2:
            out.append(ContactHandle(handle=h[0], source=ContactHandleSource(h[1])))
        else:
            raise TypeError(
                "Each handle must be a ContactHandle, a dict with 'handle' and "
                f"'source' keys, or a (handle, source) tuple; got {type(h).__name__}"
            )
    return out


def _optional_contact_fields(
    *,
    name: str | None = None,
    description: str | None = None,
    links: list[str] | None = None,
    group_names: list[str] | None = None,
    list_names: list[str] | None = None,
    custom_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the kwargs dict for the optional fields shared between
    ``CreateContact`` and ``Contact`` (the request).

    Both attrs models have the same optional-field shape: ``name``,
    ``description``, ``links``, ``group_names``, ``list_names``,
    ``custom_fields``. We omit anything the caller didn't pass so the
    generated ``UNSET`` defaults apply.
    """
    out: dict[str, Any] = {}
    if name is not None:
        out["name"] = name
    if description is not None:
        out["description"] = description
    if links is not None:
        out["links"] = links
    if group_names is not None:
        out["group_names"] = group_names
    if list_names is not None:
        out["list_names"] = list_names
    if custom_fields is not None:
        out["custom_fields"] = custom_fields
    return out


__all__ = ["Contacts"]
