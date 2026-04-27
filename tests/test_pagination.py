"""Tests for the auto-pagination iterator (helpers/base.py).

Pins ADR-003's contract:
- ``extract_page_token`` correctly pulls the cursor from Front's
  ``_pagination.next`` URL.
- ``_paginate`` walks pages until exhausted, ``max_pages`` trips, or
  ``max_items`` trips — yielding partial final pages on the items cap.
- The cursor is fed back as ``page_token=`` on each subsequent call.
- Per-helper ``iter_all`` wrappers project to domain models.
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from frontapp_public_api_client.domain import Conversation, Tag
from frontapp_public_api_client.helpers.base import extract_page_token

# ---------------------------------------------------------------------------
# extract_page_token
# ---------------------------------------------------------------------------


class TestExtractPageToken:
    def test_returns_none_for_no_url(self):
        assert extract_page_token(None) is None
        assert extract_page_token("") is None

    def test_extracts_token_query_param(self):
        url = "https://api.frontapp.com/conversations?page_token=abc123&limit=50"
        assert extract_page_token(url) == "abc123"

    def test_url_encoded_token_decodes(self):
        url = "https://api.frontapp.com/conversations?page_token=abc%2F123"
        assert extract_page_token(url) == "abc/123"

    def test_returns_none_when_param_absent(self):
        assert extract_page_token("https://api.frontapp.com/conversations") is None
        assert (
            extract_page_token("https://api.frontapp.com/conversations?limit=50")
            is None
        )

    def test_handles_malformed_url(self):
        assert extract_page_token("not a url") is None


# ---------------------------------------------------------------------------
# Multi-page mock transport
#
# Sends one response per request, indexed by call count. Page N includes a
# ``_pagination.next`` pointing at the next page (until the last, which
# omits it).
# ---------------------------------------------------------------------------


def _conv_payload(id_: str) -> dict:
    """Minimal valid ConversationResponse-shaped dict (mirrors the helper
    payloads in test_conversations.py)."""
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


def _multi_page_transport(
    pages: list[dict],
) -> tuple[httpx.MockTransport, list[httpx.Request]]:
    """Build a transport that returns ``pages[i]`` on the i-th request.

    The caller is responsible for setting ``_pagination.next`` URLs that
    embed the right ``page_token`` if multi-page behavior is intended.
    """
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
# _paginate via Conversations.iter_all
# ---------------------------------------------------------------------------


class TestIterAllConversations:
    async def test_walks_two_pages_to_exhaustion(self, attach_transport):
        page1 = {
            "_results": [_conv_payload("cnv_1"), _conv_payload("cnv_2")],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations?page_token=PAGE2"
            },
            "_links": {},
        }
        page2 = {
            "_results": [_conv_payload("cnv_3")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1, page2])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_all()]

        assert ids == ["cnv_1", "cnv_2", "cnv_3"]
        # First request has no page_token; second has page_token=PAGE2.
        assert len(recorded) == 2
        assert "page_token" not in recorded[0].url.params
        assert recorded[1].url.params.get("page_token") == "PAGE2"

    async def test_max_items_yields_partial_page(self, attach_transport):
        """``max_items=2`` mid-page stops after yielding 2 items, never
        fetching the next page."""
        page1 = {
            "_results": [_conv_payload(f"cnv_{i}") for i in range(1, 6)],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations?page_token=PAGE2"
            },
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_all(max_items=2)]

        assert ids == ["cnv_1", "cnv_2"]
        assert len(recorded) == 1  # Did not fetch page 2.

    async def test_max_pages_stops_walking(self, attach_transport):
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations?page_token=PAGE2"
            },
            "_links": {},
        }
        page2 = {
            "_results": [_conv_payload("cnv_2")],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations?page_token=PAGE3"
            },
            "_links": {},
        }
        # Page 3 exists but should never be fetched.
        page3 = {
            "_results": [_conv_payload("cnv_3")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1, page2, page3])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_all(max_pages=2)]

        assert ids == ["cnv_1", "cnv_2"]
        assert len(recorded) == 2

    async def test_no_pagination_block_means_single_page(self, attach_transport):
        """When the response omits ``_pagination`` entirely (some endpoints
        don't paginate), iteration stops after yielding the first page."""
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_all()]

        assert ids == ["cnv_1"]
        assert len(recorded) == 1

    async def test_empty_page_with_cursor_stops_iteration(self, attach_transport):
        """Defensive: if Front returns an empty page WITH a non-null cursor
        (shouldn't happen, but observed in the wild with rapidly-mutating
        filters), treat the empty page as terminal rather than chasing the
        cursor forever and draining the rate limit."""
        # Page 1 has results + a next cursor.
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations?page_token=PAGE2"
            },
            "_links": {},
        }
        # Page 2 is empty BUT still advertises a next cursor — should stop
        # here, not chase cnv_3 (which we'd never see anyway since we'd be
        # in an infinite loop).
        page2 = {
            "_results": [],
            "_pagination": {
                "next": "https://api.frontapp.test/conversations?page_token=PAGE3"
            },
            "_links": {},
        }
        # Page 3 should never be fetched.
        page3 = {
            "_results": [_conv_payload("cnv_3")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1, page2, page3])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_all()]

        assert ids == ["cnv_1"]
        assert len(recorded) == 2  # Did not chase the cursor on the empty page.

    async def test_pagination_next_unset_stops_iteration(self, attach_transport):
        """Generated pagination model types ``next_`` as ``None | str | Unset``.
        When Front omits ``next`` from the JSON, ``next_`` deserializes to
        ``UNSET`` (not None). The cursor extractor's ``isinstance(..., str)``
        check must reject UNSET as well as None."""
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            # Empty _pagination object — `next` field is absent, so the
            # generated model leaves field_pagination.next_ as UNSET.
            "_pagination": {},
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_all()]

        assert ids == ["cnv_1"]
        assert len(recorded) == 1

    async def test_yields_domain_models(self, attach_transport):
        page1 = {
            "_results": [
                _conv_payload("cnv_1") | {"created_at": 1701292639},
            ],
            "_links": {},
        }
        transport, _ = _multi_page_transport([page1])
        client = attach_transport(transport)

        items = [c async for c in client.conversations.iter_all()]
        assert isinstance(items[0], Conversation)
        # Validator converts unix-seconds → AwareDatetime.
        assert items[0].created_at == datetime.fromtimestamp(1701292639, tz=UTC)

    async def test_passes_q_and_limit_through(self, attach_transport):
        page1 = {
            "_results": [],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1])
        client = attach_transport(transport)

        async for _ in client.conversations.iter_all(q="status:open", limit=25):
            pass

        assert recorded[0].url.params.get("q") == "status:open"
        assert recorded[0].url.params.get("limit") == "25"

    async def test_empty_first_page_stops_immediately(self, attach_transport):
        page1 = {
            "_results": [],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_all()]
        assert ids == []
        assert len(recorded) == 1

    async def test_max_items_zero_yields_nothing_but_still_fetches(
        self, attach_transport
    ):
        """``max_items=0`` is a degenerate cap — fetches one page (the
        loop hasn't checked yet) but yields nothing."""
        page1 = {
            "_results": [_conv_payload("cnv_1")],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1])
        client = attach_transport(transport)

        ids = [c.id async for c in client.conversations.iter_all(max_items=0)]
        assert ids == []
        assert len(recorded) == 1


