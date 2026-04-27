"""Domain model for Frontapp contact lists.

A contact list is a named bucket of contacts used for bulk operations
(broadcasts, segmentation, exports). Lists supersede the older Contact
Groups primitive (see ``ContactGroupRef`` in ``contact.py``); the two share
an identical wire shape (id + name + is_private), so this projection mirrors
that shape and the contact_groups vertical reuses ``ContactGroupRef``.
"""

from __future__ import annotations

from pydantic import Field

from .conversation import _Frozen


class ContactList(_Frozen):
    """A Front contact list — a named bucket of contacts.

    Contact lists support bulk membership operations (``add_contacts``,
    ``remove_contacts``) and three creation scopes (workspace, team,
    teammate). Front exposes no ``GET /contact_lists/{id}`` or PATCH
    endpoint, so there is no per-list detail fetch and lists can't be
    renamed once created.
    """

    id: str | None = Field(None, description="Contact list id, e.g. 'lst_abc123'")
    name: str | None = Field(None, description="Display name of the list")
    is_private: bool | None = Field(
        None,
        description=(
            "True for teammate-scoped private lists; False for "
            "workspace/team-shared lists"
        ),
    )


__all__ = ["ContactList"]
