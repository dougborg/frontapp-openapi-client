"""Tests for the deprecated contact_groups vertical: ContactGroups helper.

contact_groups reuses ``ContactGroupRef`` from the contacts domain, so
there's no new domain-model test class — only helper-level integration
plus a check that the lazy property is wired.
"""

from __future__ import annotations

import json

import pytest

from frontapp_public_api_client.domain import Contact, ContactGroupRef


def _list_response(items: list[dict]) -> dict:
    return {"_results": items, "_pagination": {}, "_links": {}}


class TestContactGroupsHelper:
    async def test_list_returns_contact_group_refs(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                _list_response(
                    [
                        {"id": "grp_1", "name": "VIP (legacy)", "is_private": False},
                        {"id": "grp_2", "name": "Pilot", "is_private": True},
                    ]
                )
            )
        )
        items = await client.contact_groups.list()
        assert [i.id for i in items] == ["grp_1", "grp_2"]
        assert all(isinstance(i, ContactGroupRef) for i in items)
        assert items[0].name == "VIP (legacy)"

    async def test_list_for_team(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(_list_response([]))
        client = attach_transport(transport)
        await client.contact_groups.list_for_team("tim_xyz")
        assert recorded[0].url.path == "/teams/tim_xyz/contact_groups"

    async def test_list_for_teammate(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(_list_response([]))
        client = attach_transport(transport)
        await client.contact_groups.list_for_teammate("tea_xyz")
        assert recorded[0].url.path == "/teammates/tea_xyz/contact_groups"

    async def test_list_members_returns_contacts(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                _list_response([{"id": "crd_1", "name": "Alice", "handles": []}])
            )
        )
        contacts = await client.contact_groups.list_members("grp_abc")
        assert len(contacts) == 1
        assert isinstance(contacts[0], Contact)

    async def test_create_sends_name(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_groups.create("Legacy VIP")
        assert ok is True
        assert recorded[0].url.path == "/contact_groups"
        assert json.loads(recorded[0].content) == {"name": "Legacy VIP"}

    async def test_create_for_team(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        await client.contact_groups.create_for_team("tim_xyz", "Pilot")
        assert recorded[0].url.path == "/teams/tim_xyz/contact_groups"

    async def test_create_for_teammate(
        self, attach_transport, make_recording_transport
    ):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        await client.contact_groups.create_for_teammate("tea_xyz", "Personal")
        assert recorded[0].url.path == "/teammates/tea_xyz/contact_groups"

    async def test_delete(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        ok = await client.contact_groups.delete("grp_abc")
        assert ok is True
        assert recorded[0].method == "DELETE"
        assert recorded[0].url.path == "/contact_groups/grp_abc"

    async def test_add_contacts(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        await client.contact_groups.add_contacts("grp_abc", ["crd_1", "crd_2"])
        assert recorded[0].method == "POST"
        assert recorded[0].url.path == "/contact_groups/grp_abc/contacts"
        assert json.loads(recorded[0].content) == {"contact_ids": ["crd_1", "crd_2"]}

    async def test_remove_contacts(self, attach_transport, make_recording_transport):
        transport, recorded = make_recording_transport(None, status=204)
        client = attach_transport(transport)
        await client.contact_groups.remove_contacts("grp_abc", ["crd_1"])
        assert recorded[0].method == "DELETE"
        assert recorded[0].url.path == "/contact_groups/grp_abc/contacts"

    async def test_remove_contacts_rejects_over_50(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(make_mock_transport(None, status=204))
        big_list = [f"crd_{i}" for i in range(51)]
        with pytest.raises(ValueError, match="caps remove_contacts at 50"):
            await client.contact_groups.remove_contacts("grp_abc", big_list)

    def test_property_lazy_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.contact_groups
        second = client.contact_groups
        assert first is second
