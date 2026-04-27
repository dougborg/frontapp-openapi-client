"""Tests for MCP teammate tools — 4 reads + update mutation."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from frontapp_mcp.projections import ConversationSummary
from frontapp_mcp.tools.teammates import register_tools

from frontapp_public_api_client.domain import Inbox, Teammate

from .conftest import create_mock_context


@pytest.fixture
def teammates_tools(mcp_tool_capture):
    return mcp_tool_capture(register_tools)


# ---------------------------------------------------------------------------
# Read tools
# ---------------------------------------------------------------------------


class TestReadTools:
    async def test_list_teammates_returns_domain_models(self, teammates_tools):
        context, lifespan = create_mock_context()
        teammates = [
            Teammate.model_validate(
                {"id": "tea_1", "email": "a@x.com", "username": "alice"}
            ),
            Teammate.model_validate(
                {"id": "tea_2", "email": "b@x.com", "username": "bob"}
            ),
        ]
        lifespan.client = AsyncMock()
        lifespan.client.teammates.list = AsyncMock(return_value=teammates)

        result = await teammates_tools["list_teammates"](context)

        assert len(result) == 2
        assert all(isinstance(t, Teammate) for t in result)
        assert [t.username for t in result] == ["alice", "bob"]

    async def test_get_teammate_returns_domain_model(self, teammates_tools):
        context, lifespan = create_mock_context()
        teammate = Teammate.model_validate(
            {"id": "tea_a", "email": "a@x.com", "username": "alice", "is_admin": True}
        )
        lifespan.client = AsyncMock()
        lifespan.client.teammates.get = AsyncMock(return_value=teammate)

        result = await teammates_tools["get_teammate"](context, teammate_id="tea_a")
        assert isinstance(result, Teammate)
        assert result.id == "tea_a"
        assert result.is_admin is True

    async def test_list_teammate_inboxes_returns_domain_models(self, teammates_tools):
        context, lifespan = create_mock_context()
        inboxes = [Inbox.model_validate({"id": "inb_1", "name": "Support"})]
        lifespan.client = AsyncMock()
        lifespan.client.teammates.list_inboxes = AsyncMock(return_value=inboxes)

        result = await teammates_tools["list_teammate_inboxes"](
            context, teammate_id="tea_a"
        )
        assert all(isinstance(i, Inbox) for i in result)

    async def test_list_assigned_conversations_projects_each(self, teammates_tools):
        context, lifespan = create_mock_context()
        msg1 = MagicMock()
        msg1.to_dict.return_value = {"id": "cnv_1"}
        msg2 = MagicMock()
        msg2.to_dict.return_value = {"id": "cnv_2"}
        lifespan.client = AsyncMock()
        lifespan.client.teammates.list_assigned_conversations = AsyncMock(
            return_value=[msg1, msg2]
        )

        result = await teammates_tools["list_assigned_conversations"](
            context, teammate_id="tea_a"
        )

        assert len(result) == 2
        assert all(isinstance(c, ConversationSummary) for c in result)
        # The projection went through Conversation.model_validate(item.to_dict()).
        msg1.to_dict.assert_called_once()
        msg2.to_dict.assert_called_once()


# ---------------------------------------------------------------------------
# Mutation: update_teammate — preview / no-changes / confirm / decline / cancel
# ---------------------------------------------------------------------------


class TestUpdateTeammate:
    async def test_preview_does_not_call_helper(self, teammates_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.teammates.update = AsyncMock(
            side_effect=AssertionError("helper invoked on preview")
        )

        result = await teammates_tools["update_teammate"](
            context, teammate_id="tea_a", first_name="Alicia", confirm=False
        )

        assert result["confirmed"] is False
        assert result["preview"]["changes"] == {"first_name": "Alicia"}
        context.elicit.assert_not_called()
        lifespan.client.teammates.update.assert_not_awaited()

    async def test_no_changes_short_circuits(self, teammates_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()

        result = await teammates_tools["update_teammate"](
            context, teammate_id="tea_a", confirm=True
        )

        assert result["result"] == "no_changes_requested"
        assert result["confirmed"] is False
        context.elicit.assert_not_called()

    async def test_cancelled_does_not_call_helper(self, teammates_tools):
        """User cancelled the elicitation (action='decline') → CANCELLED."""
        context, lifespan = create_mock_context(elicit_action="decline")
        lifespan.client = AsyncMock()
        lifespan.client.teammates.update = AsyncMock(
            side_effect=AssertionError("helper invoked after cancel")
        )

        result = await teammates_tools["update_teammate"](
            context, teammate_id="tea_a", first_name="Alicia", confirm=True
        )

        assert result["confirmed"] is False
        assert result["result"] == "cancelled"
        lifespan.client.teammates.update.assert_not_awaited()

    async def test_declined_does_not_call_helper(self, teammates_tools):
        """User accepted but unchecked the confirm flag → DECLINED."""
        context, lifespan = create_mock_context(
            elicit_confirm=False, elicit_action="accept"
        )
        lifespan.client = AsyncMock()
        lifespan.client.teammates.update = AsyncMock(
            side_effect=AssertionError("helper invoked after decline")
        )

        result = await teammates_tools["update_teammate"](
            context, teammate_id="tea_a", first_name="Alicia", confirm=True
        )

        assert result["confirmed"] is False
        assert result["result"] == "declined"
        lifespan.client.teammates.update.assert_not_awaited()

    async def test_confirmed_calls_helper(self, teammates_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.teammates.update = AsyncMock(return_value=True)

        result = await teammates_tools["update_teammate"](
            context,
            teammate_id="tea_a",
            first_name="Alicia",
            is_available=False,
            confirm=True,
        )

        lifespan.client.teammates.update.assert_awaited_once_with(
            "tea_a",
            username=None,
            first_name="Alicia",
            last_name=None,
            is_available=False,
        )
        assert result == {"confirmed": True, "updated": True}
