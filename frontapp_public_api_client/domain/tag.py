"""Domain model for Frontapp tags.

Hand-written Pydantic projection of Front's ``TagResponse``. Distinct from
the lighter ``TagSummary`` in ``domain/conversation.py``, which is a nested
sub-type used inside ``Conversation`` and only carries id/name/highlight/
is_private. ``Tag`` here is the full standalone shape used by the tags
vertical (``client.tags``).

Front returns ``created_at`` and ``updated_at`` as unix-seconds floats
(see ``TagResponse``); the validator below converts them to
timezone-aware ``datetime`` objects, mirroring ``Conversation``.
"""

from __future__ import annotations

from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from .conversation import _unix_to_datetime


class Tag(BaseModel):
    """A Front workspace tag as returned by ``/tags*`` endpoints.

    Tag IDs are strings with a ``tag_`` prefix (e.g. ``tag_abc123``).
    ``highlight`` is a color name (``red``, ``blue``, etc.) or ``None``.
    ``is_visible_in_conversation_lists`` controls whether the tag chip
    shows up on conversation list rows in Front's UI.
    """

    id: str
    name: str
    description: str | None = None
    highlight: str | None = Field(None, description="Color name, e.g. 'red'")
    is_private: bool = False
    is_visible_in_conversation_lists: bool = False
    created_at: AwareDatetime | None = None
    updated_at: AwareDatetime | None = None

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _parse_timestamp(cls, value: Any) -> Any:
        return _unix_to_datetime(value)


__all__ = ["Tag"]
