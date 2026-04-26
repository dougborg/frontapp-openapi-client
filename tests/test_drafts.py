"""Tests for the drafts vertical: Draft domain model + Drafts helper."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pydantic
import pytest

from frontapp_public_api_client.domain import AttachmentSummary, Draft

# ---------------------------------------------------------------------------
# Domain model: Draft
# ---------------------------------------------------------------------------


class TestDraftDomain:
    """Pydantic-level validation of the Draft projection."""

    def test_minimal_payload_validates(self):
        """A draft with only an id should validate (everything else is optional)."""
        d = Draft.model_validate({"id": "msg_abc"})
        assert d.id == "msg_abc"
        assert d.subject is None
        assert d.recipients == []
        assert d.attachments == []

    def test_unix_timestamp_converts_to_aware_datetime(self):
        """Front sends created_at as unix-seconds float; the validator converts."""
        d = Draft.model_validate({"id": "msg_abc", "created_at": 1701292639})
        assert isinstance(d.created_at, datetime)
        assert d.created_at == datetime.fromtimestamp(1701292639, tz=UTC)

    def test_iso_string_timestamp_passes_through(self):
        """An already-parsed datetime string should be accepted as-is."""
        d = Draft.model_validate(
            {"id": "msg_abc", "created_at": "2024-01-01T12:00:00+00:00"}
        )
        assert d.created_at == datetime(2024, 1, 1, 12, 0, tzinfo=UTC)

    def test_extra_fields_ignored(self):
        """Front's MessageResponse carries fields the projection doesn't surface."""
        d = Draft.model_validate(
            {
                "id": "msg_abc",
                "_links": {"self": "https://api2.frontapp.com/drafts/msg_abc"},
                "metadata": {"headers": {}},
                "signature": {"id": "sig_abc"},
            }
        )
        assert d.id == "msg_abc"
        # Should not raise; extras silently ignored.

    def test_draft_mode_literal_accepts_valid_values(self):
        for mode in ("private", "shared"):
            d = Draft.model_validate({"id": "msg_abc", "draft_mode": mode})
            assert d.draft_mode == mode

    def test_draft_mode_literal_rejects_unknown(self):
        with pytest.raises(pydantic.ValidationError):
            Draft.model_validate({"id": "msg_abc", "draft_mode": "broadcast"})

    def test_attachment_summary_projects(self):
        d = Draft.model_validate(
            {
                "id": "msg_abc",
                "attachments": [
                    {
                        "id": "fil_1",
                        "filename": "invoice.pdf",
                        "url": "https://...",
                        "content_type": "application/pdf",
                        "size": 1024,
                    }
                ],
            }
        )
        assert len(d.attachments) == 1
        assert isinstance(d.attachments[0], AttachmentSummary)
        assert d.attachments[0].filename == "invoice.pdf"

    def test_frozen(self):
        """Draft is immutable per ConfigDict(frozen=True)."""
        d = Draft.model_validate({"id": "msg_abc"})
        with pytest.raises(pydantic.ValidationError):
            d.id = "msg_xyz"  # type: ignore[misc]

    def test_type_alias_field(self):
        """``type`` is a Python keyword; the field uses an alias."""
        d = Draft.model_validate({"id": "msg_abc", "type": "email"})
        assert d.type_ == "email"


# ---------------------------------------------------------------------------
# Helper: client.drafts.list_for_conversation (raw_array unwrap)
# ---------------------------------------------------------------------------


class TestDraftsHelper:
    """Helper-level integration via httpx.MockTransport.

    The drafts vertical is the first to add helper tests under tests/; the
    conversations vertical landed without unit tests. Future verticals should
    follow this pattern.
    """

    def _mock_response(
        self, payload: list[dict] | dict, status: int = 200
    ) -> httpx.MockTransport:
        """Build a MockTransport that returns ``payload`` for every request."""

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status, json=payload)

        return httpx.MockTransport(handler)

    @pytest.fixture
    def drafts_client(self, mock_api_credentials):
        """A FrontappClient whose transport will be patched per test."""
        from frontapp_public_api_client import FrontappClient

        return FrontappClient(**mock_api_credentials)

    async def test_list_for_conversation_unwraps_field_results(
        self, mock_api_credentials
    ):
        """list_conversation_drafts returns the standard field_results wrapper.

        Despite api-facts.yaml's raw_array classification (a known classifier
        quirk), the runtime parsed type is ListConversationDraftsResponse200
        with the field_results wrapper.
        """
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(
                    {
                        "_results": [
                            {"id": "msg_1", "type": "email", "is_inbound": False},
                            {"id": "msg_2", "type": "email", "is_inbound": False},
                        ],
                        "_pagination": {},
                        "_links": {},
                    }
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        drafts = await client.drafts.list_for_conversation("cnv_abc")
        assert len(drafts) == 2
        assert [d.id for d in drafts] == ["msg_1", "msg_2"]

    async def test_list_for_conversation_empty(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(
                    {"_results": [], "_pagination": {}, "_links": {}}
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        drafts = await client.drafts.list_for_conversation("cnv_abc")
        assert drafts == []

    async def test_create_on_channel_returns_domain_draft(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        client.set_async_httpx_client(
            httpx.AsyncClient(
                transport=self._mock_response(
                    {
                        "id": "msg_new",
                        "type": "email",
                        "is_inbound": False,
                        "draft_mode": "shared",
                        "subject": "Hello",
                        "body": "<p>Hi there</p>",
                        "blurb": "Hi there",
                        "created_at": 1701292639,
                    }
                ),
                base_url=mock_api_credentials["base_url"],
            )
        )

        draft = await client.drafts.create_on_channel(
            "cha_abc",
            body="<p>Hi there</p>",
            subject="Hello",
            mode="shared",
        )
        assert isinstance(draft, Draft)
        assert draft.id == "msg_new"
        assert draft.draft_mode == "shared"
        # Unix-seconds → AwareDatetime via the validator.
        assert isinstance(draft.created_at, datetime)

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

        success = await client.drafts.delete("msg_abc")
        assert success is True

    def test_drafts_property_lazy_caches(self, mock_api_credentials):
        """``client.drafts`` returns the same Drafts instance across calls."""
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.drafts
        second = client.drafts
        assert first is second
