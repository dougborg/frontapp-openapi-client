"""Domain models for Frontapp conversations.

Hand-written Pydantic models for business logic, separate from the generated
attrs API models. Shapes mirror Front's ``ConversationResponse``,
``TeammateResponse``, ``TagResponse``, and ``RecipientResponse`` schemas.

Front returns timestamps as unix-seconds floats; the validators in this module
convert them to timezone-aware ``datetime`` objects for ergonomics.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


class _Frozen(BaseModel):
    """Immutable Pydantic base used for nested conversation sub-types."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="ignore",
    )


def _unix_to_datetime(value: Any) -> Any:
    """Convert a unix-seconds number to a UTC-aware datetime.

    Pass through ``None`` and already-parsed ``datetime`` values unchanged.
    """
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC)
    return value


class TeammateSummary(_Frozen):
    """Partial representation of a teammate assigned to or authoring on a
    conversation. Matches Front's ``TeammateResponse`` schema (subset)."""

    id: str | None = Field(None, description="Teammate id, e.g. 'tea_abc123'")
    email: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_admin: bool | None = None
    is_available: bool | None = None


class TagSummary(_Frozen):
    """A tag attached to a conversation. Subset of Front's ``TagResponse``."""

    id: str | None = Field(None, description="Tag id, e.g. 'tag_abc123'")
    name: str | None = None
    highlight: str | None = Field(None, description="Color name, e.g. 'red'")
    is_private: bool | None = None


class RecipientSummary(_Frozen):
    """Main recipient of a conversation (email, handle, or role)."""

    name: str | None = None
    handle: str | None = Field(None, description="Email address or channel handle")
    role: str | None = Field(None, description="'to', 'cc', 'bcc', or 'from'")


class Conversation(BaseModel):
    """A Front conversation as returned by ``/conversations`` or
    ``/conversations/{id}``.

    Front's conversation IDs are strings with a ``cnv_`` prefix (e.g.
    ``cnv_abc123``). Status values are ``open``, ``archived``, ``deleted``,
    ``spam``, or ticketing-specific categories.
    """

    id: str
    subject: str | None = Field(None, description="Conversation subject")
    status: str | None = Field(
        None, description="'open', 'archived', 'deleted', 'spam', or a ticket status"
    )
    status_category: str | None = Field(
        None, description="Status category when ticketing is enabled"
    )
    status_id: str | None = None
    assignee: TeammateSummary | None = None
    recipient: RecipientSummary | None = None
    tags: list[TagSummary] = Field(default_factory=list)
    ticket_ids: list[str] = Field(default_factory=list)
    is_private: bool | None = None
    created_at: AwareDatetime | None = None
    updated_at: AwareDatetime | None = None
    waiting_since: AwareDatetime | None = Field(
        None, description="Timestamp of the oldest unreplied message"
    )

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    @field_validator("created_at", "updated_at", "waiting_since", mode="before")
    @classmethod
    def _parse_timestamp(cls, value: Any) -> Any:
        return _unix_to_datetime(value)


class ConversationPageCursor(_Frozen):
    """Cursor returned alongside a page of conversations.

    Front paginates via a cursor token embedded in the next URL; consumers
    pass ``page_token`` back to the list endpoint to fetch subsequent pages.
    """

    next_url: str | None = Field(
        None, description="Full URL for the next page, or None if last page"
    )
    next_page_token: str | None = Field(
        None,
        description="Extracted page_token query param from next_url, or None",
    )


__all__ = [
    "Conversation",
    "ConversationPageCursor",
    "RecipientSummary",
    "TagSummary",
    "TeammateSummary",
]
