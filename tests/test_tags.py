"""Tests for the tags vertical: Tag domain model + Tags helper."""

from __future__ import annotations

import json
from datetime import UTC, datetime

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


def _tag_payload(**overrides) -> dict:
    """Minimal valid TagResponse-shaped dict."""
    base = {
        "_links": {"self": "https://x", "related": {}},
        "id": "tag_abc",
        "name": "urgent",
        "description": None,
        "highlight": None,
        "is_private": False,
        "is_visible_in_conversation_lists": False,
    }
    base.update(overrides)
    return base


class TestTagsHelper:
    async def test_list_returns_domain_tags(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "_results": [
                        _tag_payload(id="tag_1", name="urgent"),
                        _tag_payload(id="tag_2", name="vip"),
                    ],
                    "_pagination": {},
                    "_links": {},
                }
            )
        )

        tags = await client.tags.list()
        assert len(tags) == 2
        assert all(isinstance(t, Tag) for t in tags)
        assert [t.name for t in tags] == ["urgent", "vip"]

    async def test_get_returns_tag_with_timestamps(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                _tag_payload(
                    highlight="red",
                    is_visible_in_conversation_lists=True,
                    created_at=1701292639,
                    updated_at=1701292700,
                )
            )
        )

        tag = await client.tags.get("tag_abc")
        assert tag.id == "tag_abc"
        assert tag.highlight == "red"
        assert tag.is_visible_in_conversation_lists is True
        assert isinstance(tag.created_at, datetime)

    async def test_create_serializes_highlight_enum(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(
            _tag_payload(id="tag_new", highlight="red"),
            status=201,
        )
        client = attach_transport(transport)

        tag = await client.tags.create(name="urgent", highlight="red")
        assert tag.id == "tag_new"
        body = json.loads(recorded[0].content)
        assert body["name"] == "urgent"
        assert body["highlight"] == "red"

    async def test_update_skips_unset_fields(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        success = await client.tags.update("tag_abc", name="renamed")
        assert success is True
        body = json.loads(recorded[0].content)
        assert body == {"name": "renamed"}

    async def test_delete_returns_true_on_204(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(make_mock_transport(None, status=204))

        success = await client.tags.delete("tag_abc")
        assert success is True

    async def test_apply_to_conversation_sends_tag_ids_list(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        success = await client.tags.apply_to_conversation(
            "cnv_abc", tag_ids=["tag_1", "tag_2"]
        )
        assert success is True
        body = json.loads(recorded[0].content)
        assert body == {"tag_ids": ["tag_1", "tag_2"]}
        assert recorded[0].method == "POST"
        assert recorded[0].url.path.endswith("/conversations/cnv_abc/tags")

    async def test_remove_from_conversation_uses_delete(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

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
