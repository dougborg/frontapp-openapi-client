"""Domain model for Frontapp inboxes.

Hand-written Pydantic projection of Front's ``InboxResponse``. Inboxes are
workspace-level reference data — there are no timestamp fields and no
mutable shape beyond name + visibility, so the projection is intentionally
thin.

Note: every field on the generated ``InboxResponse`` is ``UNSET`` by
default, so the projection here marks them all as optional even though
``id`` and ``name`` are typically present in real responses.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Inbox(BaseModel):
    """A Front inbox (channel container) as returned by ``/inboxes*`` endpoints.

    Inbox IDs are strings with an ``inb_`` prefix (e.g. ``inb_abc123``).
    ``is_private`` and ``is_public`` are independent flags Front uses to
    model visibility — not strict mutual opposites.
    """

    id: str | None = Field(None, description="Inbox id, e.g. 'inb_abc123'")
    name: str | None = None
    is_private: bool | None = None
    is_public: bool | None = None

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="ignore",
    )


__all__ = ["Inbox"]
