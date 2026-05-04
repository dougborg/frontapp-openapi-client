"""Tests for MCP contact tools — preview/decline/execute paths."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.projections import ContactSummary, to_contact_summary
from frontapp_mcp.tools.contacts import register_tools

from frontapp_public_api_client.domain import Contact

from .conftest import create_mock_context


@pytest.fixture
def contacts_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_tools)


# ---------------------------------------------------------------------------
# Preview path — confirm=False on every mutation
# ---------------------------------------------------------------------------


class TestPreviewPath:
    """Every mutation tool must return a preview without calling the client."""

    @pytest.mark.parametrize(
        "tool_name,kwargs",
        [
            (
                "create_contact",
                {"handles": [{"handle": "a@x.com", "source": "email"}], "name": "A"},
            ),
            (
                "create_team_contact",
                {
                    "team_id": "tim_a",
                    "handles": [{"handle": "a@x.com", "source": "email"}],
                },
            ),
            (
                "create_teammate_contact",
                {
                    "teammate_id": "tea_a",
                    "handles": [{"handle": "a@x.com", "source": "email"}],
                },
            ),
            ("update_contact", {"contact_id": "crd_a", "name": "Updated"}),
            ("delete_contact", {"contact_id": "crd_a"}),
            (
                "merge_contacts",
                {"contact_ids": ["crd_a", "crd_b"], "target_contact_id": "crd_a"},
            ),
            (
                "add_contact_note",
                {"contact_id": "crd_a", "body": "VIP", "author_id": "tea_a"},
            ),
            (
                "add_contact_handle",
                {"contact_id": "crd_a", "handle": "b@x.com", "source": "email"},
            ),
            (
                "delete_contact_handle",
                {"contact_id": "crd_a", "handle": "b@x.com", "source": "email"},
            ),
        ],
    )
    async def test_preview_returns_preview(self, contacts_tools, tool_name, kwargs):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await contacts_tools[tool_name](context, **kwargs, confirm=False)

        assert result["confirmed"] is False
        assert "preview" in result


# ---------------------------------------------------------------------------
# Update no-changes guard
# ---------------------------------------------------------------------------


class TestUpdateNoChanges:
    async def test_update_with_no_args_short_circuits(self, contacts_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()

        result = await contacts_tools["update_contact"](
            context, contact_id="crd_a", confirm=True
        )
        assert result["result"] == "no_changes_requested"


# ---------------------------------------------------------------------------
# Confirmed execution
# ---------------------------------------------------------------------------


class TestConfirmedExecution:
    async def test_create_contact_calls_helper(self, contacts_tools):
        context, lifespan = create_mock_context()
        returned = Contact.model_validate(
            {
                "id": "crd_new",
                "name": "Alice",
                "handles": [{"handle": "a@x.com", "source": "email"}],
            }
        )
        lifespan.client = AsyncMock()
        lifespan.client.contacts.create = AsyncMock(return_value=returned)

        result = await contacts_tools["create_contact"](
            context,
            handles=[{"handle": "a@x.com", "source": "email"}],
            name="Alice",
            confirm=True,
        )

        lifespan.client.contacts.create.assert_awaited_once()
        assert result["confirmed"] is True
        assert result["contact"]["id"] == "crd_new"
        assert result["contact"]["name"] == "Alice"

    async def test_delete_contact_calls_helper(self, contacts_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.contacts.delete = AsyncMock(return_value=True)

        result = await contacts_tools["delete_contact"](
            context, contact_id="crd_a", confirm=True
        )

        lifespan.client.contacts.delete.assert_awaited_once_with("crd_a")
        assert result == {"confirmed": True, "deleted": True}

    async def test_merge_contacts_warns_destructive(self, contacts_tools):
        """The preview includes a warning string flagging the destructive nature."""
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()

        result = await contacts_tools["merge_contacts"](
            context,
            contact_ids=["crd_a", "crd_b"],
            target_contact_id="crd_a",
            confirm=False,
        )
        assert "IRREVERSIBLE" in result["preview"]["warning"]

    async def test_delete_contact_warns_destructive(self, contacts_tools):
        context, _ = create_mock_context()
        result = await contacts_tools["delete_contact"](
            context, contact_id="crd_a", confirm=False
        )
        assert "PERMANENT" in result["preview"]["warning"]


# ---------------------------------------------------------------------------
# ContactSummary projection
# ---------------------------------------------------------------------------


class TestContactSummary:
    def test_primary_email_picks_first_email_handle(self):
        contact = Contact.model_validate(
            {
                "id": "crd_a",
                "name": "Alice",
                "handles": [
                    {"handle": "+15551234", "source": "phone"},
                    {"handle": "a@x.com", "source": "email"},
                    {"handle": "alt@x.com", "source": "email"},
                ],
            }
        )
        summary = to_contact_summary(contact)
        assert isinstance(summary, ContactSummary)
        assert summary.primary_email == "a@x.com"
        assert summary.primary_phone == "+15551234"
        assert summary.handle_count == 3

    def test_no_handles_means_no_primaries(self):
        contact = Contact.model_validate({"id": "crd_a", "name": "Empty"})
        summary = to_contact_summary(contact)
        assert summary.primary_email is None
        assert summary.primary_phone is None
        assert summary.handle_count == 0

    def test_group_names_filtered(self):
        contact = Contact.model_validate(
            {
                "id": "crd_a",
                "groups": [
                    {"id": "grp_1", "name": "VIP"},
                    {"id": "grp_2"},  # no name
                    {"id": "grp_3", "name": "Newsletter"},
                ],
            }
        )
        summary = to_contact_summary(contact)
        assert summary.group_names == ["VIP", "Newsletter"]
