"""Domain model for Frontapp teammates.

Hand-written Pydantic projection of Front's ``TeammateResponse``.
Distinct from the lighter ``TeammateSummary`` in ``domain/conversation.py``,
which is a nested sub-type used inside ``Conversation.assignee`` and
exposes only id/username/email/name/availability. ``Teammate`` here is
the full standalone projection used by the teammates vertical
(``client.teammates``).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Teammate(BaseModel):
    """A Front teammate as returned by ``/teammates*`` endpoints.

    Teammate IDs are strings with a ``tea_`` prefix (e.g. ``tea_abc123``).
    ``is_available`` is the teammate's manual availability toggle (used by
    Front's "out of office" routing). ``is_blocked`` is set by an admin.
    """

    id: str
    email: str
    username: str
    first_name: str | None = None
    last_name: str | None = None
    is_admin: bool = False
    is_available: bool = True
    is_blocked: bool = False
    type: str | None = Field(None, description="'user' or 'integration'")

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="ignore",
        populate_by_name=True,
    )


__all__ = ["Teammate"]
