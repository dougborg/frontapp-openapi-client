"""Tests for the conversations vertical: Conversations helper.

The conversations vertical is the canonical template — every other
vertical mirrors its shape. These tests cover both reads (list / search /
get / list_messages / list_comments) and mutations (reply / add_comment /
update), plus the ``_extract_page_token`` URL-parser helper.

Most of the generated response models have many required fields (Front's
spec marks status/recipient/assignee/etc. as required even though they
can be UNSET in practice). The ``_minimal_*_payload`` helpers below
build dicts that satisfy the strict ``from_dict`` schema while keeping
test cases readable.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from frontapp_public_api_client.domain import Conversation
from frontapp_public_api_client.helpers.conversations import _extract_page_token

# ---------------------------------------------------------------------------
# Payload helpers — minimal-valid responses for the strict from_dict path
# ---------------------------------------------------------------------------


def _teammate_payload(**overrides: Any) -> dict[str, Any]:
    base = {
        "_links": {"self": "https://x", "related": {}},
        "id": "tea_1",
        "email": "a@example.com",
        "username": "alice",
        "first_name": "Alice",
        "last_name": "Adams",
        "is_admin": False,
        "is_available": True,
        "is_blocked": False,
        "type": "user",
        "custom_fields": {},
    }
    base.update(overrides)
    return base


def _recipient_payload(**overrides: Any) -> dict[str, Any]:
    base = {
        "_links": {"related": {}},
        "name": None,
        "handle": "customer@example.com",
        "role": "to",
    }
    base.update(overrides)
    return base


def _conversation_payload(**overrides: Any) -> dict[str, Any]:
    """Minimal valid ``ConversationResponse``-shaped dict."""
    base: dict[str, Any] = {
        "_links": {"self": "https://x", "related": {}},
        "id": "cnv_abc",
        "subject": "Hello",
        "status": "assigned",
        "ticket_ids": [],
        "assignee": _teammate_payload(),
        "recipient": _recipient_payload(),
        "tags": [],
        "links": [],
        "custom_fields": {},
        "is_private": False,
        "scheduled_reminders": [],
        "metadata": {},
    }
    base.update(overrides)
    return base


def _comment_payload(**overrides: Any) -> dict[str, Any]:
    """Minimal valid ``CommentResponse``-shaped dict."""
    base: dict[str, Any] = {
        "_links": {"related": {}},
        "id": "com_1",
        "author": _teammate_payload(),
        "body": "Internal note",
        "attachments": [],
        "is_pinned": False,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# _extract_page_token — pagination cursor parsing
# ---------------------------------------------------------------------------


class TestExtractPageToken:
    def test_returns_none_for_no_url(self):
        assert _extract_page_token(None) is None
        assert _extract_page_token("") is None

    def test_extracts_page_token_query_param(self):
        url = "https://api.frontapp.com/conversations?page_token=abc123&limit=50"
        assert _extract_page_token(url) == "abc123"

    def test_returns_none_when_no_page_token(self):
        assert _extract_page_token("https://api.frontapp.com/conversations") is None
        assert (
            _extract_page_token("https://api.frontapp.com/conversations?limit=50")
            is None
        )

    def test_handles_malformed_url_gracefully(self):
        assert _extract_page_token("not a url") is None


# ---------------------------------------------------------------------------
# list / search / get
# ---------------------------------------------------------------------------


class TestListAndSearch:
    async def test_list_unwraps_field_results(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "_results": [
                        _conversation_payload(id="cnv_1", subject="Hello"),
                        _conversation_payload(id="cnv_2", subject="World"),
                    ],
                    "_pagination": {},
                    "_links": {},
                }
            )
        )

        convs = await client.conversations.list()
        assert len(convs) == 2
        assert all(isinstance(c, Conversation) for c in convs)
        assert [c.id for c in convs] == ["cnv_1", "cnv_2"]
        assert convs[0].subject == "Hello"

    async def test_list_passes_q_and_limit(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(
            {"_results": [], "_pagination": {}, "_links": {}}
        )
        client = attach_transport(transport)

        await client.conversations.list(q="status:open tag:urgent", limit=25)
        assert len(recorded) == 1
        assert recorded[0].url.params.get("q") == "status:open tag:urgent"
        assert recorded[0].url.params.get("limit") == "25"

    async def test_list_passes_sort_order_as_enum(
        self, attach_transport, make_recording_transport
    ):
        """``sort_order`` is a string at the helper boundary; the helper
        converts it to the generated ``ListConversationsSortOrder`` enum."""
        transport, recorded = make_recording_transport(
            {"_results": [], "_pagination": {}, "_links": {}}
        )
        client = attach_transport(transport)

        await client.conversations.list(sort_order="desc", sort_by="id")
        assert recorded[0].url.params.get("sort_order") == "desc"
        assert recorded[0].url.params.get("sort_by") == "id"

    async def test_list_returns_empty_on_no_results(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport({"_pagination": {}, "_links": {}})
        )

        convs = await client.conversations.list()
        assert convs == []

    async def test_search_uses_path_query(
        self, attach_transport, make_recording_transport
    ):
        """``search()`` puts the query in the URL path, not the q= param."""
        transport, recorded = make_recording_transport(
            {"_results": [], "_pagination": {}, "_links": {}}
        )
        client = attach_transport(transport)

        await client.conversations.search("status:open AND tag:vip")
        # Path-encoded: "status:open AND tag:vip" → status%3Aopen%20AND%20tag%3Avip
        assert "/conversations/search/" in str(recorded[0].url)
        assert "status%3Aopen" in str(recorded[0].url)
        assert "tag%3Avip" in str(recorded[0].url)

    async def test_get_returns_domain_conversation(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                _conversation_payload(
                    id="cnv_abc", subject="Order #1234", created_at=1701292639
                )
            )
        )

        conv = await client.conversations.get("cnv_abc")
        assert isinstance(conv, Conversation)
        assert conv.id == "cnv_abc"
        assert conv.subject == "Order #1234"
        # Unix-seconds → AwareDatetime via the validator on the Pydantic
        # ``Conversation`` model.
        assert isinstance(conv.created_at, datetime)
        assert conv.created_at == datetime.fromtimestamp(1701292639, tz=UTC)


# ---------------------------------------------------------------------------
# list_messages / list_comments — both return raw attrs (no projection)
# ---------------------------------------------------------------------------


class TestListSubResources:
    async def test_list_messages_returns_raw_attrs(
        self, attach_transport, make_mock_transport
    ):
        # MessageResponse has only optional fields, so a minimal dict works.
        client = attach_transport(
            make_mock_transport(
                {
                    "_results": [
                        {"id": "msg_1", "type": "email", "is_inbound": True},
                        {"id": "msg_2", "type": "email", "is_inbound": False},
                    ],
                    "_pagination": {},
                    "_links": {},
                }
            )
        )

        messages = await client.conversations.list_messages("cnv_abc")
        assert len(messages) == 2
        assert messages[0].id == "msg_1"

    async def test_list_messages_unset_results_returns_empty(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport({"_pagination": {}, "_links": {}})
        )
        messages = await client.conversations.list_messages("cnv_abc")
        assert messages == []

    async def test_list_messages_passes_limit_param(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(
            {"_results": [], "_pagination": {}, "_links": {}}
        )
        client = attach_transport(transport)
        await client.conversations.list_messages("cnv_abc", limit=10)
        assert recorded[0].url.params.get("limit") == "10"

    async def test_list_comments_returns_raw_attrs(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "_results": [_comment_payload(id="com_1", body="Note 1")],
                    "_pagination": {},
                    "_links": {},
                }
            )
        )

        comments = await client.conversations.list_comments("cnv_abc")
        assert len(comments) == 1
        assert comments[0].id == "com_1"


# ---------------------------------------------------------------------------
# Mutations: reply / add_comment / update
# ---------------------------------------------------------------------------


class TestMutations:
    async def test_reply_sends_required_body_fields(
        self, attach_transport, make_recording_transport
    ):
        # 202 response carries `{status, message_uid}` — both optional but
        # the parser still calls .json(), so we send a valid empty JSON body.
        transport, recorded = make_recording_transport({}, status=202)
        client = attach_transport(transport)

        await client.conversations.reply(
            "cnv_abc", body="Thanks for reaching out.", author_id="tea_xyz"
        )
        assert recorded[0].method == "POST"
        body = json.loads(recorded[0].content)
        assert body["body"] == "Thanks for reaching out."
        assert body["author_id"] == "tea_xyz"
        assert "subject" not in body  # optional, omitted

    async def test_reply_omits_optional_fields(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport({}, status=202)
        client = attach_transport(transport)

        await client.conversations.reply("cnv_abc", body="Plain")
        body = json.loads(recorded[0].content)
        assert body == {"body": "Plain"}

    async def test_reply_includes_recipients_when_provided(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport({}, status=202)
        client = attach_transport(transport)

        await client.conversations.reply(
            "cnv_abc",
            body="Hi",
            to=["a@x.com"],
            cc=["b@x.com"],
            bcc=["c@x.com"],
            subject="Re: Order",
        )
        body = json.loads(recorded[0].content)
        assert body["to"] == ["a@x.com"]
        assert body["cc"] == ["b@x.com"]
        assert body["bcc"] == ["c@x.com"]
        assert body["subject"] == "Re: Order"

    async def test_add_comment_minimum_body(
        self, attach_transport, make_recording_transport
    ):
        # add_comment returns 201 with the created comment; send a minimally
        # valid CommentResponse-shaped payload.
        transport, recorded = make_recording_transport(_comment_payload(), status=201)
        client = attach_transport(transport)

        await client.conversations.add_comment("cnv_abc", body="Internal note")
        body = json.loads(recorded[0].content)
        assert body == {"body": "Internal note"}

    async def test_add_comment_with_author_id(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(_comment_payload(), status=201)
        client = attach_transport(transport)

        await client.conversations.add_comment(
            "cnv_abc", body="VIP customer", author_id="tea_xyz"
        )
        body = json.loads(recorded[0].content)
        assert body == {"body": "VIP customer", "author_id": "tea_xyz"}

    async def test_update_with_status_serializes_enum(
        self, attach_transport, make_recording_transport
    ):
        """Helper accepts plain string ``"archived"`` and converts to the
        generated ``UpdateConversationStatus`` enum."""
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        await client.conversations.update("cnv_abc", status="archived")
        body = json.loads(recorded[0].content)
        assert body == {"status": "archived"}

    async def test_update_with_assignee_and_inbox(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        await client.conversations.update(
            "cnv_abc", assignee_id="tea_xyz", inbox_id="inb_def"
        )
        body = json.loads(recorded[0].content)
        assert body["assignee_id"] == "tea_xyz"
        assert body["inbox_id"] == "inb_def"
        assert "status" not in body

    async def test_update_with_tag_ids_replaces_full_set(
        self, attach_transport, make_recording_transport
    ):
        """Important contrast with ``apply_to_conversation`` /
        ``remove_from_conversation`` on the tags vertical — ``update(tag_ids=...)``
        REPLACES the full set."""
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        await client.conversations.update("cnv_abc", tag_ids=["tag_1", "tag_2"])
        body = json.loads(recorded[0].content)
        assert body == {"tag_ids": ["tag_1", "tag_2"]}

    async def test_update_with_no_changes_still_calls_api_with_empty_body(
        self, attach_transport, make_recording_transport
    ):
        """Helper doesn't validate emptiness — that's the MCP tool's job."""
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        await client.conversations.update("cnv_abc")
        body = json.loads(recorded[0].content)
        assert body == {}


# ---------------------------------------------------------------------------
# Property — lazy and cached
# ---------------------------------------------------------------------------


class TestConversationsProperty:
    def test_property_lazy_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.conversations
        second = client.conversations
        assert first is second
