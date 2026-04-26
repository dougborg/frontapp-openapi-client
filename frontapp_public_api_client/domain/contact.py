"""Domain models for Frontapp contacts.

A contact is a person/entity Front knows about — identified by one or more
handles (email, phone, Twitter, Facebook, custom). The same person reaching
your team via three channels appears as one contact with three handles.

Front exposes contacts on three sibling generated tags:

- ``contacts/`` — CRUD on the contact itself, including ``merge`` and the
  team-/teammate-scoped create/list paths.
- ``contact_handles/`` — add and remove handles from a contact.
- ``contact_notes/`` — internal teammate notes attached to a contact.

This domain module projects ``ContactResponse`` (and the smaller note shape)
into Pydantic models. The ``Contact`` (request) model used by
``update_a_contact`` is intentionally narrower than ``ContactResponse`` and is
not surfaced at the domain layer; callers go through the helper.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from .conversation import TeammateSummary, _Frozen, _unix_to_datetime

ContactHandleSource = Literal[
    "custom", "email", "facebook", "front_chat", "intercom", "phone", "twitter"
]


class ContactHandle(_Frozen):
    """One way to reach a contact — email, phone, social handle, etc.

    A contact can have multiple handles; ``handle`` is the literal value
    (``"a@example.com"``, ``"+15551234"``) and ``source`` is the channel.
    """

    handle: str
    source: ContactHandleSource


class ContactGroupRef(_Frozen):
    """Subset of Front's ``ContactListResponses`` schema used for the
    ``groups`` and ``lists`` arrays on a contact."""

    id: str | None = Field(None, description="Group/list id, e.g. 'grp_abc123'")
    name: str | None = None
    is_private: bool | None = None


class ContactNote(_Frozen):
    """Internal teammate note on a contact (never visible to the customer)."""

    id: str | None = Field(None, description="Note id")
    body: str | None = None
    author: TeammateSummary | None = None
    created_at: AwareDatetime | None = None

    @field_validator("created_at", mode="before")
    @classmethod
    def _parse_timestamp(cls, value: Any) -> Any:
        return _unix_to_datetime(value)


class Contact(BaseModel):
    """A Front contact as returned by ``/contacts`` endpoints.

    Front contact ids are strings with a ``crd_`` prefix.
    """

    id: str
    name: str | None = None
    description: str | None = None
    avatar_url: str | None = None
    links: list[str] = Field(default_factory=list)
    handles: list[ContactHandle] = Field(default_factory=list)
    groups: list[ContactGroupRef] = Field(default_factory=list)
    lists: list[ContactGroupRef] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_private: bool | None = None

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="ignore",
    )


__all__ = [
    "Contact",
    "ContactGroupRef",
    "ContactHandle",
    "ContactHandleSource",
    "ContactNote",
]
