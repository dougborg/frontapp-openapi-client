"""Tests for the knowledge_bases vertical: KnowledgeBases helper.

Covers the read + contribute path. The helper hides two generated-API
quirks (the `_a_` infix on 11 modules and the locale-default vs
locale-specified split); these tests pin both:

- Locale routing: ``locale=None`` hits default-locale endpoints;
  ``locale='fr'`` hits specified-locale endpoints (verified by the
  mocked URL path).
- ``with_content`` routing on get / get_article / get_category.
- ``create_article`` defaults to ``status='draft'`` and accepts
  ``status='published'`` (helper-level — the MCP tool layer is what
  locks down draft-only).
- ``update_article`` with ``status=None`` omits `status` from the
  PATCH body (preserving the existing publication state).
- Pagination: `iter_articles` walks `_pagination.next` correctly.
"""

from __future__ import annotations

import json

import httpx
import pytest

from frontapp_public_api_client.helpers.knowledge_bases import KnowledgeBases
from frontapp_public_api_client.models.knowledge_base_article_response import (
    KnowledgeBaseArticleResponse,
)
from frontapp_public_api_client.models.knowledge_base_article_slim_response import (
    KnowledgeBaseArticleSlimResponse,
)
from frontapp_public_api_client.models.knowledge_base_category_response import (
    KnowledgeBaseCategoryResponse,
)
from frontapp_public_api_client.models.knowledge_base_slim_response import (
    KnowledgeBaseSlimResponse,
)

# ---------------------------------------------------------------------------
# Test fixtures + helpers
# ---------------------------------------------------------------------------


def _kb_payload(id_: str = "knb_1") -> dict:
    """Slim KB shape — required: _links, id, type, locales."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "type": "external",
        "locales": ["en"],
    }


def _kb_full_payload(id_: str = "knb_1", name: str = "Public KB") -> dict:
    """Full KB shape — required: _links, id, name, status, type, locale."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "name": name,
        "status": "published",
        "type": "external",
        "locale": "en",
    }


def _article_slim_payload(id_: str = "kba_1", slug: str = "how-to") -> dict:
    """Slim article shape — required: _links, id, slug, locales."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "slug": slug,
        "locales": ["en"],
    }


def _article_full_payload(
    id_: str = "kba_1", subject: str = "How to", body: str = "<p>body</p>"
) -> dict:
    """Full article shape — required: _links, id, slug, name, status,
    keywords, content, locale, attachments."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "slug": subject.lower().replace(" ", "-"),
        "name": subject,
        "status": "draft",
        "keywords": [],
        "content": body,
        "locale": "en",
        "attachments": [],
    }


def _category_slim_payload(id_: str = "kbc_1", slug: str = "cat") -> dict:
    """Slim category shape — required: _links, id, slug, is_hidden, locales."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "slug": slug,
        "is_hidden": False,
        "locales": ["en"],
    }


def _category_full_payload(id_: str = "kbc_1", name: str = "Cat") -> dict:
    """Full category shape — required: _links, id, name, description,
    is_hidden, locale."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "name": name,
        "description": "desc",
        "is_hidden": False,
        "locale": "en",
    }


def _record(transport_handler):
    """Wrap a handler so we can record the request URL + method + body."""
    recorded: list[httpx.Request] = []

    def wrapper(request: httpx.Request) -> httpx.Response:
        recorded.append(request)
        return transport_handler(request)

    return httpx.MockTransport(wrapper), recorded


# ---------------------------------------------------------------------------
# list / get KB
# ---------------------------------------------------------------------------


