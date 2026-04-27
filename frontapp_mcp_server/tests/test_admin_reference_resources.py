"""Tests for the workspace-admin reference resources (#80, #81, #82).

Covers ``frontapp://me``, ``frontapp://custom_fields``, and
``frontapp://teams``. Uses a real ``FrontappClient`` with an
``httpx.MockTransport`` so the unwrap path through the generated
client code is exercised end-to-end (rather than mocking at the
helper boundary, which doesn't exist for these reference resources —
they call the generated ``api/<tag>`` modules directly).
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest
from frontapp_mcp.resources.reference import register_resources

from frontapp_public_api_client import FrontappClient


@pytest.fixture
async def make_client():
    """Factory: build a FrontappClient with a mocked httpx transport.

    Yields a callable that takes a request handler and returns a
    fully-configured ``FrontappClient``. Every client created via the
    factory is closed automatically on test teardown so the underlying
    ``httpx.AsyncClient`` doesn't leak (the unclosed-client warning was
    flagged on PR #94 review).
    """
    created: list[FrontappClient] = []

    def factory(handler) -> FrontappClient:
        client = FrontappClient(
            api_key="test-key", base_url="https://api.frontapp.test"
        )
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=httpx.MockTransport(handler),
                base_url="https://api.frontapp.test",
            )
        )
        created.append(client)
        return client

    yield factory

    for client in created:
        await client.get_async_httpx_client().aclose()


def _make_context(client: FrontappClient):
    """Mock FastMCP context whose lifespan exposes the given client."""
    context = MagicMock()
    context.request_context = MagicMock()
    context.request_context.lifespan_context = MagicMock()
    context.request_context.lifespan_context.client = client
    return context


def _capture_resources(register_fn) -> dict[str, Any]:
    """Run ``register_fn(mcp)`` against a FakeMCP and return ``{uri: callable}``."""
    captured: dict[str, Any] = {}

    class FakeMCP:
        def resource(self, **kwargs):
            uri = kwargs["uri"]

            def decorator(fn):
                captured[uri] = fn
                return fn

            return decorator

    register_fn(FakeMCP())
    return captured


@pytest.fixture
def resources():
    return _capture_resources(register_resources)


# ---------------------------------------------------------------------------
# frontapp://me
# ---------------------------------------------------------------------------


class TestMeResource:
    async def test_returns_workspace_identity(self, resources, make_client):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/me"
            return httpx.Response(
                200,
                json={
                    "_links": {"self": "https://api.frontapp.test/me"},
                    "id": "cmp_k30",
                    "name": "Dunder Mifflin Paper Company, Inc.",
                },
            )

        context = _make_context(make_client(handler))
        body = await resources["frontapp://me"](context)
        parsed = json.loads(body)
        # The resource wraps the single identity in a list for consistency
        # with the other JSON-array reference resources.
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["id"] == "cmp_k30"
        assert parsed[0]["name"] == "Dunder Mifflin Paper Company, Inc."


# ---------------------------------------------------------------------------
# frontapp://custom_fields
# ---------------------------------------------------------------------------


class TestCustomFieldsResource:
    async def test_combines_all_seven_scopes(self, resources, make_client):
        # Each scope has its own URL path; we return distinct fake fields per
        # scope so the test asserts the resource correctly tags each.
        scope_paths = {
            "/custom_fields": "global",
            "/accounts/custom_fields": "account",
            "/contacts/custom_fields": "contact",
            "/conversations/custom_fields": "conversation",
            "/inboxes/custom_fields": "inbox",
            "/links/custom_fields": "link",
            "/teammates/custom_fields": "teammate",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            scope = scope_paths.get(request.url.path)
            assert scope is not None, f"unexpected path: {request.url.path}"
            return httpx.Response(
                200,
                json={
                    "_links": {"self": str(request.url)},
                    "_results": [
                        {
                            "_links": {"self": "x", "related": {}},
                            "id": f"cf_{scope}",
                            "name": f"{scope}-field",
                            "description": f"a {scope}-scoped field",
                            "type": "string",
                        }
                    ],
                },
            )

        context = _make_context(make_client(handler))
        body = await resources["frontapp://custom_fields"](context)
        parsed = json.loads(body)

        # All 7 scopes should be present, each with one field.
        assert set(parsed.keys()) == {
            "global",
            "account",
            "contact",
            "conversation",
            "inbox",
            "link",
            "teammate",
        }
        for scope in parsed:
            assert len(parsed[scope]) == 1
            assert parsed[scope][0]["id"] == f"cf_{scope}"
            assert parsed[scope][0]["name"] == f"{scope}-field"

    async def test_empty_results_per_scope_handled(self, resources, make_client):
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={"_links": {"self": "x"}, "_results": []},
            )

        context = _make_context(make_client(handler))
        body = await resources["frontapp://custom_fields"](context)
        parsed = json.loads(body)
        # Every scope key still present, just empty.
        assert set(parsed.keys()) == {
            "global",
            "account",
            "contact",
            "conversation",
            "inbox",
            "link",
            "teammate",
        }
        for scope in parsed:
            assert parsed[scope] == []


# ---------------------------------------------------------------------------
# frontapp://teams
# ---------------------------------------------------------------------------


class TestTeamsResource:
    async def test_returns_team_refs(self, resources, make_client):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/teams"
            return httpx.Response(
                200,
                json={
                    "_links": {"self": "https://api.frontapp.test/teams"},
                    "_results": [
                        {
                            "_links": {"self": "x", "related": {}},
                            "id": "tim_support",
                            "name": "Support",
                        },
                        {
                            "_links": {"self": "y", "related": {}},
                            "id": "tim_sales",
                            "name": "Sales",
                        },
                    ],
                },
            )

        context = _make_context(make_client(handler))
        body = await resources["frontapp://teams"](context)
        parsed = json.loads(body)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert {row["id"] for row in parsed} == {"tim_support", "tim_sales"}
        assert {row["name"] for row in parsed} == {"Support", "Sales"}

    async def test_empty_workspace_returns_empty_list(self, resources, make_client):
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"_links": {"self": "x"}, "_results": []})

        context = _make_context(make_client(handler))
        body = await resources["frontapp://teams"](context)
        parsed = json.loads(body)
        assert parsed == []
