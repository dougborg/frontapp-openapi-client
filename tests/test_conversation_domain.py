"""Tests for the ``Conversation`` Pydantic domain model.

The domain model is the boundary where Front's wire shape (epoch
timestamps, attrs ``UNSET`` sentinels, mixed-case status strings) gets
normalized for application code. These tests pin the contract:

- unix-seconds floats convert to UTC-aware ``datetime``s
- already-parsed ``datetime`` and ISO strings pass through
- unknown fields are silently dropped (``extra="ignore"``)
- the model is immutable after construction (``frozen=True``)
- nested ``TagSummary`` / ``TeammateSummary`` / ``RecipientSummary``
  validate correctly from generated-API to-dict output
"""

from __future__ import annotations

from datetime import UTC, datetime

import pydantic
import pytest

from frontapp_public_api_client.domain import (
    Conversation,
    RecipientSummary,
    TagSummary,
    TeammateSummary,
)


class TestTimestampValidator:
    def test_unix_seconds_converts_to_aware_datetime(self):
        c = Conversation.model_validate({"id": "cnv_a", "created_at": 1701292639})
        assert isinstance(c.created_at, datetime)
        assert c.created_at == datetime.fromtimestamp(1701292639, tz=UTC)
        assert c.created_at.tzinfo is UTC

    def test_unix_seconds_float_works(self):
        c = Conversation.model_validate({"id": "cnv_a", "updated_at": 1701292639.5})
        assert isinstance(c.updated_at, datetime)

    def test_already_parsed_datetime_passes_through(self):
        existing = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        c = Conversation.model_validate({"id": "cnv_a", "created_at": existing})
        assert c.created_at == existing

    def test_iso_string_parses(self):
        c = Conversation.model_validate(
            {"id": "cnv_a", "created_at": "2024-01-01T12:00:00+00:00"}
        )
        assert c.created_at == datetime(2024, 1, 1, 12, 0, tzinfo=UTC)

    def test_none_remains_none(self):
        c = Conversation.model_validate({"id": "cnv_a"})
        assert c.created_at is None
        assert c.updated_at is None
        assert c.waiting_since is None

    def test_validator_runs_on_all_three_timestamp_fields(self):
        c = Conversation.model_validate(
            {
                "id": "cnv_a",
                "created_at": 1700000000,
                "updated_at": 1700001000,
                "waiting_since": 1700002000,
            }
        )
        assert isinstance(c.created_at, datetime)
        assert isinstance(c.updated_at, datetime)
        assert isinstance(c.waiting_since, datetime)


class TestExtraFields:
    def test_unknown_fields_silently_ignored(self):
        """extra=ignore — Front's response includes _links, metadata, scheduled_reminders
        etc. that aren't in the projection."""
        c = Conversation.model_validate(
            {
                "id": "cnv_a",
                "_links": {"self": "https://x"},
                "metadata": {"headers": {}},
                "scheduled_reminders": [],
                "ticket_ids": ["tic_1"],  # Not in projection — ignored.
                "totally_made_up_field": 42,
            }
        )
        assert c.id == "cnv_a"
        # Should not raise; not assertable that the extras are absent —
        # extra="ignore" silently drops them.

    def test_no_unknown_attribute_appears_on_instance(self):
        c = Conversation.model_validate({"id": "cnv_a", "totally_made_up_field": 42})
        with pytest.raises(AttributeError):
            _ = c.totally_made_up_field  # type: ignore[attr-defined]


class TestImmutability:
    def test_frozen_blocks_id_assignment(self):
        c = Conversation.model_validate({"id": "cnv_a"})
        with pytest.raises(pydantic.ValidationError):
            c.id = "cnv_b"  # type: ignore[misc]

    def test_frozen_blocks_status_assignment(self):
        c = Conversation.model_validate({"id": "cnv_a", "status": "archived"})
        with pytest.raises(pydantic.ValidationError):
            c.status = "open"  # type: ignore[misc]


class TestNestedTypes:
    def test_assignee_projects_to_teammate_summary(self):
        c = Conversation.model_validate(
            {
                "id": "cnv_a",
                "assignee": {
                    "id": "tea_a",
                    "username": "alice",
                    "first_name": "Alice",
                    "is_admin": False,
                    "is_available": True,
                },
            }
        )
        assert isinstance(c.assignee, TeammateSummary)
        assert c.assignee.id == "tea_a"
        assert c.assignee.username == "alice"

    def test_tags_project_to_tag_summary_list(self):
        c = Conversation.model_validate(
            {
                "id": "cnv_a",
                "tags": [
                    {"id": "tag_1", "name": "urgent", "highlight": "red"},
                    {"id": "tag_2", "name": "vip"},
                ],
            }
        )
        assert len(c.tags) == 2
        assert all(isinstance(t, TagSummary) for t in c.tags)
        assert c.tags[0].name == "urgent"
        assert c.tags[0].highlight == "red"

    def test_recipient_projects_to_recipient_summary(self):
        c = Conversation.model_validate(
            {
                "id": "cnv_a",
                "recipient": {
                    "name": "Bob",
                    "handle": "b@example.com",
                    "role": "to",
                },
            }
        )
        assert isinstance(c.recipient, RecipientSummary)
        assert c.recipient.handle == "b@example.com"

    def test_empty_tags_default_to_empty_list(self):
        c = Conversation.model_validate({"id": "cnv_a"})
        assert c.tags == []

    def test_optional_assignee_can_be_none(self):
        c = Conversation.model_validate({"id": "cnv_a"})
        assert c.assignee is None
