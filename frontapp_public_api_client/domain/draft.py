"""Domain model for Frontapp drafts.

A draft is an unsent message in Front (``msg_`` or ``dft_`` prefixed id). Drafts
are the safe-by-default outbound path: an agent creates a draft, the human
reviews it in Front's UI, and the human clicks send. There is no programmatic
``send_draft`` endpoint in Front's spec — sending is always human-in-the-loop.

The ``Draft`` projection mirrors Front's ``MessageResponse`` (the same shape
``create_draft`` and ``edit_draft`` return), reusing ``TeammateSummary`` and
``RecipientSummary`` from the conversations domain.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from .conversation import RecipientSummary, TeammateSummary, _Frozen, _unix_to_datetime


class AttachmentSummary(_Frozen):
    """Subset of Front's ``Attachment`` schema surfaced on a Draft.

    Drafts created without attachments expose an empty list. The actual upload
    mechanism is unresolved upstream and tracked in #12; for now, drafts can
    reference attachments that were uploaded through the Front UI.
    """

    id: str | None = Field(None, description="Attachment id, e.g. 'fil_abc123'")
    filename: str | None = None
    url: str | None = None
    content_type: str | None = None
    size: int | None = None


class Draft(BaseModel):
    """A Front draft message returned by ``create_draft`` / ``edit_draft``.

    Front returns the full ``MessageResponse`` shape; this projection keeps
    the fields callers actually use. ``draft_mode`` is one of ``'private'``
    (visible to the author only) or ``'shared'`` (visible to all teammates
    with access to the conversation).
    """

    id: str
    message_uid: str | None = Field(
        None, description="Front's secondary message UID for idempotency / dedup"
    )
    type_: str | None = Field(None, alias="type")
    is_inbound: bool | None = None
    draft_mode: Literal["private", "shared"] | None = None
    error_type: str | None = Field(
        None,
        description="Populated when a previous send attempt failed (e.g. 'no_inbox')",
    )
    version: str | None = Field(
        None,
        description="Opaque version token; pass to edit_draft to avoid clobbering",
    )
    created_at: AwareDatetime | None = None
    subject: str | None = None
    blurb: str | None = Field(None, description="Plaintext preview of the body")
    body: str | None = None
    text: str | None = None
    author: TeammateSummary | None = None
    recipients: list[RecipientSummary] = Field(default_factory=list)
    attachments: list[AttachmentSummary] = Field(default_factory=list)

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("created_at", mode="before")
    @classmethod
    def _parse_timestamp(cls, value: Any) -> Any:
        return _unix_to_datetime(value)


__all__ = ["AttachmentSummary", "Draft"]
