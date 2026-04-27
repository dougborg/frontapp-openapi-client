"""Tests for the workspace-admin closeout helpers (#86, #93).

Helper-level coverage of the small Tier 3 verticals shipped together:

- ``client.teams.{list, get, add_teammates, remove_teammates}`` (#86)
- ``client.applications.trigger_event`` (#93)

The rules surface (#84) is a reference resource only — its tests live
in ``frontapp_mcp_server/tests/test_admin_reference_resources.py``.
"""

from __future__ import annotations

import json

import httpx
import pytest

from frontapp_public_api_client.helpers.applications import Applications
from frontapp_public_api_client.helpers.teams import Teams
from frontapp_public_api_client.models.team_response import TeamResponse


def _team_preview_payload(id_: str = "tim_1", name: str = "Support") -> dict:
    """Slim TeamPreviewResponse — required: _links, id, name."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "name": name,
    }


def _team_full_payload(id_: str = "tim_1", name: str = "Support") -> dict:
    """Full TeamResponse — required: _links, id, name, inboxes, members."""
    return {
        "_links": {"self": "https://x", "related": {}},
        "id": id_,
        "name": name,
        "inboxes": [],
        "members": [],
    }


# ---------------------------------------------------------------------------
# Teams helper (#86)
# ---------------------------------------------------------------------------


class TestTeamsHelper:
    async def test_list_returns_field_results(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                {
                    "_links": {"self": "x"},
                    "_results": [
                        _team_preview_payload("tim_1", "Support"),
                        _team_preview_payload("tim_2", "Sales"),
                    ],
                }
            )
        )
        teams = await client.teams.list()
        assert {t.id for t in teams} == {"tim_1", "tim_2"}
        assert {t.name for t in teams} == {"Support", "Sales"}

    async def test_get_returns_full_team_response(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(make_mock_transport(_team_full_payload()))
        team = await client.teams.get("tim_1")
        assert isinstance(team, TeamResponse)
        assert team.id == "tim_1"
        assert team.name == "Support"

    async def test_add_teammates_sends_correct_body(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(204)

        client = attach_transport(httpx.MockTransport(handler))
        result = await client.teams.add_teammates("tim_1", ["tea_a", "tea_b"])
        assert result is True
        assert recorded[0].method == "POST"
        assert recorded[0].url.path == "/teams/tim_1/teammates"
        body = json.loads(recorded[0].content)
        assert body == {"teammate_ids": ["tea_a", "tea_b"]}

    async def test_remove_teammates_sends_correct_body(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(204)

        client = attach_transport(httpx.MockTransport(handler))
        result = await client.teams.remove_teammates("tim_1", ["tea_a"])
        assert result is True
        assert recorded[0].method == "DELETE"
        assert recorded[0].url.path == "/teams/tim_1/teammates"


class TestTeamsWiring:
    def test_client_teams_returns_helper(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        assert isinstance(client.teams, Teams)

    def test_lazy_property_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        assert client.teams is client.teams


# ---------------------------------------------------------------------------
# Applications helper (#93)
# ---------------------------------------------------------------------------


class TestApplicationsHelper:
    async def test_trigger_event_with_id_sends_correct_payload(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(204)

        client = attach_transport(httpx.MockTransport(handler))
        result = await client.applications.trigger_event(
            "app_xyz",
            event_type="customer_replied",
            app_object_id="cnv_abc",
        )
        assert result is True
        assert recorded[0].method == "POST"
        assert recorded[0].url.path == "/applications/app_xyz/events"
        body = json.loads(recorded[0].content)
        assert body["event_type"] == "customer_replied"
        assert body["app_object"]["id"] == "cnv_abc"

    async def test_trigger_event_with_ext_link(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(204)

        client = attach_transport(httpx.MockTransport(handler))
        await client.applications.trigger_event(
            "app_xyz",
            event_type="external_event",
            app_object_ext_link="https://example.com/issue/42",
        )
        body = json.loads(recorded[0].content)
        assert body["app_object"]["ext_link"] == "https://example.com/issue/42"


class TestApplicationsWiring:
    def test_client_applications_returns_helper(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        assert isinstance(client.applications, Applications)


# Suppress unused-import warning when pytest collects without running every test
_ = pytest
