"""Messages helper facade — ergonomic wrappers around generated message endpoints.

Exposes ``client.messages`` for operations on individual messages by id,
outside the context of listing them on a conversation. Useful when an
agent has a ``msg_*`` id from a webhook or audit log and wants to read or
acknowledge it without first looking up the parent conversation.

Scope is intentionally narrow:

- ``get`` — fetch one message by id
- ``seen_status`` — read the seen receipts for an outbound message
- ``mark_seen`` — POST a seen acknowledgement (rate-limited to 10
  req/msg/hour; only call in response to an actual end-user view)

Out of scope (use other helpers / channels instead):

- ``create_message`` / ``create_message_reply`` — outbound replies go
  through the drafts vertical (``client.drafts``); for direct sends via
  conversations, use ``client.conversations.reply(...)``.
- ``import_inbox_message`` / ``receive_custom_messages`` — Channel API
  surface for partner integrations, not the agent surface.

Quirks worth knowing:

- ``MarkMessageSeenBody`` is generated as an additional-properties-only
  attrs class — there is no declared ``teammate_id`` field. Set it via
  ``body["teammate_id"] = value`` (the helper does this internally).
- ``GetMessageSeenStatusResponse200.field_results`` can be UNSET on
  empty-receipt messages; use ``getattr(parsed, "field_results", None) or []``.
- ``SeenReceiptResponse.first_seen_at`` is an ISO string, not an epoch
  float — no unix-to-datetime conversion is needed.
"""

from __future__ import annotations

import builtins

from frontapp_public_api_client.helpers.base import Base
from frontapp_public_api_client.models.message_response import MessageResponse
from frontapp_public_api_client.models.seen_receipt_response import SeenReceiptResponse


class Messages(Base):
    """Ergonomic operations over Frontapp's ``/messages/{id}`` surface."""

    async def get(self, message_id: str) -> MessageResponse:
        """Fetch one message by id (e.g. ``"msg_abc"``).

        Returns the raw generated ``MessageResponse`` attrs model — there
        is no Pydantic ``Message`` projection (issue #4 deferred it until
        a caller actually wants one).

        Required Front scope: ``messages:read``.
        """
        from frontapp_public_api_client.api.messages import get_message
        from frontapp_public_api_client.utils import unwrap_as

        response = await get_message.asyncio_detailed(
            message_id=message_id, client=self._client
        )
        return unwrap_as(response, MessageResponse)

    async def seen_status(self, message_id: str) -> builtins.list[SeenReceiptResponse]:
        """List seen receipts for an outbound message.

        Returns a list of ``SeenReceiptResponse`` (each carries
        ``first_seen_at`` as an ISO string and ``seen_by`` as the
        recipient's ``ContactHandle``). Empty list when no receipts are
        available yet.

        Required Front scope: ``messages:read``.
        """
        from frontapp_public_api_client.api.messages import get_message_seen_status
        from frontapp_public_api_client.utils import unwrap

        response = await get_message_seen_status.asyncio_detailed(
            message_id=message_id, client=self._client
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def mark_seen(self, message_id: str, teammate_id: str | None = None) -> bool:
        """Acknowledge that a teammate (or the workspace) has seen a message.

        Front rate-limits this to 10 requests per message per hour and
        documents that it should only be called in response to an actual
        end-user view — not as a backfill job.

        ``teammate_id`` is optional; when provided it attributes the seen
        event to a specific teammate (``"tea_abc"``).

        Required Front scope: ``messages:write``. Returns ``True`` on the
        documented 204 No Content.
        """
        from frontapp_public_api_client.api.messages import mark_message_seen
        from frontapp_public_api_client.models.mark_message_seen_body import (
            MarkMessageSeenBody,
        )
        from frontapp_public_api_client.utils import is_success

        body = MarkMessageSeenBody()
        if teammate_id is not None:
            body["teammate_id"] = teammate_id

        response = await mark_message_seen.asyncio_detailed(
            message_id=message_id, client=self._client, body=body
        )
        return is_success(response)


__all__ = ["Messages"]
