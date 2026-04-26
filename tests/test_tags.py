"""Tests for the tags vertical: Tag domain model + Tags helper."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import httpx
import pydantic
import pytest

from frontapp_public_api_client.domain import Tag

# ---------------------------------------------------------------------------
# Domain model: Tag
# ---------------------------------------------------------------------------


class TestTagDomain:
    def test_minimal_payload_validates(self):
        t = Tag.model_validate({"id": "tag_abc", "name": "urgent"})
        assert t.id == "tag_abc"
        assert t.name == "urgent"
        assert t.description is None
        assert t.highlight is None
        assert t.is_private is False
        assert t.is_visible_in_conversation_lists is False
        assert t.created_at is None

    def test_unix_timestamp_converts_to_aware_datetime(self):
        t = Tag.model_validate(
            {"id": "tag_abc", "name": "urgent", "created_at": 1701292639}
        )
        assert isinstance(t.created_at, datetime)
        assert t.created_at == datetime.fromtimestamp(1701292639, tz=UTC)

    def test_extra_fields_ignored(self):
        t = Tag.model_validate(
            {
                "id": "tag_abc",
                "name": "urgent",
                "_links": {"self": "https://api2.frontapp.com/tags/tag_abc"},
            }
        )
        assert t.id == "tag_abc"

    def test_frozen(self):
        t = Tag.model_validate({"id": "tag_abc", "name": "urgent"})
        with pytest.raises(pydantic.ValidationError):
            t.id = "tag_xyz"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Helper: Tags
# ---------------------------------------------------------------------------


class TestTagsHelper:
    """Helper-level integration via ``httpx.MockTransport``."""

    def _mock_response(
        self, payload: dict | list | None, status: int = 200
    ) -> httpx.MockTransport:
        def handler(_request: httpx.Request) -> httpx.Response:
            if payload is None:
                return httpx.Response(status, content=b"")
            return httpx.Response(status, json=payload)

        return httpx.MockTransport(handler)

    def _mock_recording(
        self, payload: dict | list | None, status: int = 200
    ) -> tuple[httpx.MockTransport, list[httpx.Request]]:
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            if payload is None:
                return httpx.Response(status, content=b"")
            return httpx.Response(status, json=payload)

        return httpx.MockTransport(handler), recorded

    async def test_list_returns_domain_tags(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(
                    {
                        "_results": [
                            {
                                "_links": {"self": "https://x", "related": {}},
                                "id": "tag_1",
                                "name": "urgent",
                                "description": None,
                                "highlight": None,
                                "is_private": False,
                                "is_visible_in_conversation_lists": False,
                            },
                            {
                                "_links": {"self": "https://x", "related": {}},
                                "id": "tag_2",
                                "name": "vip",
                                "description": None,
                                "highlight": None,
                                "is_private": False,
                                "is_visible_in_conversation_lists": False,
                            },
                        ],
                        "_pagination": {},
                        "_links": {},
                    }
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        tags = await client.tags.list()
        assert len(tags) == 2
        assert all(isinstance(t, Tag) for t in tags)
        assert [t.name for t in tags] == ["urgent", "vip"]

    async def test_get_returns_tag_with_timestamps(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(
                    {
                        "_links": {"self": "https://x", "related": {}},
                        "id": "tag_abc",
                        "name": "urgent",
                        "description": None,
                        "highlight": "red",
                        "is_private": False,
                        "is_visible_in_conversation_lists": True,
                        "created_at": 1701292639,
                        "updated_at": 1701292700,
                    }
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        tag = await client.tags.get("tag_abc")
        assert tag.id == "tag_abc"
        assert tag.highlight == "red"
        assert tag.is_visible_in_conversation_lists is True
        assert isinstance(tag.created_at, datetime)

    async def test_create_serializes_highlight_enum(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording(
            {
                "_links": {"self": "https://x", "related": {}},
                "id": "tag_new",
                "name": "urgent",
                "description": None,
                "highlight": "red",
                "is_private": False,
                "is_visible_in_conversation_lists": False,
            },
            status=201,
        )
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        tag = await client.tags.create(name="urgent", highlight="red")
        assert tag.id == "tag_new"
        body = json.loads(recorded[0].content)
        assert body["name"] == "urgent"
        assert body["highlight"] == "red"

    async def test_update_skips_unset_fields(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording(None, status=204)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        success = await client.tags.update("tag_abc", name="renamed")
        assert success is True
        body = json.loads(recorded[0].content)
        assert body == {"name": "renamed"}

    async def test_delete_returns_true_on_204(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(None, status=204),
                base_url=mock_api_credentials["base_url"],
            )
        )

        success = await client.tags.delete("tag_abc")
        assert success is True

    async def test_apply_to_conversation_sends_tag_ids_list(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording(None, status=204)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        success = await client.tags.apply_to_conversation(
            "cnv_abc", tag_ids=["tag_1", "tag_2"]
        )
        assert success is True
        body = json.loads(recorded[0].content)
        assert body == {"tag_ids": ["tag_1", "tag_2"]}
        assert recorded[0].method == "POST"
        assert recorded[0].url.path.endswith("/conversations/cnv_abc/tags")

    async def test_remove_from_conversation_uses_delete(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording(None, status=204)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        success = await client.tags.remove_from_conversation(
            "cnv_abc", tag_ids=["tag_1"]
        )
        assert success is True
        assert recorded[0].method == "DELETE"
        body = json.loads(recorded[0].content)
        assert body == {"tag_ids": ["tag_1"]}

    def test_tags_property_lazy_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.tags
        second = client.tags
        assert first is second
