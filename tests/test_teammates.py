"""Tests for the teammates vertical: Teammate domain model + Teammates helper."""

from __future__ import annotations

import json

import pydantic
import pytest

from frontapp_public_api_client.domain import Inbox, Teammate

# ---------------------------------------------------------------------------
# Domain model: Teammate
# ---------------------------------------------------------------------------


class TestTeammateDomain:
    def test_required_fields_minimum(self):
        t = Teammate.model_validate(
            {"id": "tea_abc", "email": "a@x.com", "username": "alice"}
        )
        assert t.id == "tea_abc"
        assert t.email == "a@x.com"
        assert t.username == "alice"
        assert t.is_admin is False
        assert t.is_available is True
        assert t.is_blocked is False

    def test_extra_fields_ignored(self):
        t = Teammate.model_validate(
            {
                "id": "tea_abc",
                "email": "a@x.com",
                "username": "alice",
                "_links": {"self": "https://x"},
                "custom_fields": {"region": "us"},
            }
        )
        assert t.id == "tea_abc"

    def test_type_field_passes_through(self):
        t = Teammate.model_validate(
            {"id": "tea_a", "email": "a@x.com", "username": "a", "type": "user"}
        )
        assert t.type == "user"

    def test_frozen(self):
        t = Teammate.model_validate(
            {"id": "tea_abc", "email": "a@x.com", "username": "alice"}
        )
        with pytest.raises(pydantic.ValidationError):
            t.id = "tea_xyz"  # type: ignore[misc]

    def test_missing_required_field_rejected(self):
        with pytest.raises(pydantic.ValidationError):
            Teammate.model_validate({"id": "tea_abc"})  # no email/username


# ---------------------------------------------------------------------------
# Helper: Teammates
# ---------------------------------------------------------------------------


def _teammate_payload(**overrides) -> dict:
    """Minimal valid TeammateResponse-shaped dict (mirrors test_conversations.py)."""
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


class TestTeammatesHelper:
    async def test_list_returns_domain_teammates(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "_results": [
                        _teammate_payload(id="tea_1", username="alice"),
                        _teammate_payload(id="tea_2", username="bob"),
                    ],
                    "_pagination": {},
                    "_links": {},
                }
            )
        )

        teammates = await client.teammates.list()
        assert len(teammates) == 2
        assert all(isinstance(t, Teammate) for t in teammates)
        assert [t.username for t in teammates] == ["alice", "bob"]

    async def test_get_returns_full_teammate(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                _teammate_payload(
                    id="tea_abc", username="charlie", is_admin=True, is_available=False
                )
            )
        )

        teammate = await client.teammates.get("tea_abc")
        assert teammate.id == "tea_abc"
        assert teammate.is_admin is True
        assert teammate.is_available is False

    async def test_list_inboxes_returns_domain_inboxes(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "_results": [
                        {"id": "inb_1", "name": "Support"},
                        {"id": "inb_2", "name": "Sales"},
                    ],
                    "_pagination": {},
                    "_links": {},
                }
            )
        )

        inboxes = await client.teammates.list_inboxes("tea_abc")
        assert len(inboxes) == 2
        assert all(isinstance(i, Inbox) for i in inboxes)

    async def test_list_assigned_conversations_passes_q_filter(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(
            {"_results": [], "_pagination": {}, "_links": {}}
        )
        client = attach_transport(transport)

        await client.teammates.list_assigned_conversations(
            "tea_abc", q="status:open", limit=25
        )
        assert "/teammates/tea_abc/conversations" in str(recorded[0].url)
        assert recorded[0].url.params.get("q") == "status:open"
        assert recorded[0].url.params.get("limit") == "25"

    async def test_update_skips_unset_fields(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        success = await client.teammates.update("tea_abc", first_name="Alicia")
        assert success is True
        body = json.loads(recorded[0].content)
        assert body == {"first_name": "Alicia"}
        # Email and other read-only fields not in the body.
        assert "email" not in body
        assert "is_admin" not in body

    async def test_update_with_is_available_flag(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        await client.teammates.update("tea_abc", is_available=False)
        body = json.loads(recorded[0].content)
        assert body == {"is_available": False}

    async def test_update_returns_false_on_non_2xx(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport({"_error": {"message": "not found"}}, status=404)
        )

        # update_teammate uses is_success which returns False for non-2xx;
        # the helper doesn't raise.
        success = await client.teammates.update("tea_missing", first_name="x")
        assert success is False

    def test_teammates_property_lazy_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.teammates
        second = client.teammates
        assert first is second

    # -- iter_assigned_conversations ----------------------------------------

    async def test_iter_assigned_conversations_walks_pages(self, attach_transport):
        import httpx

        def _conv(id_: str) -> dict:
            # Minimal shape the unwrap path needs — list_assigned_conversations
            # returns ConversationResponse items, but we only ever read .id /
            # url so we don't need full TeammateResponse on assignee.
            return {
                "_links": {"self": "https://x", "related": {}},
                "id": id_,
                "subject": id_,
                "status": "assigned",
                "ticket_ids": [],
                "assignee": _teammate_payload(),
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

        recorded: list[httpx.Request] = []
        call = {"i": 0}
        pages = [
            {
                "_results": [_conv("cnv_1")],
                "_pagination": {
                    "next": "https://api.frontapp.test/teammates/tea_a/conversations?page_token=P2"
                },
                "_links": {},
            },
            {
                "_results": [_conv("cnv_2")],
                "_pagination": {"next": None},
                "_links": {},
            },
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            idx = call["i"]
            call["i"] += 1
            return httpx.Response(200, json=pages[idx])

        client = attach_transport(httpx.MockTransport(handler))

        items = [c async for c in client.teammates.iter_assigned_conversations("tea_a")]
        assert [c.id for c in items] == ["cnv_1", "cnv_2"]
        assert "/teammates/tea_a/conversations" in str(recorded[0].url)
        assert recorded[1].url.params.get("page_token") == "P2"
