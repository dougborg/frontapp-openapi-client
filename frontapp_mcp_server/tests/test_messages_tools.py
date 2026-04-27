"""Tests for MCP message tools — preview/decline/execute paths."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.tools.messages import register_tools

from frontapp_public_api_client.models.message_response import MessageResponse
from frontapp_public_api_client.models.seen_receipt_response import SeenReceiptResponse

from .conftest import create_mock_context


@pytest.fixture
def messages_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_tools)


# ---------------------------------------------------------------------------
# Read tools — return summary dicts
# ---------------------------------------------------------------------------


class TestReadTools:
    async def test_get_message_returns_summary_dict(self, messages_tools):
        context, lifespan = create_mock_context()
        message = MessageResponse.from_dict(
            {
                "id": "msg_abc",
                "type": "email",
                "is_inbound": True,
                "subject": "Hello",
                "blurb": "Hi there",
                "text": "Hi there",
                "body": "<p>Hi there</p>",
                "created_at": 1701292639,
            }
        )
        lifespan.client = AsyncMock()
        lifespan.client.messages.get = AsyncMock(return_value=message)

        result = await messages_tools["get_message"](context, message_id="msg_abc")

        lifespan.client.messages.get.assert_awaited_once_with("msg_abc")
        assert result["id"] == "msg_abc"
        assert result["type"] == "email"
        assert result["is_inbound"] is True
        assert result["subject"] == "Hello"
        assert result["text"] == "Hi there"

    async def test_get_message_seen_status_returns_list(self, messages_tools):
        context, lifespan = create_mock_context()
        receipts = [
            SeenReceiptResponse.from_dict(
                {
                    "_links": {"related": {"message": "..."}},
                    "first_seen_at": "2024-01-01T12:00:00Z",
                    "seen_by": {"handle": "a@example.com", "source": "email"},
                }
            ),
            SeenReceiptResponse.from_dict(
                {
                    "_links": {"related": {"message": "..."}},
                    "first_seen_at": "2024-01-01T12:05:00Z",
                    "seen_by": {"handle": "b@example.com", "source": "email"},
                }
            ),
        ]
        lifespan.client = AsyncMock()
        lifespan.client.messages.seen_status = AsyncMock(return_value=receipts)

        result = await messages_tools["get_message_seen_status"](
            context, message_id="msg_abc"
        )

        lifespan.client.messages.seen_status.assert_awaited_once_with("msg_abc")
        assert len(result) == 2
        assert result[0]["first_seen_at"] == "2024-01-01T12:00:00Z"
        assert result[0]["seen_by"]["handle"] == "a@example.com"
        assert result[0]["seen_by"]["source"] == "email"


# ---------------------------------------------------------------------------
# Mutation: mark_message_seen — preview / decline / confirm
# ---------------------------------------------------------------------------


class TestMarkMessageSeen:
    async def test_preview_does_not_call_helper(self, messages_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await messages_tools["mark_message_seen"](
            context, message_id="msg_abc", confirm=False
        )

        assert result["confirmed"] is False
        assert result["preview"]["message_id"] == "msg_abc"
        assert result["preview"]["rate_limit"] == "10 req/msg/hour"
        context.elicit.assert_not_called()

    async def test_declined_does_not_call_helper(self, messages_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked after decline")
        )

        result = await messages_tools["mark_message_seen"](
            context, message_id="msg_abc", confirm=True
        )

        assert result["confirmed"] is False
        assert result["result"] == "cancelled"
        context.elicit.assert_called_once()

    async def test_confirmed_calls_helper(self, messages_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.messages.mark_seen = AsyncMock(return_value=True)

        result = await messages_tools["mark_message_seen"](
            context, message_id="msg_abc", confirm=True
        )

        lifespan.client.messages.mark_seen.assert_awaited_once_with(
            "msg_abc", teammate_id=None
        )
        assert result == {"confirmed": True, "marked_seen": True}

    async def test_confirmed_with_teammate_id_forwards_it(self, messages_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.messages.mark_seen = AsyncMock(return_value=True)

        result = await messages_tools["mark_message_seen"](
            context,
            message_id="msg_abc",
            teammate_id="tea_xyz",
            confirm=True,
        )

        lifespan.client.messages.mark_seen.assert_awaited_once_with(
            "msg_abc", teammate_id="tea_xyz"
        )
        assert result == {"confirmed": True, "marked_seen": True}
