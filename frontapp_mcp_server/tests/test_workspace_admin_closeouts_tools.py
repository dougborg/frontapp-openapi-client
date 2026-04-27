"""Tests for the workspace-admin closeout MCP tools (#86, #93).

- ``add_team_members`` / ``remove_team_members`` (#86) — preview /
  decline / confirm paths.
- ``trigger_application_event`` (#93) — preview / decline / confirm
  paths; both id-based and ext_link-based event payloads.

The rules surface (#84) is a reference resource, exercised in
``test_admin_reference_resources.py``.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.tools.applications import register_tools as register_applications
from frontapp_mcp.tools.teams import register_tools as register_teams

from .conftest import create_mock_context


@pytest.fixture
def teams_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_teams)


@pytest.fixture
def applications_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_applications)


# ---------------------------------------------------------------------------
# add_team_members / remove_team_members (#86)
# ---------------------------------------------------------------------------


class TestAddTeamMembers:
    async def test_preview_does_not_call_helper(self, teams_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await teams_tools["add_team_members"](
            context,
            team_id="tim_1",
            teammate_ids=["tea_a", "tea_b"],
            confirm=False,
        )
        assert result["confirmed"] is False
        assert result["preview"]["teammate_count"] == 2
        assert result["preview"]["teammate_ids"] == ["tea_a", "tea_b"]
        context.elicit.assert_not_called()

    async def test_confirmed_calls_helper(self, teams_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.teams.add_teammates = AsyncMock(return_value=True)

        result = await teams_tools["add_team_members"](
            context,
            team_id="tim_1",
            teammate_ids=["tea_a"],
            confirm=True,
        )
        assert result["confirmed"] is True
        assert result["added_count"] == 1
        lifespan.client.teams.add_teammates.assert_awaited_once_with("tim_1", ["tea_a"])

    async def test_declined_elicitation_does_not_call_helper(self, teams_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked after decline")
        )

        result = await teams_tools["add_team_members"](
            context,
            team_id="tim_1",
            teammate_ids=["tea_a"],
            confirm=True,
        )
        assert result["confirmed"] is False
        context.elicit.assert_called_once()


class TestRemoveTeamMembers:
    async def test_preview_includes_count_and_ids(self, teams_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await teams_tools["remove_team_members"](
            context,
            team_id="tim_1",
            teammate_ids=["tea_a", "tea_b", "tea_c"],
            confirm=False,
        )
        assert result["confirmed"] is False
        assert result["preview"]["teammate_count"] == 3
        assert result["preview"]["action"] == "remove_team_members"

    async def test_confirmed_calls_helper(self, teams_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.teams.remove_teammates = AsyncMock(return_value=True)

        result = await teams_tools["remove_team_members"](
            context, team_id="tim_1", teammate_ids=["tea_a"], confirm=True
        )
        assert result["confirmed"] is True
        assert result["removed_count"] == 1
        lifespan.client.teams.remove_teammates.assert_awaited_once_with(
            "tim_1", ["tea_a"]
        )


# ---------------------------------------------------------------------------
# trigger_application_event (#93)
# ---------------------------------------------------------------------------


class TestTriggerApplicationEvent:
    async def test_preview_does_not_call_helper(self, applications_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await applications_tools["trigger_application_event"](
            context,
            application_uid="app_xyz",
            event_type="customer_replied",
            app_object_id="cnv_abc",
            confirm=False,
        )
        assert result["confirmed"] is False
        assert result["preview"]["event_type"] == "customer_replied"
        assert result["preview"]["app_object_id"] == "cnv_abc"
        context.elicit.assert_not_called()

    async def test_confirmed_with_id_calls_helper(self, applications_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.applications.trigger_event = AsyncMock(return_value=True)

        result = await applications_tools["trigger_application_event"](
            context,
            application_uid="app_xyz",
            event_type="customer_replied",
            app_object_id="cnv_abc",
            confirm=True,
        )
        assert result["confirmed"] is True
        call = lifespan.client.applications.trigger_event.await_args
        assert call is not None
        assert call.args == ("app_xyz",)
        assert call.kwargs["event_type"] == "customer_replied"
        assert call.kwargs["app_object_id"] == "cnv_abc"
        assert call.kwargs["app_object_ext_link"] is None

    async def test_confirmed_with_ext_link_passes_through(self, applications_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.applications.trigger_event = AsyncMock(return_value=True)

        await applications_tools["trigger_application_event"](
            context,
            application_uid="app_xyz",
            event_type="external_event",
            app_object_ext_link="https://example.com/x",
            confirm=True,
        )
        call = lifespan.client.applications.trigger_event.await_args
        assert call is not None
        assert call.kwargs["app_object_ext_link"] == "https://example.com/x"
        assert call.kwargs["app_object_id"] is None

    async def test_declined_does_not_call_helper(self, applications_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked after decline")
        )

        result = await applications_tools["trigger_application_event"](
            context,
            application_uid="app_xyz",
            event_type="x",
            app_object_id="cnv_y",
            confirm=True,
        )
        assert result["confirmed"] is False
