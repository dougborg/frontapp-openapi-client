"""Tests for MCP contact_groups tools (deprecated surface).

Same shape as test_contact_lists_tools — every mutation is two-step
confirm. Tool descriptions carry a deprecation note that we don't
assert on individually; the behavioral assertions are identical to
contact_lists.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.tools.contact_groups import register_tools

from frontapp_public_api_client.domain import ContactGroupRef

from .conftest import create_mock_context


@pytest.fixture
def groups_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_tools)


class TestReads:
    async def test_list_contact_groups_calls_helper(self, groups_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.contact_groups.list = AsyncMock(
            return_value=[
                ContactGroupRef.model_validate({"id": "grp_1", "name": "VIP (legacy)"}),
            ]
        )

        result = await groups_tools["list_contact_groups"](context)

        lifespan.client.contact_groups.list.assert_awaited_once()
        assert result[0].id == "grp_1"


class TestPreviewPath:
    @pytest.mark.parametrize(
        "tool_name,kwargs",
        [
            ("create_contact_group", {"name": "Pilot"}),
            ("create_team_contact_group", {"team_id": "tim_a", "name": "Pilot"}),
            (
                "create_teammate_contact_group",
                {"teammate_id": "tea_a", "name": "Pilot"},
            ),
            ("delete_contact_group", {"contact_group_id": "grp_a"}),
            (
                "add_contacts_to_group",
                {"contact_group_id": "grp_a", "contact_ids": ["crd_1"]},
            ),
            (
                "remove_contacts_from_group",
                {"contact_group_id": "grp_a", "contact_ids": ["crd_1"]},
            ),
        ],
    )
    async def test_preview_returns_preview(self, groups_tools, tool_name, kwargs):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await groups_tools[tool_name](context, **kwargs, confirm=False)

        assert result["confirmed"] is False
        assert "preview" in result

    async def test_remove_over_50_returns_error(self, groups_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked when over-cap")
        )

        big_list = [f"crd_{i}" for i in range(51)]
        result = await groups_tools["remove_contacts_from_group"](
            context, contact_group_id="grp_a", contact_ids=big_list, confirm=True
        )

        assert result["confirmed"] is False
        assert "caps remove_contacts at 50" in result["error"]


class TestConfirmedExecution:
    async def test_add_contacts_calls_helper(self, groups_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.contact_groups.add_contacts = AsyncMock(return_value=True)

        result = await groups_tools["add_contacts_to_group"](
            context,
            contact_group_id="grp_a",
            contact_ids=["crd_1", "crd_2"],
            confirm=True,
        )

        lifespan.client.contact_groups.add_contacts.assert_awaited_once_with(
            "grp_a", ["crd_1", "crd_2"]
        )
        assert result["added_count"] == 2
