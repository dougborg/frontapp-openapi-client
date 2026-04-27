"""Tests for MCP draft tools — preview-vs-execute confirm flow.

These tests verify the two-step confirm pattern works as documented in
ADR-0016 → "Drafts-first outbound": every mutation tool returns a preview on
``confirm=False`` without making any API calls, and only attempts the API
call after both the explicit ``confirm=True`` AND a successful elicitation.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.projections import DraftSummary, to_draft_summary
from frontapp_mcp.tools.drafts import register_tools

from frontapp_public_api_client.domain import Draft

from .conftest import create_mock_context


@pytest.fixture
def drafts_tools(mcp_tool_capture) -> dict[str, object]:
    """Register all draft tools and return the captured function dict."""
    return mcp_tool_capture(register_tools)


# ---------------------------------------------------------------------------
# Two-step confirm — preview path (no API call expected)
# ---------------------------------------------------------------------------


class TestPreviewPath:
    """``confirm=False`` should return a preview dict and never call the client."""

    async def test_create_draft_on_channel_preview(self, drafts_tools):
        context, lifespan = create_mock_context()
        # Crash the test if any client method is invoked during preview.
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await drafts_tools["create_draft_on_channel"](
            context, channel_id="cha_abc", body="Hi there", confirm=False
        )

        assert result == {
            "preview": {
                "action": "create_draft_on_channel",
                "channel_id": "cha_abc",
                "subject": None,
                "body_preview": "Hi there",
                "to": None,
                "cc": None,
                "bcc": None,
                "mode": None,
            },
            "confirmed": False,
        }
        # elicit() is never invoked on the preview path.
        context.elicit.assert_not_called()

    async def test_create_draft_reply_preview(self, drafts_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await drafts_tools["create_draft_reply"](
            context,
            conversation_id="cnv_abc",
            body="Reply",
            channel_id="cha_xyz",
            confirm=False,
        )

        assert result["confirmed"] is False
        assert result["preview"]["action"] == "create_draft_reply"
        assert result["preview"]["channel_id"] == "cha_xyz"

    async def test_edit_draft_preview(self, drafts_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await drafts_tools["edit_draft"](
            context,
            draft_id="msg_abc",
            body="Updated body",
            channel_id="cha_xyz",
            confirm=False,
        )

        assert result["confirmed"] is False
        assert result["preview"]["action"] == "edit_draft"
        assert result["preview"]["draft_id"] == "msg_abc"

    async def test_delete_draft_preview(self, drafts_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await drafts_tools["delete_draft"](
            context, draft_id="msg_abc", confirm=False
        )

        assert result == {
            "preview": {"action": "delete_draft", "draft_id": "msg_abc"},
            "confirmed": False,
        }


# ---------------------------------------------------------------------------
# Two-step confirm — declined elicitation
# ---------------------------------------------------------------------------


class TestDeclinedElicitation:
    """When the user declines elicitation, the tool must NOT call the API."""

    async def test_delete_draft_declined(self, drafts_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked after decline")
        )

        result = await drafts_tools["delete_draft"](
            context, draft_id="msg_abc", confirm=True
        )

        assert result["confirmed"] is False
        assert result["result"] == "cancelled"
        # Elicitation WAS invoked (unlike the preview path).
        context.elicit.assert_called_once()


# ---------------------------------------------------------------------------
# Confirmed path — verify the API call shape is correct
# ---------------------------------------------------------------------------


class TestConfirmedExecution:
    """``confirm=True`` + accepted elicitation should reach the helper."""

    async def test_create_draft_on_channel_calls_helper(self, drafts_tools):
        context, lifespan = create_mock_context()
        # Build a Draft return value the helper would produce.
        returned_draft = Draft.model_validate(
            {"id": "msg_new", "subject": "Hello", "draft_mode": "shared"}
        )
        lifespan.client = AsyncMock()
        lifespan.client.drafts.create_on_channel = AsyncMock(
            return_value=returned_draft
        )

        result = await drafts_tools["create_draft_on_channel"](
            context,
            channel_id="cha_abc",
            body="Hi there",
            subject="Hello",
            mode="shared",
            confirm=True,
        )

        lifespan.client.drafts.create_on_channel.assert_awaited_once_with(
            "cha_abc",
            body="Hi there",
            author_id=None,
            subject="Hello",
            to=None,
            cc=None,
            bcc=None,
            mode="shared",
        )
        assert result["confirmed"] is True
        assert result["draft"]["id"] == "msg_new"
        assert result["draft"]["draft_mode"] == "shared"

    async def test_delete_draft_calls_helper(self, drafts_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.drafts.delete = AsyncMock(return_value=True)

        result = await drafts_tools["delete_draft"](
            context, draft_id="msg_abc", confirm=True
        )

        lifespan.client.drafts.delete.assert_awaited_once_with("msg_abc")
        assert result == {"confirmed": True, "deleted": True}


# ---------------------------------------------------------------------------
# DraftSummary projection
# ---------------------------------------------------------------------------


class TestDraftSummary:
    def test_to_draft_summary_projects_author_name_from_first_last(self):
        from frontapp_public_api_client.domain import (
            RecipientSummary,
            TeammateSummary,
        )

        draft = Draft.model_validate(
            {
                "id": "msg_abc",
                "subject": "Hi",
                "body": "<p>hi</p>",
                "draft_mode": "shared",
            }
        )
        # Re-construct with author and recipients for projection.
        author = TeammateSummary(first_name="Ada", last_name="Lovelace")
        recipient = RecipientSummary(handle="customer@example.com", role="to")
        draft = draft.model_copy(update={"author": author, "recipients": [recipient]})

        summary = to_draft_summary(draft)

        assert isinstance(summary, DraftSummary)
        assert summary.id == "msg_abc"
        assert summary.author_name == "Ada Lovelace"
        assert summary.recipients == ["customer@example.com"]
        assert summary.draft_mode == "shared"

    def test_to_draft_summary_falls_back_to_username(self):
        from frontapp_public_api_client.domain import TeammateSummary

        draft = Draft.model_validate({"id": "msg_abc"})
        author = TeammateSummary(username="ada", first_name=None, last_name=None)
        draft = draft.model_copy(update={"author": author})

        summary = to_draft_summary(draft)
        assert summary.author_name == "ada"