# ---------------------------------------------------------------------------
# iter_all on other helpers — same fixture proves the wrapping is consistent
# ---------------------------------------------------------------------------


class TestIterAllOtherHelpers:
    async def test_tags_iter_all(self, attach_transport):
        page1 = {
            "_results": [_tag_payload(f"tag_{i}") for i in range(1, 4)],
            "_pagination": {"next": None},
            "_links": {},
        }
        transport, _ = _multi_page_transport([page1])
        client = attach_transport(transport)

        items = [t async for t in client.tags.iter_all()]
        assert all(isinstance(t, Tag) for t in items)
        assert [t.id for t in items] == ["tag_1", "tag_2", "tag_3"]

    async def test_contacts_iter_all_max_items(self, attach_transport):
        from frontapp_public_api_client.domain import Contact

        page1 = {
            "_results": [{"id": f"crd_{i}", "name": str(i)} for i in range(1, 6)],
            "_pagination": {"next": "https://api.frontapp.test/contacts?page_token=P2"},
            "_links": {},
        }
        transport, recorded = _multi_page_transport([page1])
        client = attach_transport(transport)

        items = [c async for c in client.contacts.iter_all(max_items=3)]
        assert all(isinstance(c, Contact) for c in items)
        assert [c.id for c in items] == ["crd_1", "crd_2", "crd_3"]
        assert len(recorded) == 1


# ---------------------------------------------------------------------------
# Module-level _extract_page_token re-export still works
# ---------------------------------------------------------------------------


def test_legacy_extract_page_token_alias():
    """The original symbol on the conversations helper still resolves so
    callers (and tests) that import the private name don't break."""
    from frontapp_public_api_client.helpers.conversations import _extract_page_token

    assert (
        _extract_page_token("https://api.frontapp.test/conversations?page_token=abc")
        == "abc"
    )
