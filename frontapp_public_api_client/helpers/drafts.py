"""Drafts helper facade — ergonomic wrappers around generated draft endpoints.

Exposes ``client.drafts.{list_for_conversation, create_on_channel, create_reply,
edit, delete}`` with domain-model returns where Front returns a body. Drafts are
the safe-by-default outbound path: an agent creates a draft, the human reviews
it in Front's UI, and the human clicks send. There is no programmatic
``send_draft`` endpoint — sending is always human-in-the-loop.

Notes:

- ``edit`` and ``create_reply`` build ``EditDraft`` / ``ReplyDraft`` models which
  require both ``body`` AND ``channel_id``. Front treats PATCH /drafts/{id}/ as a
  full replacement, so callers must re-supply the body even when only changing
  metadata.
- ``list_for_conversation`` returns raw attrs ``MessageResponse`` items pulled
  out of the standard ``field_results`` wrapper of
  ``ListConversationDraftsResponse200`` — same shape as every other Front
  list endpoint.
- ``attachments`` accepts ``list[FileSpec]`` on every mutation helper. When
  provided, the helper bypasses the generated client and sends the request
  as ``multipart/form-data`` (the generated client serializes these endpoints
  as ``application/json``, which Front rejects for binary content). When
  ``attachments`` is ``None`` or empty, the standard generated path is used.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any, Literal
from urllib.parse import quote

from frontapp_public_api_client.helpers.attachments import FileSpec
from frontapp_public_api_client.helpers.base import Base

if TYPE_CHECKING:
    from frontapp_public_api_client.domain import Draft
    from frontapp_public_api_client.models.message_response import MessageResponse


async def _send_draft_multipart(
    drafts: Drafts,
    *,
    method: Literal["POST", "PATCH"],
    path: str,
    files: builtins.list[FileSpec],
    **fields: Any,
) -> Draft:
    """Shared multipart-bypass + Draft validation for the three draft mutations.

    Folds the four lines that were copy-pasted across create_on_channel /
    create_reply / edit (build payload → call attachments.post_multipart →
    validate Draft) into one place. ``fields`` accepts the same kwargs the
    callers expose; ``None`` values are dropped before encoding so missing
    optional fields don't show up as empty multipart parts.
    """
    from frontapp_public_api_client.domain import Draft

    payload = {k: v for k, v in fields.items() if v is not None}
    data = await drafts._client.attachments.post_multipart(
        method=method,
        path=path,
        fields=payload,
        files=files,
    )
    return Draft.model_validate(data or {})


class Drafts(Base):
    """Ergonomic operations over Frontapp's drafts endpoints."""

    # -- reads --------------------------------------------------------------

    async def list_for_conversation(
        self, conversation_id: str
    ) -> builtins.list[MessageResponse]:
        """List drafts on a conversation. Returns raw attrs ``MessageResponse``s.

        Callers wanting a domain projection should
        ``Draft.model_validate(item.to_dict())`` per item.
        """
        from frontapp_public_api_client.api.drafts import list_conversation_drafts
        from frontapp_public_api_client.utils import unwrap

        response = await list_conversation_drafts.asyncio_detailed(
            conversation_id=conversation_id, client=self._client
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    # -- mutations ----------------------------------------------------------

    async def create_on_channel(
        self,
        channel_id: str,
        *,
        body: str,
        author_id: str | None = None,
        subject: str | None = None,
        to: builtins.list[str] | None = None,
        cc: builtins.list[str] | None = None,
        bcc: builtins.list[str] | None = None,
        quote_body: str | None = None,
        attachments: builtins.list[FileSpec] | None = None,
        mode: Literal["private", "shared"] | None = None,
        signature_id: str | None = None,
        should_add_default_signature: bool | None = None,
    ) -> Draft:
        """Create a new draft on a channel (no existing conversation).

        Returns the created ``Draft``. The human reviews it in Front and sends.
        Pass ``attachments=[FileSpec(...), ...]`` to attach files; the request
        is then sent as ``multipart/form-data`` (the generated client's
        JSON-only path doesn't support binary).
        """
        if attachments:
            return await _send_draft_multipart(
                self,
                method="POST",
                path=f"/channels/{quote(str(channel_id), safe='')}/drafts",
                files=attachments,
                body=body,
                author_id=author_id,
                subject=subject,
                to=to,
                cc=cc,
                bcc=bcc,
                quote_body=quote_body,
                mode=mode,
                signature_id=signature_id,
                should_add_default_signature=should_add_default_signature,
            )

        from frontapp_public_api_client.api.drafts import create_draft
        from frontapp_public_api_client.domain import Draft
        from frontapp_public_api_client.models.create_draft import CreateDraft
        from frontapp_public_api_client.models.create_draft_mode import (
            CreateDraftMode,
        )
        from frontapp_public_api_client.models.message_response import MessageResponse
        from frontapp_public_api_client.utils import unwrap_as

        payload_kwargs: dict[str, Any] = {"body": body}
        if author_id is not None:
            payload_kwargs["author_id"] = author_id
        if subject is not None:
            payload_kwargs["subject"] = subject
        if to is not None:
            payload_kwargs["to"] = to
        if cc is not None:
            payload_kwargs["cc"] = cc
        if bcc is not None:
            payload_kwargs["bcc"] = bcc
        if quote_body is not None:
            payload_kwargs["quote_body"] = quote_body
        if mode is not None:
            payload_kwargs["mode"] = CreateDraftMode(mode)
        if signature_id is not None:
            payload_kwargs["signature_id"] = signature_id
        if should_add_default_signature is not None:
            payload_kwargs["should_add_default_signature"] = (
                should_add_default_signature
            )

        draft_body = CreateDraft(**payload_kwargs)
        response = await create_draft.asyncio_detailed(
            channel_id=channel_id, client=self._client, body=draft_body
        )
        message = unwrap_as(response, MessageResponse)
        return Draft.model_validate(message.to_dict())

    async def create_reply(
        self,
        conversation_id: str,
        *,
        body: str,
        channel_id: str,
        author_id: str | None = None,
        subject: str | None = None,
        to: builtins.list[str] | None = None,
        cc: builtins.list[str] | None = None,
        bcc: builtins.list[str] | None = None,
        quote_body: str | None = None,
        attachments: builtins.list[FileSpec] | None = None,
        mode: Literal["private", "shared"] | None = None,
        signature_id: str | None = None,
        should_add_default_signature: bool | None = None,
    ) -> Draft:
        """Create a draft reply on an existing conversation.

        ``channel_id`` is required — Front uses it to pick which channel the
        outbound reply will eventually send through. Returns the created
        ``Draft`` (Front's ``_parse_response`` parses ``MessageResponse`` on
        200 — the spec's ``Any`` arm covers redirects only).

        Pass ``attachments=[FileSpec(...), ...]`` to attach files; the request
        is then sent as ``multipart/form-data``.
        """
        if attachments:
            return await _send_draft_multipart(
                self,
                method="POST",
                path=(f"/conversations/{quote(str(conversation_id), safe='')}/drafts"),
                files=attachments,
                body=body,
                channel_id=channel_id,
                author_id=author_id,
                subject=subject,
                to=to,
                cc=cc,
                bcc=bcc,
                quote_body=quote_body,
                mode=mode,
                signature_id=signature_id,
                should_add_default_signature=should_add_default_signature,
            )

        from frontapp_public_api_client.api.drafts import create_draft_reply
        from frontapp_public_api_client.domain import Draft
        from frontapp_public_api_client.models.create_draft_mode import (
            CreateDraftMode,
        )
        from frontapp_public_api_client.models.message_response import MessageResponse
        from frontapp_public_api_client.models.reply_draft import ReplyDraft
        from frontapp_public_api_client.utils import unwrap_as

        payload_kwargs: dict[str, Any] = {"body": body, "channel_id": channel_id}
        if author_id is not None:
            payload_kwargs["author_id"] = author_id
        if subject is not None:
            payload_kwargs["subject"] = subject
        if to is not None:
            payload_kwargs["to"] = to
        if cc is not None:
            payload_kwargs["cc"] = cc
        if bcc is not None:
            payload_kwargs["bcc"] = bcc
        if quote_body is not None:
            payload_kwargs["quote_body"] = quote_body
        if mode is not None:
            payload_kwargs["mode"] = CreateDraftMode(mode)
        if signature_id is not None:
            payload_kwargs["signature_id"] = signature_id
        if should_add_default_signature is not None:
            payload_kwargs["should_add_default_signature"] = (
                should_add_default_signature
            )

        reply = ReplyDraft(**payload_kwargs)
        response = await create_draft_reply.asyncio_detailed(
            conversation_id=conversation_id, client=self._client, body=reply
        )
        message = unwrap_as(response, MessageResponse)
        return Draft.model_validate(message.to_dict())

    async def edit(
        self,
        draft_id: str,
        *,
        body: str,
        channel_id: str,
        author_id: str | None = None,
        subject: str | None = None,
        to: builtins.list[str] | None = None,
        cc: builtins.list[str] | None = None,
        bcc: builtins.list[str] | None = None,
        quote_body: str | None = None,
        attachments: builtins.list[FileSpec] | None = None,
        mode: Literal["shared"] | None = None,
        signature_id: str | None = None,
        should_add_default_signature: bool | None = None,
        version: str | None = None,
    ) -> Draft:
        """Edit a draft (full-replacement PATCH).

        Front's PATCH /drafts/{id}/ replaces the draft body — ``body`` and
        ``channel_id`` are both required even if you're only changing
        metadata. Pass ``version`` (from a prior ``Draft.version`` token) to
        avoid clobbering concurrent edits.

        ``mode`` only accepts ``'shared'`` here (Front narrows the enum on
        edit; private drafts can't be re-shared via this endpoint).

        The endpoint path is ``/drafts/{message_id}/`` — note the trailing
        slash and the parameter rename. The helper accepts ``draft_id`` and
        passes it through as ``message_id`` to the generated module.

        Pass ``attachments=[FileSpec(...), ...]`` to replace the draft's
        attachment set; the request is then sent as ``multipart/form-data``.
        """
        if attachments:
            return await _send_draft_multipart(
                self,
                method="PATCH",
                path=f"/drafts/{quote(str(draft_id), safe='')}/",
                files=attachments,
                body=body,
                channel_id=channel_id,
                author_id=author_id,
                subject=subject,
                to=to,
                cc=cc,
                bcc=bcc,
                quote_body=quote_body,
                mode=mode,
                signature_id=signature_id,
                should_add_default_signature=should_add_default_signature,
                version=version,
            )

        from frontapp_public_api_client.api.drafts import edit_draft
        from frontapp_public_api_client.domain import Draft
        from frontapp_public_api_client.models.edit_draft import EditDraft
        from frontapp_public_api_client.models.edit_draft_mode import EditDraftMode
        from frontapp_public_api_client.models.message_response import MessageResponse
        from frontapp_public_api_client.utils import unwrap_as

        payload_kwargs: dict[str, Any] = {"body": body, "channel_id": channel_id}
        if author_id is not None:
            payload_kwargs["author_id"] = author_id
        if subject is not None:
            payload_kwargs["subject"] = subject
        if to is not None:
            payload_kwargs["to"] = to
        if cc is not None:
            payload_kwargs["cc"] = cc
        if bcc is not None:
            payload_kwargs["bcc"] = bcc
        if quote_body is not None:
            payload_kwargs["quote_body"] = quote_body
        if mode is not None:
            payload_kwargs["mode"] = EditDraftMode(mode)
        if signature_id is not None:
            payload_kwargs["signature_id"] = signature_id
        if should_add_default_signature is not None:
            payload_kwargs["should_add_default_signature"] = (
                should_add_default_signature
            )
        if version is not None:
            payload_kwargs["version"] = version

        edit_body = EditDraft(**payload_kwargs)
        response = await edit_draft.asyncio_detailed(
            message_id=draft_id, client=self._client, body=edit_body
        )
        message = unwrap_as(response, MessageResponse)
        return Draft.model_validate(message.to_dict())

    async def delete(self, draft_id: str) -> bool:
        """Delete a draft by id. Returns ``True`` on success (204 No Content)."""
        from frontapp_public_api_client.api.drafts import delete_draft
        from frontapp_public_api_client.utils import is_success

        response = await delete_draft.asyncio_detailed(
            draft_id=draft_id, client=self._client
        )
        return is_success(response)


__all__ = ["Drafts"]
