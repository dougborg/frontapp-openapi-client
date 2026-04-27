"""Tests for MCP conversations tools — 5 reads + 2 mutations."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from frontapp_mcp.projections import ConversationSummary
from frontapp_mcp.tools.conversations import register_tools

from frontapp_public_api_client.domain import Conversation

from .conftest import create_mock_context


@pytest.fixture
def conversations_tools(mcp_tool_capture):
    return mcp_tool_capture(register_tools)


# ---------------------------------------------------------------------------
# Read tools — list / get / search / list_messages / list_comments
# ---------------------------------------------------------------------------


class TestReadTools:
    async def test_list_conversations_projects_each(self, conversations_tools):
        context, lifespan = create_mock_context()
        convs = [
            Conversation.model_validate({"id": "cnv_1", "subject": "A"}),
            Conversation.model_validate({"id": "cnv_2", "subject": "B"}),
        ]
        lifespan.client = AsyncMock()
        lifespan.client.conversations.list = AsyncMock(return_value=convs)

        result = await conversations_tools["list_conversations"](context)

        assert len(result) == 2
        assert all(isinstance(s, ConversationSummary) for s in result)
        assert [s.id for s in result] == ["cnv_1", "cnv_2"]

    async def test_list_conversations_passes_q_limit_token(self, conversations_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.conversations.list = AsyncMock(return_value=[])

        await conversations_tools["list_conversations"](
            context, q="status:open", limit=25, page_token="cursor_abc"
        )

        lifespan.client.conversations.list.assert_awaited_once_with(
            q="status:open", limit=25, page_token="cursor_abc"
        )

    async def test_get_conversation_returns_summary(self, conversations_tools):
        context, lifespan = create_mock_context()
        conv = Conversation.model_validate({"id": "cnv_a", "subject": "Hi"})
        lifespan.client = AsyncMock()
        lifespan.client.conversations.get = AsyncMock(return_value=conv)

        result = await conversations_tools["get_conversation"](
            context, conversation_id="cnv_a"
        )

        assert isinstance(result, ConversationSummary)
        assert result.id == "cnv_a"
        assert result.subject == "Hi"

    async def test_search_conversations_passes_query(self, conversations_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.conversations.search = AsyncMock(return_value=[])

        await conversations_tools["search_conversations"](
            context, query="status:open AND tag:vip"
        )

        lifespan.client.conversations.search.assert_awaited_once_with(
            "status:open AND tag:vip", limit=None, page_token=None
        )

    async def test_list_conversation_messages_returns_dicts(self, conversations_tools):
        context, lifespan = create_mock_context()
        msg1 = MagicMock()
        msg1.to_dict.return_value = {"id": "msg_1", "type": "email"}
        msg2 = MagicMock()
        msg2.to_dict.return_value = {"id": "msg_2", "type": "email"}
        lifespan.client = AsyncMock()
        lifespan.client.conversations.list_messages = AsyncMock(
            return_value=[msg1, msg2]
        )

        result = await conversations_tools["list_conversation_messages"](
            context, conversation_id="cnv_a"
        )

        # Assert .to_dict() was called per item, so removing the projection
        # logic from the tool would fail this test (not just the equality).
        msg1.to_dict.assert_called_once()
        msg2.to_dict.assert_called_once()
        assert len(result) == 2
        assert result[0] == {"id": "msg_1", "type": "email"}

    async def test_list_conversation_comments_returns_dicts(self, conversations_tools):
        context, lifespan = create_mock_context()
        comment = MagicMock()
        comment.to_dict.return_value = {"id": "com_1", "body": "Note"}
        lifespan.client = AsyncMock()
        lifespan.client.conversations.list_comments = AsyncMock(return_value=[comment])

        result = await conversations_tools["list_conversation_comments"](
            context, conversation_id="cnv_a"
        )

        assert result == [{"id": "com_1", "body": "Note"}]


# ---------------------------------------------------------------------------
# Mutation: update_conversation — preview / no-changes / confirm / decline
# ---------------------------------------------------------------------------


class TestUpdateConversation:
    async def test_preview_does_not_call_helper(self, conversations_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview")
        )

        result = await conversations_tools["update_conversation"](
            context, conversation_id="cnv_a", status="archived", confirm=False
        )

        assert result["confirmed"] is False
        assert result["preview"]["changes"] == {"status": "archived"}
        context.elicit.assert_not_called()

    async def test_no_changes_short_circuits(self, conversations_tools):
        """Empty changes dict returns early with ``no_changes_requested``
        even when confirm=True is passed — protects against no-op mutations."""
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()

        result = await conversations_tools["update_conversation"](
            context, conversation_id="cnv_a", confirm=True
        )

        assert result["result"] == "no_changes_requested"
        assert result["confirmed"] is False
        context.elicit.assert_not_called()

    async def test_declined_does_not_call_helper(self, conversations_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked after decline")
        )

        result = await conversations_tools["update_conversation"](
            context, conversation_id="cnv_a", status="archived", confirm=True
        )

        assert result["confirmed"] is False
        assert result["result"] == "cancelled"
        context.elicit.assert_called_once()

    async def test_confirmed_calls_helper(self, conversations_tools):
        context, lifespan = create_mock_context()
        response = MagicMock()
        response.status_code = 204
        lifespan.client = AsyncMock()
        lifespan.client.conversations.update = AsyncMock(return_value=response)

        result = await conversations_tools["update_conversation"](
            context,
            conversation_id="cnv_a",
            status="archived",
            assignee_id="tea_xyz",
            confirm=True,
        )

        lifespan.client.conversations.update.assert_awaited_once_with(
            "cnv_a",
            status="archived",
            assignee_id="tea_xyz",
            inbox_id=None,
            tag_ids=None,
        )
        assert result == {"confirmed": True, "status_code": 204}

    async def test_tag_ids_documented_as_replace(self, conversations_tools):
        """The preview should make it clear update_conversation REPLACES
        the full tag set (vs the delta methods on the tags vertical)."""
        context, _ = create_mock_context()
        result = await conversations_tools["update_conversation"](
            context,
            conversation_id="cnv_a",
            tag_ids=["tag_1", "tag_2"],
            confirm=False,
        )
        assert result["preview"]["changes"] == {"tag_ids": ["tag_1", "tag_2"]}


# ---------------------------------------------------------------------------
# Mutation: add_conversation_comment — preview / decline / confirm
# ---------------------------------------------------------------------------


class TestAddConversationComment:
    async def test_preview_includes_truncated_body(self, conversations_tools):
        context, lifespan = create_mock_context()
        long_body = "x" * 250
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview")
        )

        result = await conversations_tools["add_conversation_comment"](
            context, conversation_id="cnv_a", body=long_body, confirm=False
        )

        # Truncated to 200 chars + ellipsis.
        assert result["preview"]["body_preview"].endswith("…")
        assert len(result["preview"]["body_preview"]) == 201

    async def test_short_body_not_truncated(self, conversations_tools):
        context, _ = create_mock_context()
        result = await conversations_tools["add_conversation_comment"](
            context, conversation_id="cnv_a", body="Short", confirm=False
        )
        assert result["preview"]["body_preview"] == "Short"

    async def test_declined_does_not_call_helper(self, conversations_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked after decline")
        )

        result = await conversations_tools["add_conversation_comment"](
            context, conversation_id="cnv_a", body="Note", confirm=True
        )

        assert result["confirmed"] is False
        assert result["result"] == "cancelled"

    async def test_confirmed_calls_helper(self, conversations_tools):
        context, lifespan = create_mock_context()
        response = MagicMock()
        response.status_code = 201
        lifespan.client = AsyncMock()
        lifespan.client.conversations.add_comment = AsyncMock(return_value=response)

        result = await conversations_tools["add_conversation_comment"](
            context,
            conversation_id="cnv_a",
            body="VIP customer",
            author_id="tea_xyz",
            confirm=True,
        )

        lifespan.client.conversations.add_comment.assert_awaited_once_with(
            "cnv_a", body="VIP customer", author_id="tea_xyz"
        )
        assert result == {"confirmed": True, "status_code": 201}
