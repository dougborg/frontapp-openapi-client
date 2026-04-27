"""Tests for the inboxes vertical: Inbox domain model + Inboxes helper."""

from __future__ import annotations

import json

import pydantic
import pytest

from frontapp_public_api_client.domain import Inbox

# ---------------------------------------------------------------------------
# Domain model: Inbox
# ---------------------------------------------------------------------------


class TestInboxDomain:
    def test_minimal_payload_validates(self):
        i = Inbox.model_validate({"id": "inb_abc", "name": "Support"})
        assert i.id == "inb_abc"
        assert i.name == "Support"
        assert i.is_private is None
        assert i.is_public is None

    def test_all_fields_optional(self):
        """InboxResponse marks every field UNSET — projection accepts {}."""
        i = Inbox.model_validate({})
        assert i.id is None
        assert i.name is None

    def test_extra_fields_ignored(self):
        i = Inbox.model_validate(
            {
                "id": "inb_abc",
                "name": "Support",
                "_links": {"self": "..."},
                "custom_fields": {"region": "us"},
            }
        )
        assert i.id == "inb_abc"

    def test_frozen(self):
        i = Inbox.model_validate({"id": "inb_abc", "name": "Support"})
        with pytest.raises(pydantic.ValidationError):
            i.id = "inb_xyz"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Helper: Inboxes
# ---------------------------------------------------------------------------


class TestInboxesHelper:
    async def test_list_returns_domain_inboxes(
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

        inboxes = await client.inboxes.list()
        assert len(inboxes) == 2
        assert all(isinstance(i, Inbox) for i in inboxes)
        assert [i.name for i in inboxes] == ["Support", "Sales"]

    async def test_get_returns_inbox(self, attach_transport, make_mock_transport):
        client = attach_transport(
            make_mock_transport(
                {
                    "id": "inb_abc",
                    "name": "Support",
                    "is_private": False,
                    "is_public": True,
                }
            )
        )

        inbox = await client.inboxes.get("inb_abc")
        assert inbox.id == "inb_abc"
        assert inbox.is_public is True

    async def test_create_sends_full_body(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(
            {"id": "inb_new", "name": "Triage"}, status=201
        )
        client = attach_transport(transport)

        inbox = await client.inboxes.create(
            name="Triage", teammate_ids=["tea_1", "tea_2"], is_public=False
        )
        assert inbox.id == "inb_new"
        body = json.loads(recorded[0].content)
        assert body["name"] == "Triage"
        assert body["teammate_ids"] == ["tea_1", "tea_2"]
        assert body["is_public"] is False

    async def test_grant_access_sends_teammate_ids(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        success = await client.inboxes.grant_access(
            "inb_abc", teammate_ids=["tea_1", "tea_2"]
        )
        assert success is True
        body = json.loads(recorded[0].content)
        assert body == {"teammate_ids": ["tea_1", "tea_2"]}
        assert recorded[0].method == "POST"

    async def test_revoke_access_uses_delete_method(
        self, attach_transport, make_recording_transport
    ):
        """Wraps the awkwardly-named generated module ``removes_inbox_access``."""
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)

        success = await client.inboxes.revoke_access("inb_abc", teammate_ids=["tea_1"])
        assert success is True
        assert recorded[0].method == "DELETE"

    def test_inboxes_property_lazy_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.inboxes
        second = client.inboxes
        assert first is second
