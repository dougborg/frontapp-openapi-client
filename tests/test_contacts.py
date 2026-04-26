"""Tests for the contacts vertical: Contact domain model + Contacts helper."""

from __future__ import annotations

import httpx
import pydantic
import pytest

from frontapp_public_api_client.domain import (
    Contact,
    ContactGroupRef,
    ContactHandle,
    ContactNote,
)

# ---------------------------------------------------------------------------
# Domain model: Contact
# ---------------------------------------------------------------------------


class TestContactDomain:
    def test_minimal_payload_validates(self):
        c = Contact.model_validate({"id": "crd_abc"})
        assert c.id == "crd_abc"
        assert c.handles == []
        assert c.groups == []
        assert c.lists == []
        assert c.custom_fields == {}

    def test_handles_projection(self):
        c = Contact.model_validate(
            {
                "id": "crd_abc",
                "handles": [
                    {"handle": "a@example.com", "source": "email"},
                    {"handle": "+15551234", "source": "phone"},
                ],
            }
        )
        assert len(c.handles) == 2
        assert all(isinstance(h, ContactHandle) for h in c.handles)
        assert c.handles[0].source == "email"
        assert c.handles[1].handle == "+15551234"

    def test_handle_source_literal_rejects_unknown(self):
        with pytest.raises(pydantic.ValidationError):
            Contact.model_validate(
                {
                    "id": "crd_abc",
                    "handles": [{"handle": "x", "source": "telegraph"}],
                }
            )

    def test_groups_and_lists_project_to_ref(self):
        c = Contact.model_validate(
            {
                "id": "crd_abc",
                "groups": [{"id": "grp_1", "name": "VIP", "is_private": False}],
                "lists": [{"id": "lst_1", "name": "Newsletter"}],
            }
        )
        assert isinstance(c.groups[0], ContactGroupRef)
        assert c.groups[0].name == "VIP"
        assert c.lists[0].name == "Newsletter"

    def test_extra_fields_ignored(self):
        c = Contact.model_validate(
            {
                "id": "crd_abc",
                "_links": {"self": "https://api2.frontapp.com/contacts/crd_abc"},
                "avatar_url": "https://...",
            }
        )
        assert c.id == "crd_abc"
        assert c.avatar_url == "https://..."

    def test_frozen(self):
        c = Contact.model_validate({"id": "crd_abc"})
        with pytest.raises(pydantic.ValidationError):
            c.id = "crd_xyz"  # type: ignore[misc]


class TestContactNoteDomain:
    def test_unix_timestamp_converts(self):
        from datetime import UTC, datetime

        n = ContactNote.model_validate(
            {
                "id": "not_1",
                "body": "VIP customer",
                "created_at": 1701292639,
            }
        )
        assert isinstance(n.created_at, datetime)
        assert n.created_at == datetime.fromtimestamp(1701292639, tz=UTC)


# ---------------------------------------------------------------------------
# Helper: Contacts
# ---------------------------------------------------------------------------


