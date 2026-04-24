"""Conversation helper facade — ergonomic wrappers around generated endpoints.

Exposes ``client.conversations.{list, get, search, update, list_messages,
reply, list_comments, add_comment}`` with domain-model return values.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from frontapp_public_api_client.helpers.base import Base

if TYPE_CHECKING:
    from frontapp_public_api_client.domain import Conversation


def _extract_page_token(next_url: str | None) -> str | None:
    """Pull the ``page_token`` query param out of Front's next-page URL."""
    if not next_url:
        return None
    try:
        query = urlparse(next_url).query
        tokens = parse_qs(query).get("page_token", [])
        return tokens[0] if tokens else None
    except (ValueError, IndexError):
        return None


class Conversations(Base):
    """Ergonomic operations over Frontapp's ``/conversations*`` endpoints."""

    # -- reads --------------------------------------------------------------

    async def list(
        self,
        *,
        q: str | None = None,
        limit: int | None = None,
        page_token: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> builtins.list[Conversation]:
        """List conversations in reverse chronological order.

        Args:
            q: Front search syntax (e.g. ``"status:open tag:urgent"``). See
                https://dev.frontapp.com/reference/list-conversations.
            limit: Page size (max 100, default 50).
            page_token: Cursor from a previous response's ``_pagination.next``.
            sort_by: Sort field (``"id"`` for chronological).
            sort_order: ``"asc"`` or ``"desc"``.
        """
        from frontapp_public_api_client.api.conversations import list_conversations
        from frontapp_public_api_client.domain import Conversation
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
            from frontapp_public_api_client.models.list_conversations_sort_order import (
                ListConversationsSortOrder,
            )

            kwargs["sort_order"] = ListConversationsSortOrder(sort_order)

        response = await list_conversations.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Conversation.model_validate(c.to_dict()) for c in results]

    async def search(
        self,
        query: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Conversation]:
        """Full Front search-syntax query (e.g. ``"status:open AND tag:urgent"``)."""
        from frontapp_public_api_client.api.conversations import search_conversations
        from frontapp_public_api_client.domain import Conversation
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "query": query}
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await search_conversations.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Conversation.model_validate(c.to_dict()) for c in results]

    async def get(self, conversation_id: str) -> Conversation:
        """Fetch one conversation by id (e.g. ``"cnv_abc123"``)."""
        from frontapp_public_api_client.api.conversations import (
            get_conversation_by_id,
        )
        from frontapp_public_api_client.domain import Conversation
        from frontapp_public_api_client.utils import unwrap

        response = await get_conversation_by_id.asyncio_detailed(
            conversation_id=conversation_id, client=self._client
        )
        parsed = unwrap(response)
        return Conversation.model_validate(parsed.to_dict())

    async def list_messages(
        self,
        conversation_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Any]:
        """List messages in a conversation. Returns raw attrs models."""
        from frontapp_public_api_client.api.conversations import (
            list_conversation_messages,
        )
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {
            "client": self._client,
            "conversation_id": conversation_id,
        }
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_conversation_messages.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def list_comments(self, conversation_id: str) -> builtins.list[Any]:
        """List internal comments on a conversation."""
        from frontapp_public_api_client.api.comments import (
            list_conversation_comments,
        )
        from frontapp_public_api_client.utils import unwrap

        response = await list_conversation_comments.asyncio_detailed(
            conversation_id=conversation_id, client=self._client
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    # -- mutations ----------------------------------------------------------

    async def reply(
        self,
        conversation_id: str,
        *,
        body: str,
        author_id: str | None = None,
        subject: str | None = None,
        to: builtins.list[str] | None = None,
        cc: builtins.list[str] | None = None,
        bcc: builtins.list[str] | None = None,
    ) -> Any:
        """Send an outbound reply on an existing conversation.

        Uses the channel the conversation was opened on. Returns the raw
        response (Front replies with 202 Accepted; the message is enqueued).
        """
        from frontapp_public_api_client.api.conversations import (
            reply_to_conversation,
        )
        from frontapp_public_api_client.models.outbound_reply_message import (
            OutboundReplyMessage,
        )

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

        message = OutboundReplyMessage(**payload_kwargs)
        return await reply_to_conversation.asyncio_detailed(
            conversation_id=conversation_id, client=self._client, body=message
        )

    async def add_comment(
        self,
        conversation_id: str,
        *,
        body: str,
        author_id: str | None = None,
    ) -> Any:
        """Add an internal comment (visible to teammates only)."""
        from frontapp_public_api_client.api.comments import add_comment
        from frontapp_public_api_client.models.add_comment import AddComment

        payload_kwargs: dict[str, Any] = {"body": body}
        if author_id is not None:
            payload_kwargs["author_id"] = author_id

        comment = AddComment(**payload_kwargs)
        return await add_comment.asyncio_detailed(
            conversation_id=conversation_id, client=self._client, body=comment
        )

    async def update(
        self,
        conversation_id: str,
        *,
        status: str | None = None,
        assignee_id: str | None = None,
        inbox_id: str | None = None,
        tag_ids: builtins.list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Any:
        """Update a conversation's mutable fields.

        Use ``status='archived'`` to archive, ``status='open'`` to reopen.
        Pass ``assignee_id=None`` explicitly via :meth:`unassign` to clear;
        here ``None`` means "don't change".
        """
        from frontapp_public_api_client.api.conversations import update_conversation
        from frontapp_public_api_client.models.update_conversation import (
            UpdateConversation,
        )

        payload_kwargs: dict[str, Any] = {}
        if status is not None:
            from frontapp_public_api_client.models.update_conversation_status import (
                UpdateConversationStatus,
            )

            payload_kwargs["status"] = UpdateConversationStatus(status)
        if assignee_id is not None:
            payload_kwargs["assignee_id"] = assignee_id
        if inbox_id is not None:
            payload_kwargs["inbox_id"] = inbox_id
        if tag_ids is not None:
            payload_kwargs["tag_ids"] = tag_ids
        if custom_fields is not None:
            payload_kwargs["custom_fields"] = custom_fields

        body = UpdateConversation(**payload_kwargs)
        return await update_conversation.asyncio_detailed(
            conversation_id=conversation_id, client=self._client, body=body
        )


__all__ = ["Conversations", "_extract_page_token"]
