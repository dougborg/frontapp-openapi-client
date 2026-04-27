"""Tests for MCP contact_lists tools — preview/decline/execute paths.

Mirrors the contacts-tools test layout: every mutation is verified to
return a preview without calling the client on confirm=False, to honor
declined elicitation, and to invoke the helper on confirmed elicitation.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.tools.contact_lists import register_tools

from frontapp_public_api_client.domain import Contact, ContactList

from .conftest import create_mock_context


@pytest.fixture
def lists_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_tools)


# ---------------------------------------------------------------------------
# Reads — no confirm gate
# ---------------------------------------------------------------------------


class TestReads:
    async def test_list_contact_lists_calls_helper(self, lists_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.contact_lists.list = AsyncMock(
            return_value=[
                ContactList.model_validate({"id": "lst_1", "name": "VIP"}),
                ContactList.model_validate({"id": "lst_2", "name": "Newsletter"}),
            ]
        )

        result = await lists_tools["list_contact_lists"](context)

        lifespan.client.contact_lists.list.assert_awaited_once()
        assert [r.id for r in result] == ["lst_1", "lst_2"]

    async def test_list_team_contact_lists_passes_team_id(self, lists_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.contact_lists.list_for_team = AsyncMock(return_value=[])

        await lists_tools["list_team_contact_lists"](context, team_id="tim_xyz")

        lifespan.client.contact_lists.list_for_team.assert_awaited_once_with("tim_xyz")

    async def test_list_contacts_in_contact_list_returns_summaries(self, lists_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.contact_lists.list_members = AsyncMock(
            return_value=[
                Contact.model_validate({"id": "crd_1", "name": "Alice", "handles": []})
            ]
        )

        result = await lists_tools["list_contacts_in_contact_list"](
            context, contact_list_id="lst_abc"
        )

        assert len(result) == 1
        assert result[0].id == "crd_1"


# ---------------------------------------------------------------------------
# Preview path — confirm=False on every mutation
# ---------------------------------------------------------------------------


class TestPreviewPath:
    @pytest.mark.parametrize(
        "tool_name,kwargs",
        [
            ("create_contact_list", {"name": "VIP"}),
            ("create_team_contact_list", {"team_id": "tim_a", "name": "VIP"}),
            (
                "create_teammate_contact_list",
                {"teammate_id": "tea_a", "name": "Personal"},
            ),
            ("delete_contact_list", {"contact_list_id": "lst_a"}),
            (
                "add_contacts_to_contact_list",
                {"contact_list_id": "lst_a", "contact_ids": ["crd_1"]},
            ),
            (
                "remove_contacts_from_contact_list",
                {"contact_list_id": "lst_a", "contact_ids": ["crd_1"]},
            ),
        ],
    )
    async def test_preview_returns_preview(self, lists_tools, tool_name, kwargs):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await lists_tools[tool_name](context, **kwargs, confirm=False)

        assert result["confirmed"] is False
        assert "preview" in result
        context.elicit.assert_not_called()

    async def test_remove_over_50_returns_error_without_calling_elicit(
        self, lists_tools
    ):
        """The 50-cap guard fires before the preview path even runs."""
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked when over-cap")
        )

        big_list = [f"crd_{i}" for i in range(51)]
        result = await lists_tools["remove_contacts_from_contact_list"](
            context, contact_list_id="lst_a", contact_ids=big_list, confirm=True
        )

        assert result["confirmed"] is False
        assert "caps remove_contacts at 50" in result["error"]
        context.elicit.assert_not_called()


# ---------------------------------------------------------------------------
# Confirmed execution
# ---------------------------------------------------------------------------


class TestConfirmedExecution:
    async def test_create_calls_helper(self, lists_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.contact_lists.create = AsyncMock(return_value=True)

        result = await lists_tools["create_contact_list"](
            context, name="VIP", confirm=True
        )

        lifespan.client.contact_lists.create.assert_awaited_once_with("VIP")
        assert result == {"confirmed": True, "name": "VIP"}

    async def test_add_contacts_calls_helper(self, lists_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.contact_lists.add_contacts = AsyncMock(return_value=True)

        result = await lists_tools["add_contacts_to_contact_list"](
            context,
            contact_list_id="lst_a",
            contact_ids=["crd_1", "crd_2"],
            confirm=True,
        )

        lifespan.client.contact_lists.add_contacts.assert_awaited_once_with(
            "lst_a", ["crd_1", "crd_2"]
        )
        assert result["added_count"] == 2

    async def test_declined_does_not_call_helper(self, lists_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked when declined")
        )

        result = await lists_tools["delete_contact_list"](
            context, contact_list_id="lst_a", confirm=True
        )

        assert result["confirmed"] is False
        assert result["result"] == "cancelled"