class TestContactsHelper:
    """Helper-level integration via httpx.MockTransport.

    Mirrors tests/test_drafts.py — uses set_async_httpx_client to inject
    a MockTransport so we exercise the full request-construction path
    without hitting the network.
    """

    def _mock_response(
        self, payload: dict | list, status: int = 200
    ) -> httpx.MockTransport:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status, json=payload)

        return httpx.MockTransport(handler)

    def _mock_recording(
        self, payload: dict | list, status: int = 200
    ) -> tuple[httpx.MockTransport, list[httpx.Request]]:
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(status, json=payload)

        return httpx.MockTransport(handler), recorded

    async def test_list_unwraps_field_results(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(
                    {
                        "_results": [
                            {"id": "crd_1", "name": "Alice"},
                            {"id": "crd_2", "name": "Bob"},
                        ],
                        "_pagination": {},
                        "_links": {},
                    }
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        contacts = await client.contacts.list()
        assert [c.id for c in contacts] == ["crd_1", "crd_2"]
        assert all(isinstance(c, Contact) for c in contacts)

    async def test_search_by_email_passes_q_param(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording(
            {"_results": [], "_pagination": {}, "_links": {}}
        )
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        await client.contacts.search_by_email("a@example.com")
        assert len(recorded) == 1
        assert recorded[0].url.params.get("q") == "a@example.com"

    async def test_get_returns_domain_contact(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(
                    {
                        "id": "crd_abc",
                        "name": "Alice",
                        "handles": [{"handle": "a@example.com", "source": "email"}],
                    }
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        contact = await client.contacts.get("crd_abc")
        assert isinstance(contact, Contact)
        assert contact.id == "crd_abc"
        assert contact.handles[0].handle == "a@example.com"

    async def test_create_sends_handles_and_returns_contact(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording(
            {"id": "crd_new", "name": "Alice", "handles": []}, status=201
        )
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        contact = await client.contacts.create(
            handles=[{"handle": "a@example.com", "source": "email"}],
            name="Alice",
        )
        assert isinstance(contact, Contact)
        assert contact.id == "crd_new"
        # Body should round-trip the handle structure.
        import json

        body = json.loads(recorded[0].content)
        assert body["handles"] == [{"handle": "a@example.com", "source": "email"}]
        assert body["name"] == "Alice"

    async def test_create_handles_tuple_form(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording({"id": "crd_new"}, status=201)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        await client.contacts.create(
            handles=[("a@example.com", "email"), ("+15551234", "phone")]
        )
        import json

        body = json.loads(recorded[0].content)
        assert len(body["handles"]) == 2

    async def test_create_handles_rejects_bad_shape(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response({}),
                base_url=mock_api_credentials["base_url"],
            )
        )

        with pytest.raises(TypeError):
            await client.contacts.create(handles=["just a string"])

    async def test_update_skips_handles(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording({}, status=204)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        success = await client.contacts.update(
            "crd_abc", name="Alice Updated", description="VIP"
        )
        assert success is True
        import json

        body = json.loads(recorded[0].content)
        assert body == {"name": "Alice Updated", "description": "VIP"}
        assert "handles" not in body

    async def test_merge_returns_contact(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording(
            {"id": "crd_target", "name": "Merged"}, status=200
        )
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        contact = await client.contacts.merge(
            contact_ids=["crd_1", "crd_2"], target_contact_id="crd_target"
        )
        assert isinstance(contact, Contact)
        assert contact.id == "crd_target"
        import json

        body = json.loads(recorded[0].content)
        assert body["contact_ids"] == ["crd_1", "crd_2"]
        assert body["target_contact_id"] == "crd_target"

    async def test_add_handle_serializes_source_enum(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording({}, status=204)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        success = await client.contacts.add_handle(
            "crd_abc", handle="b@example.com", source="email"
        )
        assert success is True
        import json

        body = json.loads(recorded[0].content)
        assert body == {"handle": "b@example.com", "source": "email"}

    async def test_delete_handle_with_force(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        transport, recorded = self._mock_recording({}, status=204)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        await client.contacts.delete_handle(
            "crd_abc", handle="b@example.com", source="email", force=True
        )
        import json

        body = json.loads(recorded[0].content)
        assert body == {
            "handle": "b@example.com",
            "source": "email",
            "force": True,
        }

    async def test_add_note_requires_author(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        # Status 200 (not 201) skips _parse_response so we don't have to mock
        # the full nested ContactNoteResponses shape; this test asserts the
        # request body only.
        transport, recorded = self._mock_recording({}, status=200)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=transport, base_url=mock_api_credentials["base_url"]
            )
        )

        await client.contacts.add_note(
            "crd_abc", body="VIP customer", author_id="tea_xyz"
        )
        import json

        body = json.loads(recorded[0].content)
        assert body == {"author_id": "tea_xyz", "body": "VIP customer"}

    async def test_list_notes_handles_202_status(self, mock_api_credentials):
        """list_notes returns HTTP 202, not 200 — verify unwrap dispatches correctly."""
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(
                    {"_results": [], "_pagination": {}, "_links": {}},
                    status=202,
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        notes = await client.contacts.list_notes("crd_abc")
        assert notes == []

    async def test_delete_returns_true_on_204(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda req: httpx.Response(204, content=b"")
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        success = await client.contacts.delete("crd_abc")
        assert success is True

    def test_contacts_property_lazy_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.contacts
        second = client.contacts
        assert first is second
