"""Tests for MCP tag tools — preview/decline/execute paths + delta semantics."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.projections import TagSummary, to_tag_summary
from frontapp_mcp.tools.tags import register_tools

from frontapp_public_api_client.domain import Tag

from .conftest import create_mock_context


def _make_mcp() -> tuple[object, dict]:
    captured: dict[str, object] = {}

    class FakeMCP:
        def tool(self, **kwargs: object):
            name = kwargs["name"]

            def decorator(fn):
                captured[name] = fn
                return fn

            return decorator

    return FakeMCP(), captured


@pytest.fixture
def tags_tools() -> dict[str, object]:
    mcp, captured = _make_mcp()
    register_tools(mcp)  # type: ignore[arg-type]
    return captured


# ---------------------------------------------------------------------------
# Read tools
# ---------------------------------------------------------------------------


class TestReadTools:
    async def test_get_tag_returns_summary(self, tags_tools):
        context, lifespan = create_mock_context()
        tag = Tag.model_validate(
            {
                "id": "tag_abc",
                "name": "urgent",
                "highlight": "red",
                "is_private": False,
                "is_visible_in_conversation_lists": True,
            }
        )
        lifespan.client = AsyncMock()
        lifespan.client.tags.get = AsyncMock(return_value=tag)

        result = await tags_tools["get_tag"](context, tag_id="tag_abc")

        assert isinstance(result, TagSummary)
        assert result.id == "tag_abc"
        assert result.highlight == "red"

    async def test_list_tags_projects_each(self, tags_tools):
        context, lifespan = create_mock_context()
        tags = [
            Tag.model_validate({"id": "tag_1", "name": "urgent"}),
            Tag.model_validate({"id": "tag_2", "name": "vip"}),
        ]
        lifespan.client = AsyncMock()
        lifespan.client.tags.list = AsyncMock(return_value=tags)

        result = await tags_tools["list_tags"](context)

        assert len(result) == 2
        assert all(isinstance(t, TagSummary) for t in result)


# ---------------------------------------------------------------------------
# Mutation: preview path
# ---------------------------------------------------------------------------


class TestPreviewPath:
    @pytest.mark.parametrize(
        "tool_name,kwargs",
        [
            (
                "add_tag_to_conversation",
                {"conversation_id": "cnv_a", "tag_id": "tag_1"},
            ),
            (
                "remove_tag_from_conversation",
                {"conversation_id": "cnv_a", "tag_id": "tag_1"},
            ),
            ("create_tag", {"name": "urgent"}),
            ("create_child_tag", {"parent_tag_id": "tag_p", "name": "child"}),
            ("update_tag", {"tag_id": "tag_a", "name": "renamed"}),
            ("delete_tag", {"tag_id": "tag_a"}),
        ],
    )
    async def test_preview_returns_preview(self, tags_tools, tool_name, kwargs):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await tags_tools[tool_name](context, **kwargs, confirm=False)

        assert result["confirmed"] is False
        assert "preview" in result
        context.elicit.assert_not_called()


# ---------------------------------------------------------------------------
# Delta-vs-replace documentation in previews
# ---------------------------------------------------------------------------


class TestDeltaSemantics:
    async def test_add_tag_preview_documents_delta(self, tags_tools):
        context, _ = create_mock_context()
        result = await tags_tools["add_tag_to_conversation"](
            context, conversation_id="cnv_a", tag_id="tag_1", confirm=False
        )
        assert "delta" in result["preview"]["semantics"].lower()

    async def test_delete_tag_preview_warns_destructive(self, tags_tools):
        context, _ = create_mock_context()
        result = await tags_tools["delete_tag"](context, tag_id="tag_a", confirm=False)
        assert "PERMANENT" in result["preview"]["warning"]


# ---------------------------------------------------------------------------
# Update no-changes guard
# ---------------------------------------------------------------------------


class TestUpdateNoChanges:
    async def test_update_with_no_args_short_circuits(self, tags_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()

        result = await tags_tools["update_tag"](context, tag_id="tag_a", confirm=True)
        assert result["result"] == "no_changes_requested"
        context.elicit.assert_not_called()


# ---------------------------------------------------------------------------
# Confirmed execution
# ---------------------------------------------------------------------------


class TestConfirmedExecution:
    async def test_add_tag_calls_helper_with_list(self, tags_tools):
        """The MCP tool takes a single tag_id but wraps it into a list for the helper."""
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.tags.apply_to_conversation = AsyncMock(return_value=True)

        result = await tags_tools["add_tag_to_conversation"](
            context, conversation_id="cnv_a", tag_id="tag_1", confirm=True
        )

        lifespan.client.tags.apply_to_conversation.assert_awaited_once_with(
            "cnv_a", tag_ids=["tag_1"]
        )
        assert result == {"confirmed": True, "applied": True}

    async def test_remove_tag_calls_helper_with_list(self, tags_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.tags.remove_from_conversation = AsyncMock(return_value=True)

        result = await tags_tools["remove_tag_from_conversation"](
            context, conversation_id="cnv_a", tag_id="tag_1", confirm=True
        )

        lifespan.client.tags.remove_from_conversation.assert_awaited_once_with(
            "cnv_a", tag_ids=["tag_1"]
        )
        assert result == {"confirmed": True, "removed": True}

    async def test_create_tag_returns_summary(self, tags_tools):
        context, lifespan = create_mock_context()
        new_tag = Tag.model_validate({"id": "tag_new", "name": "urgent"})
        lifespan.client = AsyncMock()
        lifespan.client.tags.create = AsyncMock(return_value=new_tag)

        result = await tags_tools["create_tag"](
            context, name="urgent", highlight="red", confirm=True
        )

        assert result["confirmed"] is True
        assert result["tag"]["id"] == "tag_new"
        lifespan.client.tags.create.assert_awaited_once()

    async def test_delete_tag_calls_helper(self, tags_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.tags.delete = AsyncMock(return_value=True)

        result = await tags_tools["delete_tag"](context, tag_id="tag_abc", confirm=True)

        lifespan.client.tags.delete.assert_awaited_once_with("tag_abc")
        assert result == {"confirmed": True, "deleted": True}


# ---------------------------------------------------------------------------
# Decline path
# ---------------------------------------------------------------------------


class TestDeclinePath:
    async def test_delete_tag_declined(self, tags_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked after decline")
        )

        result = await tags_tools["delete_tag"](context, tag_id="tag_abc", confirm=True)
        assert result["confirmed"] is False
        assert result["result"] == "cancelled"


# ---------------------------------------------------------------------------
# TagSummary projection
# ---------------------------------------------------------------------------


class TestTagSummaryProjection:
    def test_to_tag_summary_includes_timestamps_as_iso(self):
        from datetime import UTC, datetime

        tag = Tag.model_validate(
            {
                "id": "tag_a",
                "name": "urgent",
                "created_at": 1701292639,
            }
        )
        summary = to_tag_summary(tag)
        assert summary.id == "tag_a"
        assert (
            summary.created_at == datetime.fromtimestamp(1701292639, tz=UTC).isoformat()
        )
