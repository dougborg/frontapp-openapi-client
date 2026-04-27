"""Tests for MCP knowledge_bases tools (#83).

Covers the 6 read tools (no confirm) and the 4 contribute mutations
(two-step confirm). The drafts-only policy is the most important
property — these tests pin that:

- ``create_kb_article`` always passes ``status="draft"`` to the helper,
  with no way for the agent to override.
- ``update_kb_article`` calls the helper with ``status=None`` (the
  helper treats this as "omit the field from the PATCH body, preserving
  the existing publication state") — agents cannot flip
  draft↔published.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from frontapp_mcp.projections import KbArticleSummary, KbCategoryRef, KbRef
from frontapp_mcp.tools.knowledge_bases import register_tools

from .conftest import create_mock_context


@pytest.fixture
def kb_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_tools)


def _attrs_with_to_dict(payload: dict):
    """Mock attrs response with a ``to_dict()`` returning ``payload``."""
    obj = MagicMock()
    obj.to_dict = lambda: payload
    return obj


# ---------------------------------------------------------------------------
# Read tools — projection + delegation
# ---------------------------------------------------------------------------


class TestRead:
    async def test_list_knowledge_bases_projects(self, kb_tools):
        context, lifespan = create_mock_context()
        kb = MagicMock()
        kb.id = "knb_1"
        kb.type_ = MagicMock(value="external")
        kb.locales = ["en"]
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.list = AsyncMock(return_value=[kb])

        result = await kb_tools["list_knowledge_bases"](context)
        assert len(result) == 1
        assert isinstance(result[0], KbRef)
        assert result[0].id == "knb_1"
        assert result[0].type == "external"

    async def test_get_kb_returns_dict(self, kb_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.get = AsyncMock(
            return_value=_attrs_with_to_dict({"id": "knb_1", "name": "Public KB"})
        )
        result = await kb_tools["get_kb"](
            context, knowledge_base_id="knb_1", with_content=True
        )
        assert result["id"] == "knb_1"
        assert result["name"] == "Public KB"
        # Confirm we threaded with_content/locale through.
        call = lifespan.client.knowledge_bases.get.await_args
        assert call is not None
        assert call.kwargs["with_content"] is True

    async def test_list_kb_articles_projects_each(self, kb_tools):
        context, lifespan = create_mock_context()
        article = MagicMock()
        article.id = "kba_1"
        article.slug = "how-to"
        article.locales = ["en"]
        article.updated_at = 1700000000.0
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.list_articles = AsyncMock(
            return_value=[article]
        )

        result = await kb_tools["list_kb_articles"](context, knowledge_base_id="knb_1")
        assert len(result) == 1
        assert isinstance(result[0], KbArticleSummary)
        assert result[0].id == "kba_1"
        assert result[0].slug == "how-to"

    async def test_list_kb_articles_in_category(self, kb_tools):
        context, lifespan = create_mock_context()
        a = MagicMock()
        a.id = "kba_1"
        a.slug = "x"
        a.locales = ["en"]
        a.updated_at = None
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.list_articles_in_category = AsyncMock(
            return_value=[a]
        )

        result = await kb_tools["list_kb_articles_in_category"](
            context, category_id="kbc_1"
        )
        assert len(result) == 1
        assert result[0].id == "kba_1"

    async def test_get_kb_article_returns_dict(self, kb_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.get_article = AsyncMock(
            return_value=_attrs_with_to_dict(
                {"id": "kba_1", "name": "Hello", "content": "<p>body</p>"}
            )
        )

        result = await kb_tools["get_kb_article"](context, article_id="kba_1")
        assert result["id"] == "kba_1"
        assert result["content"] == "<p>body</p>"
        # Default with_content=True for this tool
        call = lifespan.client.knowledge_bases.get_article.await_args
        assert call is not None
        assert call.kwargs["with_content"] is True

    async def test_list_kb_categories_projects(self, kb_tools):
        context, lifespan = create_mock_context()
        cat = MagicMock()
        cat.id = "kbc_1"
        cat.slug = "security"
        cat.is_hidden = False
        cat.locales = ["en"]
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.list_categories = AsyncMock(return_value=[cat])

        result = await kb_tools["list_kb_categories"](
            context, knowledge_base_id="knb_1"
        )
        assert isinstance(result[0], KbCategoryRef)
        assert result[0].slug == "security"
        assert result[0].is_hidden is False


# ---------------------------------------------------------------------------
# create_kb_article — DRAFTS ONLY policy
# ---------------------------------------------------------------------------


class TestCreateArticleDraftsOnly:
    async def test_preview_path_does_not_call_helper(self, kb_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await kb_tools["create_kb_article"](
            context,
            knowledge_base_id="knb_1",
            subject="Hello",
            content="body",
            confirm=False,
        )
        assert result["confirmed"] is False
        # The preview surfaces status: "draft" so the human sees what
        # publication state will result.
        assert result["preview"]["status"] == "draft"
        context.elicit.assert_not_called()

    async def test_confirmed_calls_helper_with_draft_status(self, kb_tools):
        """The MCP layer's drafts-only policy: status='draft' is hardcoded
        regardless of any value the agent might try to pass. The tool
        signature has no `status` parameter."""
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.create_article = AsyncMock(
            return_value=_attrs_with_to_dict({"id": "kba_new", "status": "draft"})
        )

        result = await kb_tools["create_kb_article"](
            context,
            knowledge_base_id="knb_1",
            subject="Hello",
            content="body",
            confirm=True,
        )

        assert result["confirmed"] is True
        call = lifespan.client.knowledge_bases.create_article.await_args
        assert call is not None
        # The crucial assertion for the drafts-only policy.
        assert call.kwargs["status"] == "draft"

    async def test_tool_signature_has_no_status_arg(self, kb_tools):
        """Belt-and-suspenders: even if a future change tries to add a
        status arg, this test catches it."""
        import inspect

        sig = inspect.signature(kb_tools["create_kb_article"])
        assert "status" not in sig.parameters


# ---------------------------------------------------------------------------
# update_kb_article — never flips publication state
# ---------------------------------------------------------------------------


class TestUpdateArticleDraftsOnly:
    async def test_preview_path_does_not_call_helper(self, kb_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await kb_tools["update_kb_article"](
            context, article_id="kba_1", subject="new title", confirm=False
        )
        assert result["confirmed"] is False
        # The preview note clarifies that status is preserved.
        assert "status unchanged" in result["preview"]["note"]

    async def test_confirmed_calls_helper_with_status_none(self, kb_tools):
        """The MCP layer's drafts-only update policy: status=None is
        passed to the helper, which omits it from the PATCH body —
        preserving whatever publication state the article had."""
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.update_article = AsyncMock(
            return_value=_attrs_with_to_dict({"id": "kba_1"})
        )

        await kb_tools["update_kb_article"](
            context, article_id="kba_1", subject="edited", confirm=True
        )

        call = lifespan.client.knowledge_bases.update_article.await_args
        assert call is not None
        assert call.kwargs["status"] is None

    async def test_tool_signature_has_no_status_arg(self, kb_tools):
        import inspect

        sig = inspect.signature(kb_tools["update_kb_article"])
        assert "status" not in sig.parameters


# ---------------------------------------------------------------------------
# Categories — standard preview/confirm flow
# ---------------------------------------------------------------------------


class TestCategoryMutations:
    async def test_create_kb_category_preview(self, kb_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        result = await kb_tools["create_kb_category"](
            context,
            knowledge_base_id="knb_1",
            name="Security",
            confirm=False,
        )
        assert result["confirmed"] is False
        assert result["preview"]["name"] == "Security"

    async def test_create_kb_category_confirmed(self, kb_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.create_category = AsyncMock(
            return_value=_attrs_with_to_dict({"id": "kbc_new", "name": "Security"})
        )

        result = await kb_tools["create_kb_category"](
            context,
            knowledge_base_id="knb_1",
            name="Security",
            confirm=True,
        )
        assert result["confirmed"] is True
        call = lifespan.client.knowledge_bases.create_category.await_args
        assert call is not None
        assert call.kwargs["name"] == "Security"

    async def test_update_kb_category_omits_unset_fields(self, kb_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.knowledge_bases.update_category = AsyncMock(
            return_value=_attrs_with_to_dict({"id": "kbc_1", "name": "Renamed"})
        )

        await kb_tools["update_kb_category"](
            context, category_id="kbc_1", name="Renamed", confirm=True
        )
        call = lifespan.client.knowledge_bases.update_category.await_args
        assert call is not None
        assert call.kwargs["name"] == "Renamed"
        assert call.kwargs["description"] is None


# ---------------------------------------------------------------------------
# Decline path
# ---------------------------------------------------------------------------


class TestDeclinedElicitation:
    async def test_create_article_declined_does_not_call_helper(self, kb_tools):
        context, lifespan = create_mock_context(elicit_confirm=False)
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked after decline")
        )

        result = await kb_tools["create_kb_article"](
            context,
            knowledge_base_id="knb_1",
            subject="x",
            content="y",
            confirm=True,
        )
        assert result["confirmed"] is False
        assert result["result"] == "cancelled"
        context.elicit.assert_called_once()