class TestListAndGetKb:
    async def test_list_returns_field_results(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {"_links": {"self": "x"}, "_results": [_kb_payload("knb_1")]}
            )
        )
        kbs = await client.knowledge_bases.list()
        assert len(kbs) == 1
        assert kbs[0].id == "knb_1"
        # Slim KB doesn't carry a name — only id, type, locales.
        # `with_content=True` get is required to retrieve the workspace name.

    async def test_get_slim_default(self, attach_transport, make_mock_transport):
        client = attach_transport(make_mock_transport(_kb_payload()))
        kb = await client.knowledge_bases.get("knb_1")
        assert isinstance(kb, KnowledgeBaseSlimResponse)
        assert kb.id == "knb_1"

    async def test_get_with_content_default_locale_routes_to_content_endpoint(
        self, attach_transport
    ):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/knowledge_bases/knb_1/content"
            return httpx.Response(200, json=_kb_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        kb = await client.knowledge_bases.get("knb_1", with_content=True)
        assert kb.id == "knb_1"
        assert kb.name == "Public KB"

    async def test_get_with_content_specified_locale_routes_correctly(
        self, attach_transport
    ):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/knowledge_bases/knb_1/locales/fr/content"
            return httpx.Response(200, json=_kb_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        kb = await client.knowledge_bases.get("knb_1", with_content=True, locale="fr")
        assert kb.id == "knb_1"


# ---------------------------------------------------------------------------
# Articles — list / iter / get
# ---------------------------------------------------------------------------


class TestArticles:
    async def test_list_returns_slim_articles(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "_links": {"self": "x"},
                    "_results": [_article_slim_payload("kba_1")],
                }
            )
        )
        articles = await client.knowledge_bases.list_articles("knb_1")
        assert len(articles) == 1
        assert articles[0].id == "kba_1"

    async def test_iter_walks_pagination(self, attach_transport):
        page1 = {
            "_links": {"self": "x"},
            "_results": [_article_slim_payload("kba_1")],
            "_pagination": {
                "next": "https://api.frontapp.test/knowledge_bases/knb_1/articles?page_token=PG2"
            },
        }
        page2 = {
            "_links": {"self": "x"},
            "_results": [_article_slim_payload("kba_2")],
            "_pagination": {"next": None},
        }
        call_count = {"i": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            i = call_count["i"]
            call_count["i"] += 1
            return httpx.Response(200, json=page1 if i == 0 else page2)

        client = attach_transport(httpx.MockTransport(handler))
        ids = [a.id async for a in client.knowledge_bases.iter_articles("knb_1")]
        assert ids == ["kba_1", "kba_2"]

    async def test_list_in_category(self, attach_transport, make_mock_transport):
        client = attach_transport(
            make_mock_transport(
                {
                    "_links": {"self": "x"},
                    "_results": [_article_slim_payload("kba_5")],
                }
            )
        )
        articles = await client.knowledge_bases.list_articles_in_category("kbc_1")
        assert len(articles) == 1
        assert articles[0].id == "kba_5"

    async def test_get_article_slim(self, attach_transport, make_mock_transport):
        client = attach_transport(make_mock_transport(_article_slim_payload()))
        article = await client.knowledge_bases.get_article("kba_1")
        assert isinstance(article, KnowledgeBaseArticleSlimResponse)

    async def test_get_article_with_content_routes_to_content_endpoint(
        self, attach_transport
    ):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/knowledge_base_articles/kba_1/content"
            return httpx.Response(200, json=_article_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        article = await client.knowledge_bases.get_article("kba_1", with_content=True)
        assert isinstance(article, KnowledgeBaseArticleResponse)

    async def test_get_article_with_specified_locale_routes_correctly(
        self, attach_transport
    ):
        def handler(request: httpx.Request) -> httpx.Response:
            assert (
                request.url.path == "/knowledge_base_articles/kba_1/locales/fr/content"
            )
            return httpx.Response(200, json=_article_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        article = await client.knowledge_bases.get_article(
            "kba_1", with_content=True, locale="fr"
        )
        assert article.id == "kba_1"


# ---------------------------------------------------------------------------
# Articles — create / update
# ---------------------------------------------------------------------------


class TestCreateArticle:
    async def test_defaults_to_draft_status(self, attach_transport):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/knowledge_bases/knb_1/articles"
            body = json.loads(request.content)
            assert body["status"] == "draft"
            assert body["subject"] == "Hello"
            assert body["content"] == "<p>body</p>"
            return httpx.Response(201, json=_article_full_payload(id_="kba_new"))

        client = attach_transport(httpx.MockTransport(handler))
        article = await client.knowledge_bases.create_article(
            "knb_1", subject="Hello", content="<p>body</p>"
        )
        assert article.id == "kba_new"

    async def test_published_status_passes_through(self, attach_transport):
        """Helper level retains status kwarg for library callers
        (Python scripts can publish programmatically). MCP tool
        layer is the safety boundary."""

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["status"] == "published"
            return httpx.Response(201, json=_article_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        await client.knowledge_bases.create_article(
            "knb_1", subject="x", content="y", status="published"
        )

    async def test_specified_locale_routes_correctly(self, attach_transport):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/knowledge_bases/knb_1/locales/fr/articles"
            return httpx.Response(201, json=_article_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        await client.knowledge_bases.create_article(
            "knb_1", subject="x", content="y", locale="fr"
        )


class TestUpdateArticle:
    async def test_status_none_omits_field(self, attach_transport):
        """The update tool's drafts-only policy depends on this:
        omitting status preserves the existing publication state."""

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            body = json.loads(request.content)
            assert "status" not in body
            assert body["subject"] == "edited"
            return httpx.Response(200, json=_article_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        await client.knowledge_bases.update_article("kba_1", subject="edited")

    async def test_specified_locale_routes_correctly(self, attach_transport):
        def handler(request: httpx.Request) -> httpx.Response:
            assert (
                request.url.path == "/knowledge_base_articles/kba_1/locales/de/content"
            )
            return httpx.Response(200, json=_article_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        await client.knowledge_bases.update_article("kba_1", subject="x", locale="de")


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


class TestCategories:
    async def test_list(self, attach_transport, make_mock_transport):
        client = attach_transport(
            make_mock_transport(
                {
                    "_links": {"self": "x"},
                    "_results": [_category_slim_payload("kbc_1")],
                }
            )
        )
        cats = await client.knowledge_bases.list_categories("knb_1")
        assert len(cats) == 1
        assert cats[0].id == "kbc_1"

    async def test_iter_walks_pagination(self, attach_transport):
        page1 = {
            "_links": {"self": "x"},
            "_results": [_category_slim_payload("kbc_1")],
            "_pagination": {
                "next": "https://api.frontapp.test/knowledge_bases/knb_1/categories?page_token=N"
            },
        }
        page2 = {
            "_links": {"self": "x"},
            "_results": [_category_slim_payload("kbc_2")],
            "_pagination": {"next": None},
        }
        call_count = {"i": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            i = call_count["i"]
            call_count["i"] += 1
            return httpx.Response(200, json=page1 if i == 0 else page2)

        client = attach_transport(httpx.MockTransport(handler))
        ids = [c.id async for c in client.knowledge_bases.iter_categories("knb_1")]
        assert ids == ["kbc_1", "kbc_2"]

    async def test_create_with_required_name(self, attach_transport):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["name"] == "Security"
            assert request.url.path == "/knowledge_bases/knb_1/categories"
            return httpx.Response(201, json=_category_full_payload(id_="kbc_new"))

        client = attach_transport(httpx.MockTransport(handler))
        cat = await client.knowledge_bases.create_category("knb_1", name="Security")
        assert isinstance(cat, KnowledgeBaseCategoryResponse)
        assert cat.id == "kbc_new"

    async def test_create_with_specified_locale_routes_correctly(
        self, attach_transport
    ):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/knowledge_bases/knb_1/locales/es/categories"
            return httpx.Response(201, json=_category_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        await client.knowledge_bases.create_category(
            "knb_1", name="Seguridad", locale="es"
        )

    async def test_update_only_name(self, attach_transport):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            body = json.loads(request.content)
            assert body == {"name": "Renamed"}
            return httpx.Response(200, json=_category_full_payload())

        client = attach_transport(httpx.MockTransport(handler))
        await client.knowledge_bases.update_category("kbc_1", name="Renamed")


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------


class TestWiring:
    def test_client_property_returns_helper(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        assert isinstance(client.knowledge_bases, KnowledgeBases)

    def test_lazy_property_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.knowledge_bases
        second = client.knowledge_bases
        assert first is second


# Suppress unused-import warning when pytest collects without running every test
_ = pytest
