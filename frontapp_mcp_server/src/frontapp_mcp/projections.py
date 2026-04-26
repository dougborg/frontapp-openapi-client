"""Shared response projections used by MCP tools and resources.

When a tool returns a list of conversations and a reference resource also
exposes recent conversations, both paths want the same compact, LLM-friendly
shape. Defining the projection here lets the two surfaces share the schema
without one importing private symbols from the other.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from frontapp_public_api_client.domain import Contact, Conversation, Draft, Inbox, Tag


class ConversationSummary(BaseModel):
    """Compact projection of a conversation for LLM responses.

    The full ``Conversation`` domain model carries more structure than is
    useful to an LLM on every list hit. Callers can still call
    ``get_conversation`` for full detail on a specific id.
    """

    id: str
    subject: str | None = None
    status: str | None = None
    assignee_name: str | None = None
    recipient: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_private: bool | None = None
    created_at: str | None = None
    updated_at: str | None = None
    waiting_since: str | None = None


def to_summary(conv: Conversation) -> ConversationSummary:
    """Project a ``Conversation`` domain model to a ``ConversationSummary``."""
    assignee_name: str | None = None
    if conv.assignee:
        parts = [conv.assignee.first_name, conv.assignee.last_name]
        assignee_name = " ".join(p for p in parts if p) or conv.assignee.username
    return ConversationSummary(
        id=conv.id,
        subject=conv.subject,
        status=conv.status,
        assignee_name=assignee_name,
        recipient=conv.recipient.handle if conv.recipient else None,
        tags=[t.name for t in conv.tags if t.name],
        is_private=conv.is_private,
        created_at=conv.created_at.isoformat() if conv.created_at else None,
        updated_at=conv.updated_at.isoformat() if conv.updated_at else None,
        waiting_since=conv.waiting_since.isoformat() if conv.waiting_since else None,
    )


class DraftSummary(BaseModel):
    """Compact projection of a draft for LLM responses.

    Strips the heavy ``MessageResponse`` shape down to what an LLM cares about
    when reviewing a draft it just created or edited: id, subject, body,
    recipient handles, version (for clobber-free re-edits), and timestamps.
    """

    id: str
    subject: str | None = None
    body: str | None = None
    blurb: str | None = None
    draft_mode: str | None = None
    error_type: str | None = None
    version: str | None = None
    author_name: str | None = None
    recipients: list[str] = Field(default_factory=list)
    attachment_filenames: list[str] = Field(default_factory=list)
    created_at: str | None = None


def to_draft_summary(draft: Draft) -> DraftSummary:
    """Project a ``Draft`` domain model to a ``DraftSummary``."""
    author_name: str | None = None
    if draft.author:
        parts = [draft.author.first_name, draft.author.last_name]
        author_name = " ".join(p for p in parts if p) or draft.author.username
    return DraftSummary(
        id=draft.id,
        subject=draft.subject,
        body=draft.body,
        blurb=draft.blurb,
        draft_mode=draft.draft_mode,
        error_type=draft.error_type,
        version=draft.version,
        author_name=author_name,
        recipients=[r.handle for r in draft.recipients if r.handle],
        attachment_filenames=[a.filename for a in draft.attachments if a.filename],
        created_at=draft.created_at.isoformat() if draft.created_at else None,
    )


class ContactSummary(BaseModel):
    """Compact projection of a contact for LLM responses.

    Surfaces the fields an agent actually uses when triaging or
    referencing a contact: id, display name, primary handles by source,
    and counts to avoid stuffing the full handles list into the LLM
    context.
    """

    id: str
    name: str | None = None
    description: str | None = None
    primary_email: str | None = None
    primary_phone: str | None = None
    handle_count: int = 0
    is_private: bool | None = None
    group_names: list[str] = Field(default_factory=list)


def _first_handle(contact: Contact, source: str) -> str | None:
    for h in contact.handles:
        if h.source == source:
            return h.handle
    return None


def to_contact_summary(contact: Contact) -> ContactSummary:
    """Project a ``Contact`` domain model to a ``ContactSummary``."""
    return ContactSummary(
        id=contact.id,
        name=contact.name,
        description=contact.description,
        primary_email=_first_handle(contact, "email"),
        primary_phone=_first_handle(contact, "phone"),
        handle_count=len(contact.handles),
        is_private=contact.is_private,
        group_names=[g.name for g in contact.groups if g.name],
    )


class TagCatalogSummary(BaseModel):
    """Compact projection of a workspace tag for LLM responses.

    Named to disambiguate from the conversation-nested ``TagSummary`` in
    ``frontapp_public_api_client.domain.conversation`` — that one only
    carries id/name/highlight/is_private. This catalog projection adds
    visibility flags + timestamps used by the tag management surface.
    """

    id: str
    name: str
    description: str | None = None
    highlight: str | None = None
    is_private: bool = False
    is_visible_in_conversation_lists: bool = False
    created_at: str | None = None
    updated_at: str | None = None


def to_tag_catalog_summary(tag: Tag) -> TagCatalogSummary:
    """Project a ``Tag`` domain model to a ``TagCatalogSummary``."""
    return TagCatalogSummary(
        id=tag.id,
        name=tag.name,
        description=tag.description,
        highlight=tag.highlight,
        is_private=tag.is_private,
        is_visible_in_conversation_lists=tag.is_visible_in_conversation_lists,
        created_at=tag.created_at.isoformat() if tag.created_at else None,
        updated_at=tag.updated_at.isoformat() if tag.updated_at else None,
    )


class InboxSummary(BaseModel):
    """Compact projection of an inbox for LLM responses.

    Inbox responses from Front are already thin (id, name, two visibility
    flags) so this projection is essentially a typed re-shape with
    consistent serialization.
    """

    id: str | None = None
    name: str | None = None
    is_private: bool | None = None
    is_public: bool | None = None


def to_inbox_summary(inbox: Inbox) -> InboxSummary:
    """Project an ``Inbox`` domain model to an ``InboxSummary``."""
    return InboxSummary(
        id=inbox.id,
        name=inbox.name,
        is_private=inbox.is_private,
        is_public=inbox.is_public,
    )


__all__ = [
    "ContactSummary",
    "ConversationSummary",
    "DraftSummary",
    "InboxSummary",
    "TagCatalogSummary",
    "to_contact_summary",
    "to_draft_summary",
    "to_inbox_summary",
    "to_summary",
    "to_tag_catalog_summary",
]
