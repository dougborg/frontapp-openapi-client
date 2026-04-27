"""Tests for the messages vertical: Messages helper.

No domain projection ships with this vertical (issue #4 deferred it), so
these tests exercise the helper against ``MockTransport`` directly and
assert on the raw generated attrs models.
"""

from __future__ import annotations

import json

import pytest

from frontapp_public_api_client.models.message_response import MessageResponse
from frontapp_public_api_client.models.seen_receipt_response import SeenReceiptResponse
from frontapp_public_api_client.utils import APIError


class TestMessagesHelper:
    """Helper-level integration via the shared ``attach_transport`` /
    ``make_*_transport`` fixtures from ``tests/conftest.py``."""

    # -- get ----------------------------------------------------------------

    async def test_get_returns_message_response(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "id": "msg_abc",
                    "type": "email",
                    "is_inbound": True,
                    "subject": "Hello",
                    "blurb": "Hi there",
                    "body": "<p>Hi there</p>",
                    "text": "Hi there",
                    "created_at": 1701292639,
                }
            )
        )

        message = await client.messages.get("msg_abc")
        assert isinstance(message, MessageResponse)
        assert message.id == "msg_abc"
        assert message.subject == "Hello"
        assert message.is_inbound is True

    async def test_get_raises_on_404(self, attach_transport, make_mock_transport):
        client = attach_transport(
            make_mock_transport(
                {"_error": {"status": 404, "message": "Not found"}}, status=404
            )
        )

        with pytest.raises(APIError):
            await client.messages.get("msg_missing")

    # -- seen_status --------------------------------------------------------

    async def test_seen_status_returns_list_of_receipts(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "_results": [
                        {
                            "_links": {"related": {"message": "..."}},
                            "first_seen_at": "2024-01-01T12:00:00Z",
                            "seen_by": {
                                "handle": "a@example.com",
                                "source": "email",
                            },
                        },
                        {
                            "_links": {"related": {"message": "..."}},
                            "first_seen_at": "2024-01-01T12:05:00Z",
                            "seen_by": {
                                "handle": "b@example.com",
                                "source": "email",
                            },
                        },
                    ],
                    "_pagination": {},
                    "_links": {},
                }
            )
        )

        receipts = await client.messages.seen_status("msg_abc")
        assert len(receipts) == 2
        assert all(isinstance(r, SeenReceiptResponse) for r in receipts)
        assert receipts[0].first_seen_at == "2024-01-01T12:00:00Z"
        assert receipts[1].seen_by.handle == "b@example.com"

    async def test_seen_status_returns_empty_list_when_unset(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {"_pagination": {}, "_links": {}}
            )  # no _results → UNSET
        )

        receipts = await client.messages.seen_status("msg_abc")
        assert receipts == []

    # -- mark_seen ----------------------------------------------------------

    async def test_mark_seen_no_teammate_id_sends_empty_body(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        success = await client.messages.mark_seen("msg_abc")
        assert success is True
        assert len(recorded) == 1
        assert recorded[0].method == "POST"
        assert recorded[0].url.path.endswith("/messages/msg_abc/seen")
        assert json.loads(recorded[0].content) == {}

    async def test_mark_seen_with_teammate_id_includes_it(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        success = await client.messages.mark_seen("msg_abc", teammate_id="tea_xyz")
        assert success is True
        body = json.loads(recorded[0].content)
        assert body == {"teammate_id": "tea_xyz"}

    async def test_mark_seen_returns_false_on_non_204(
        self, attach_transport, make_mock_transport
    ):
        """``is_success`` is True for any 2xx; an unexpected non-2xx returns False."""
        # 429 is wrapped as RateLimitError by unwrap, but mark_seen uses
        # is_success which only inspects the status — confirm the helper
        # surfaces a False return rather than raising.
        client = attach_transport(
            make_mock_transport(
                {"_error": {"status": 429, "message": "Too many requests"}},
                status=429,
            )
        )

        success = await client.messages.mark_seen("msg_abc")
        assert success is False

    # -- property -----------------------------------------------------------

    def test_messages_property_lazy_caches(self, mock_api_credentials):
        """``client.messages`` returns the same Messages instance across calls."""
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.messages
        second = client.messages
        assert first is second
