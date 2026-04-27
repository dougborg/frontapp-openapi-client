"""Smoke tests for the variant ``iter_*`` wrappers added in follow-up A.

The core ``_paginate`` machinery is exhaustively tested in
``tests/test_pagination.py`` against ``Conversations.iter_all``. These
tests just verify each variant correctly:

1. forwards its path-id / query kwargs to the right generated endpoint,
2. applies the right projection (domain model vs raw attrs),
3. respects ``max_items`` (proxy for "uses _paginate at all").

One short test per new method — exhaustive matrix lives on iter_all.
"""

from __future__ import annotations

import httpx

from frontapp_public_api_client.domain import Contact, Conversation, Tag


def _conv_payload(id_: str) -> dict:
    """Minimal valid ConversationResponse-shaped dict (mirrors test_pagination.py)."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "subject": id_,
        "status": "assigned",
        "ticket_ids": [],
        "assignee": {
            "_links": {"self": "https://x", "related": {}},
            "id": "tea_1",
            "email": "a@x.com",
            "username": "a",
            "first_name": "A",
            "last_name": "A",
            "is_admin": False,
            "is_available": True,
            "is_blocked": False,
            "type": "user",
            "custom_fields": {},
        },
        "recipient": {
            "_links": {"related": {}},
            "name": None,
            "handle": "c@x.com",
            "role": "to",
        },
        "tags": [],
        "links": [],
        "custom_fields": {},
        "is_private": False,
        "scheduled_reminders": [],
        "metadata": {},
    }


def _tag_payload(id_: str) -> dict:
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "name": id_,
        "description": None,
        "highlight": None,
        "is_private": False,
        "is_visible_in_conversation_lists": False,
    }


def _multi_page(pages: list[dict]) -> tuple[httpx.MockTransport, list[httpx.Request]]:
    """Build a transport that returns ``pages[i]`` on the i-th request."""
    recorded: list[httpx.Request] = []
    call_count = {"i": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded.append(request)
        idx = call_count["i"]
        call_count["i"] += 1
        if idx >= len(pages):
            return httpx.Response(404, json={})
        return httpx.Response(200, json=pages[idx])

    return httpx.MockTransport(handler), recorded


# ---------------------------------------------------------------------------
# Conversations: iter_search, iter_messages
# ---------------------------------------------------------------------------


class TestConversationsVariants:
    async def test_iter_search_walks_pages(self, attach_transport):
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations/search/x?page_token=P2"
            },
            "_links": {},
        }
        page2 = {
            "_results": [_conv_payload("cnv_2")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1, page2])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_search("status:open")]
        assert ids == ["cnv_1", "cnv_2"]
        # Query embedded in URL path, not as ``q=``.
        assert "/conversations/search/" in str(recorded[0].url)
        assert "status%3Aopen" in str(recorded[0].url)

    async def test_iter_search_yields_domain_models(self, attach_transport):
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, _ = _multi_page([page1])
        client = attach_transport(transport)

        items = [c async for c in client.conversations.iter_search("x")]
        assert isinstance(items[0], Conversation)

    async def test_iter_messages_walks_pages_with_path_id(self, attach_transport):
        page1 = {
            "_results": [{"id": "msg_1"}, {"id": "msg_2"}],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations/cnv_a/messages?page_token=P2"
            },
            "_links": {},
        }
        page2 = {
            "_results": [{"id": "msg_3"}],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1, page2])
        client = attach_transport(transport)

        ids = [m.id async for m in client.conversations.iter_messages("cnv_a")]
        assert ids == ["msg_1", "msg_2", "msg_3"]
        # The conversation_id ends up in the URL path.
        assert "/conversations/cnv_a/messages" in str(recorded[0].url)
        assert recorded[1].url.params.get("page_token") == "P2"

    async def test_iter_messages_max_items(self, attach_transport):
        page1 = {
            "_results": [{"id": f"msg_{i}"} for i in range(1, 6)],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations/cnv_a/messages?page_token=P2"
            },
            "_links": {},
        }
        transport, recorded = _multi_page([page1])
        client = attach_transport(transport)

        ids = [
            m.id async for m in client.conversations.iter_messages("cnv_a", max_items=2)
        ]
        assert ids == ["msg_1", "msg_2"]
        assert len(recorded) == 1


# ---------------------------------------------------------------------------
# Contacts: iter_for_team, iter_for_teammate, iter_conversations
# ---------------------------------------------------------------------------


class TestContactsVariants:
    async def test_iter_for_team_uses_path_id(self, attach_transport):
        page1 = {
            "_results": [{"id": "crd_1", "name": "Alice"}],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1])
        client = attach_transport(transport)

        items = [c async for c in client.contacts.iter_for_team("tim_a")]
        assert all(isinstance(c, Contact) for c in items)
        assert "/teams/tim_a/contacts" in str(recorded[0].url)

    async def test_iter_for_teammate_uses_path_id(self, attach_transport):
        page1 = {
            "_results": [{"id": "crd_1"}],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1])
        client = attach_transport(transport)

        items = [c async for c in client.contacts.iter_for_teammate("tea_a")]
        assert len(items) == 1
        assert "/teammates/tea_a/contacts" in str(recorded[0].url)

    async def test_iter_conversations_walks_pages(self, attach_transport):
        page1 = {
            "_results": [_conv_payload("cnv_1"), _conv_payload("cnv_2")],
            "_pagination": {
                "next": "https://api.frontapp.test/contacts/crd_a/conversations?page_token=P2"
            },
            "_links": {},
        }
        page2 = {
            "_results": [_conv_payload("cnv_3")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1, page2])
        client = attach_transport(transport)

        # Yields raw attrs (no domain projection on this method).
        items = [c async for c in client.contacts.iter_conversations("crd_a")]
        assert [c.id for c in items] == ["cnv_1", "cnv_2", "cnv_3"]
        assert "/contacts/crd_a/conversations" in str(recorded[0].url)


# ---------------------------------------------------------------------------
# Tags: iter_company, iter_for_team, iter_for_teammate, iter_conversations
# ---------------------------------------------------------------------------


class TestTagsVariants:
    async def test_iter_company_yields_domain_tags(self, attach_transport):
        page1 = {
            "_results": [_tag_payload(f"tag_{i}") for i in range(1, 4)],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1])
        client = attach_transport(transport)

        items = [t async for t in client.tags.iter_company()]
        assert all(isinstance(t, Tag) for t in items)
        assert [t.id for t in items] == ["tag_1", "tag_2", "tag_3"]
        assert "/company/tags" in str(recorded[0].url)

    async def test_iter_for_team_uses_path_id(self, attach_transport):
        page1 = {
            "_results": [_tag_payload("tag_1")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1])
        client = attach_transport(transport)

        items = [t async for t in client.tags.iter_for_team("tim_a")]
        assert len(items) == 1
        assert "/teams/tim_a/tags" in str(recorded[0].url)

    async def test_iter_for_teammate_uses_path_id(self, attach_transport):
        page1 = {
            "_results": [_tag_payload("tag_1")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1])
        client = attach_transport(transport)

        items = [t async for t in client.tags.iter_for_teammate("tea_a")]
        assert len(items) == 1
        assert "/teammates/tea_a/tags" in str(recorded[0].url)

    async def test_iter_conversations_walks_pages(self, attach_transport):
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            "_pagination": {
                "next": "https://api.frontapp.test/tags/tag_a/conversations?page_token=P2"
            },
            "_links": {},
        }
        page2 = {
            "_results": [_conv_payload("cnv_2")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1, page2])
        client = attach_transport(transport)

        items = [c async for c in client.tags.iter_conversations("tag_a")]
        assert [c.id for c in items] == ["cnv_1", "cnv_2"]
        assert "/tags/tag_a/conversations" in str(recorded[0].url)


# ---------------------------------------------------------------------------
# Inboxes: iter_conversations
# ---------------------------------------------------------------------------


class TestInboxesVariants:
    async def test_iter_conversations_walks_pages(self, attach_transport):
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            "_pagination": {
                "next": "https://api.frontapp.test/inboxes/inb_a/conversations?page_token=P2"
            },
            "_links": {},
        }
        page2 = {
            "_results": [_conv_payload("cnv_2")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1, page2])
        client = attach_transport(transport)

        items = [c async for c in client.inboxes.iter_conversations("inb_a")]
        assert [c.id for c in items] == ["cnv_1", "cnv_2"]
        assert "/inboxes/inb_a/conversations" in str(recorded[0].url)

    async def test_iter_conversations_passes_q_filter(self, attach_transport):
        page1 = {
            "_results": [],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page([page1])
        client = attach_transport(transport)

        async for _ in client.inboxes.iter_conversations("inb_a", q="status:open"):
            pass

        assert recorded[0].url.params.get("q") == "status:open"
