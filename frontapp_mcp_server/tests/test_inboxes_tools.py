"""Tests for MCP inbox tools — preview/decline/execute paths."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.projections import InboxSummary
from frontapp_mcp.tools.inboxes import register_tools

from frontapp_public_api_client.domain import Inbox

from .conftest import create_mock_context


@pytest.fixture
def inboxes_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_tools)


# ---------------------------------------------------------------------------
# Read tools
# ---------------------------------------------------------------------------


class TestReadTools:
    async def test_get_inbox_returns_summary(self, inboxes_tools):
        context, lifespan = create_mock_context()
        inbox = Inbox.model_validate({"id": "inb_abc", "name": "Support"})
        lifespan.client = AsyncMock()
        lifespan.client.inboxes.get = AsyncMock(return_value=inbox)

        result = await inboxes_tools["get_inbox"](context, inbox_id="inb_abc")

        assert isinstance(result, InboxSummary)
        assert result.id == "inb_abc"
        assert result.name == "Support"

    async def test_list_inboxes_projects_each(self, inboxes_tools):
        context, lifespan = create_mock_context()
        inboxes = [
            Inbox.model_validate({"id": "inb_1", "name": "Support"}),
            Inbox.model_validate({"id": "inb_2", "name": "Sales"}),
        ]
        lifespan.client = AsyncMock()
        lifespan.client.inboxes.list = AsyncMock(return_value=inboxes)

        result = await inboxes_tools["list_inboxes"](context)

        assert len(result) == 2
        assert all(isinstance(i, InboxSummary) for i in result)


# ---------------------------------------------------------------------------
# Mutation: preview / decline / confirm
# ---------------------------------------------------------------------------


class TestPreviewPath:
    @pytest.mark.parametrize(
        "tool_name,kwargs",
        [
            ("create_inbox", {"name": "Triage"}),
            ("create_team_inbox", {"team_id": "tim_a", "name": "Team Triage"}),
            (
                "grant_inbox_access",
                {"inbox_id": "inb_a", "teammate_ids": ["tea_1", "tea_2"]},
            ),
            (
                "revoke_inbox_access",
                {"inbox_id": "inb_a", "teammate_ids": ["tea_1"]},
            ),
        ],
    )
    async def test_preview_returns_preview(self, inboxes_tools, tool_name, kwargs):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await inboxes_tools[tool_name](context, **kwargs, confirm=False)

        assert result["confirmed"] is False
        assert "preview" in result


class TestPreviewIncludesTeammateCount:
    """Per the issue, access tools must surface count + ids in preview."""

    async def test_grant_access_preview_has_count_and_ids(self, inboxes_tools):
        context, _ = create_mock_context()
        result = await inboxes_tools["grant_inbox_access"](
            context,
            inbox_id="inb_a",
            teammate_ids=["tea_1", "tea_2", "tea_3"],
            confirm=False,
        )
        assert result["preview"]["teammate_count"] == 3
        assert result["preview"]["teammate_ids"] == ["tea_1", "tea_2", "tea_3"]

    async def test_revoke_access_preview_has_count_and_ids(self, inboxes_tools):
        context, _ = create_mock_context()
        result = await inboxes_tools["revoke_inbox_access"](
            context,
            inbox_id="inb_a",
            teammate_ids=["tea_1"],
            confirm=False,
        )
        assert result["preview"]["teammate_count"] == 1
        assert result["preview"]["teammate_ids"] == ["tea_1"]


class TestConfirmedExecution:
    async def test_create_inbox_calls_helper(self, inboxes_tools):
        context, lifespan = create_mock_context()
        new_inbox = Inbox.model_validate({"id": "inb_new", "name": "Triage"})
        lifespan.client = AsyncMock()
        lifespan.client.inboxes.create = AsyncMock(return_value=new_inbox)

        result = await inboxes_tools["create_inbox"](
            context, name="Triage", teammate_ids=["tea_1"], confirm=True
        )

        lifespan.client.inboxes.create.assert_awaited_once()
        assert result["confirmed"] is True
        assert result["inbox"]["id"] == "inb_new"

    async def test_grant_access_calls_helper(self, inboxes_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.inboxes.grant_access = AsyncMock(return_value=True)

        result = await inboxes_tools["grant_inbox_access"](
            context, inbox_id="inb_a", teammate_ids=["tea_1", "tea_2"], confirm=True
        )

        lifespan.client.inboxes.grant_access.assert_awaited_once_with(
            "inb_a", teammate_ids=["tea_1", "tea_2"]
        )
        assert result == {"confirmed": True, "granted": True}

    async def test_revoke_access_calls_helper(self, inboxes_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.inboxes.revoke_access = AsyncMock(return_value=True)

        result = await inboxes_tools["revoke_inbox_access"](
            context, inbox_id="inb_a", teammate_ids=["tea_1"], confirm=True
        )

        lifespan.client.inboxes.revoke_access.assert_awaited_once_with(
            "inb_a", teammate_ids=["tea_1"]
        )
        assert result == {"confirmed": True, "revoked": True}
