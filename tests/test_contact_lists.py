"""Tests for the contact_lists vertical: ContactList domain + ContactLists helper."""

from __future__ import annotations

import json

import httpx
import pydantic
import pytest

from frontapp_public_api_client.domain import Contact, ContactList

# ---------------------------------------------------------------------------
# Domain model: ContactList
# ---------------------------------------------------------------------------


class TestContactListDomain:
    def test_minimal_payload_validates(self):
        cl = ContactList.model_validate({"id": "lst_abc"})
        assert cl.id == "lst_abc"
        assert cl.name is None
        assert cl.is_private is None

    def test_full_payload(self):
        cl = ContactList.model_validate(
            {"id": "lst_abc", "name": "VIP", "is_private": False}
        )
        assert cl.id == "lst_abc"
        assert cl.name == "VIP"
        assert cl.is_private is False

    def test_extra_fields_ignored(self):
        cl = ContactList.model_validate(
            {
                "id": "lst_abc",
                "_links": {"self": "https://api2.frontapp.com/contact_lists/lst_abc"},
                "name": "VIP",
            }
        )
        assert cl.id == "lst_abc"
        assert cl.name == "VIP"

    def test_frozen(self):
        cl = ContactList.model_validate({"id": "lst_abc", "name": "VIP"})
        with pytest.raises(pydantic.ValidationError):
            cl.name = "Newsletter"


# ---------------------------------------------------------------------------
# Helper: client.contact_lists
# ---------------------------------------------------------------------------


def _list_response(items: list[dict]) -> dict:
    return {"_results": items, "_pagination": {}, "_links": {}}


class TestContactListsHelper:
    """Helper-level integration via the shared transport fixtures."""

    async def test_list_unwraps_field_results(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                _list_response(
                    [
                        {"id": "lst_1", "name": "VIP", "is_private": False},
                        {"id": "lst_2", "name": "Newsletter", "is_private": False},
                    ]
                )
            )
        )
        items = await client.contact_lists.list()
        assert [i.id for i in items] == ["lst_1", "lst_2"]
        assert all(isinstance(i, ContactList) for i in items)

    async def test_list_for_team_uses_team_path(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(_list_response([]))
        client = attach_transport(transport)
        await client.contact_lists.list_for_team("tim_xyz")
        assert recorded[0].url.path == "/teams/tim_xyz/contact_lists"

    async def test_list_for_teammate_uses_teammate_path(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(_list_response([]))
        client = attach_transport(transport)
        await client.contact_lists.list_for_teammate("tea_xyz")
        assert recorded[0].url.path == "/teammates/tea_xyz/contact_lists"

    async def test_list_members_returns_contacts(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                _list_response(
                    [
                        {"id": "crd_1", "name": "Alice", "handles": []},
                        {"id": "crd_2", "name": "Bob", "handles": []},
                    ]
                )
            )
        )
        contacts = await client.contact_lists.list_members("lst_abc")
        assert [c.id for c in contacts] == ["crd_1", "crd_2"]
        assert all(isinstance(c, Contact) for c in contacts)

    async def test_create_sends_name_and_returns_true(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_lists.create("VIP")
        assert ok is True
        assert recorded[0].url.path == "/contact_lists"
        assert json.loads(recorded[0].content) == {"name": "VIP"}

    async def test_create_for_team(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_lists.create_for_team("tim_xyz", "VIP")
        assert ok is True
        assert recorded[0].url.path == "/teams/tim_xyz/contact_lists"
        assert json.loads(recorded[0].content) == {"name": "VIP"}

    async def test_create_for_teammate(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_lists.create_for_teammate("tea_xyz", "Drafts")
        assert ok is True
        assert recorded[0].url.path == "/teammates/tea_xyz/contact_lists"

    async def test_delete(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_lists.delete("lst_abc")
        assert ok is True
        assert recorded[0].method == "DELETE"
        assert recorded[0].url.path == "/contact_lists/lst_abc"

    async def test_add_contacts_sends_contact_ids(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_lists.add_contacts(
            "lst_abc", ["crd_1", "crd_2", "alt:email:foo@x.com"]
        )
        assert ok is True
        assert recorded[0].method == "POST"
        assert recorded[0].url.path == "/contact_lists/lst_abc/contacts"
        body = json.loads(recorded[0].content)
        assert body == {"contact_ids": ["crd_1", "crd_2", "alt:email:foo@x.com"]}

    async def test_remove_contacts_sends_contact_ids(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_lists.remove_contacts("lst_abc", ["crd_1", "crd_2"])
        assert ok is True
        assert recorded[0].method == "DELETE"
        assert recorded[0].url.path == "/contact_lists/lst_abc/contacts"
        assert json.loads(recorded[0].content) == {"contact_ids": ["crd_1", "crd_2"]}

    async def test_remove_contacts_rejects_over_50(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(make_mock_transport(None, status=204))
        big_list = [f"crd_{i}" for i in range(51)]
        with pytest.raises(ValueError, match="caps remove_contacts at 50"):
            await client.contact_lists.remove_contacts("lst_abc", big_list)

    async def test_remove_contacts_accepts_aliases(
        self, attach_transport, make_recording_transport
    ):
        """Front's RemoveContactsFromList shares the same model as
        AddContactsToList, so aliases work on remove too."""
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_lists.remove_contacts(
            "lst_abc", ["alt:email:foo@x.com", "alt:phone:+15555550100"]
        )
        assert ok is True
        body = json.loads(recorded[0].content)
        assert body == {
            "contact_ids": ["alt:email:foo@x.com", "alt:phone:+15555550100"]
        }

    async def test_iter_members_walks_pages(self, attach_transport):
        """iter_members hides cursor pagination; verify it walks both pages."""
        page1_url = (
            "https://api.frontapp.test/contact_lists/lst_abc/contacts"
            "?page_token=PAGE2&limit=2"
        )

        def handler(request: httpx.Request) -> httpx.Response:
            token = request.url.params.get("page_token")
            if token == "PAGE2":
                return httpx.Response(
                    200,
                    json={
                        "_results": [
                            {"id": "crd_3", "name": "Carol", "handles": []},
                        ],
                        "_pagination": {},
                        "_links": {},
                    },
                )
            return httpx.Response(
                200,
                json={
                    "_results": [
                        {"id": "crd_1", "name": "Alice", "handles": []},
                        {"id": "crd_2", "name": "Bob", "handles": []},
                    ],
                    "_pagination": {"next": page1_url},
                    "_links": {},
                },
            )

        client = attach_transport(httpx.MockTransport(handler))
        seen = []
        async for c in client.contact_lists.iter_members("lst_abc", limit=2):
            seen.append(c.id)
        assert seen == ["crd_1", "crd_2", "crd_3"]

    def test_property_lazy_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.contact_lists
        second = client.contact_lists
        assert first is second
