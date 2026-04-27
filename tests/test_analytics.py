"""Tests for the analytics vertical: Analytics helper (create→poll loop).

Front's analytics endpoints are server-side async — POST returns
immediately with ``status: "running"``; a follow-up GET polls until
``status == "done"`` (or ``"failed"`` / ``"too_big"`` for exports).
The helper's ``run_report`` and ``run_export`` collapse that into a
single call. These tests pin the polling-loop semantics:

- happy path (1+ running poll, then done)
- immediate done (no extra GETs)
- terminal failure status
- timeout exhaustion
- ``Retry-After`` header overrides the interval
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import httpx
import pytest

from frontapp_public_api_client.helpers.analytics import (
    Analytics,
    _retry_after_or,
    attempts_for,
)
from frontapp_public_api_client.models.analytics_metric_id import AnalyticsMetricId
from frontapp_public_api_client.models.analytics_report_response_status import (
    AnalyticsReportResponseStatus,
)
from frontapp_public_api_client.utils import APIError


def _report_payload(*, uid: str, status: str, progress: int = 0) -> dict:
    """Minimal valid AnalyticsReportResponse-shaped dict."""
    return {
        "uid": uid,
        "status": status,
        "progress": progress,
        "metrics": [],
        "_links": {"self": "https://x"},
    }


def _export_payload(
    *, id_: str, status: str, progress: int = 0, url: str | None = None
) -> dict:
    """Minimal valid AnalyticsExportResponse-shaped dict.

    ``filters`` is required by the spec; we echo back an empty inbox-ids
    filter since exports always carry one of the typed filter shapes.
    """
    payload: dict = {
        "id": id_,
        "status": status,
        "progress": progress,
        "filters": {"inbox_ids": []},
        "_links": {"self": "https://x"},
    }
    if url is not None:
        payload["url"] = url
    return payload


def _seq_handler(responses: list[tuple[int, dict]]) -> httpx.MockTransport:
    """Build a MockTransport that returns ``responses[i]`` on the i-th call."""
    call_count = {"i": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        i = call_count["i"]
        call_count["i"] = min(i + 1, len(responses) - 1)
        status, body = responses[i]
        return httpx.Response(status, json=body)

    return httpx.MockTransport(handler)


# ---------------------------------------------------------------------------
# attempts_for + _retry_after_or
# ---------------------------------------------------------------------------


class TestAttemptsFor:
    def test_basic_division(self):
        assert attempts_for(30, 1.0) == 30
        assert attempts_for(120, 2.0) == 60

    def test_rounds_up(self):
        # 31 / 2.0 → 15.5 → 16 attempts
        assert attempts_for(31, 2.0) == 16

    def test_at_least_one_attempt(self):
        assert attempts_for(0, 1.0) == 1
        assert attempts_for(0.5, 5.0) == 1


class TestRetryAfterOr:
    def test_returns_default_when_header_absent(self):
        assert _retry_after_or(httpx.Headers({}), 1.5) == 1.5

    def test_parses_seconds(self):
        assert _retry_after_or(httpx.Headers({"Retry-After": "5"}), 1.0) == 5.0

    def test_returns_default_for_invalid(self):
        assert _retry_after_or(httpx.Headers({"Retry-After": "Wed, ..."}), 1.0) == 1.0

    def test_returns_default_for_zero_or_negative(self):
        assert _retry_after_or(httpx.Headers({"Retry-After": "0"}), 1.0) == 1.0
        assert _retry_after_or(httpx.Headers({"Retry-After": "-3"}), 1.0) == 1.0


# ---------------------------------------------------------------------------
# run_report — polling loop
# ---------------------------------------------------------------------------


class TestRunReport:
    @pytest.fixture
    def no_sleep(self, monkeypatch):
        """Replace asyncio.sleep with a no-op so the polling loop runs at full speed."""
        sleeps: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            sleeps.append(seconds)

        monkeypatch.setattr(
            "frontapp_public_api_client.helpers.analytics.asyncio.sleep",
            fake_sleep,
        )
        return sleeps

    async def test_happy_path_walks_running_to_done(self, attach_transport, no_sleep):
        # POST → 201 with running; GET#1 → running; GET#2 → done
        transport = _seq_handler(
            [
                (201, _report_payload(uid="rpt_1", status="running")),
                (200, _report_payload(uid="rpt_1", status="running", progress=50)),
                (200, _report_payload(uid="rpt_1", status="done", progress=100)),
            ]
        )
        client = attach_transport(transport)

        result = await client.analytics.run_report(
            start=datetime(2026, 1, 1, tzinfo=UTC),
            end=datetime(2026, 1, 31, tzinfo=UTC),
            metrics=[AnalyticsMetricId.AVG_FIRST_RESPONSE_TIME],
        )

        assert result.status == AnalyticsReportResponseStatus.DONE
        assert result.progress == 100

    async def test_immediate_done_does_not_sleep(self, attach_transport, no_sleep):
        transport = _seq_handler(
            [
                (201, _report_payload(uid="rpt_1", status="running")),
                (200, _report_payload(uid="rpt_1", status="done", progress=100)),
            ]
        )
        client = attach_transport(transport)

        await client.analytics.run_report(
            start=datetime(2026, 1, 1, tzinfo=UTC),
            end=datetime(2026, 1, 31, tzinfo=UTC),
            metrics=[AnalyticsMetricId.AVG_FIRST_RESPONSE_TIME],
        )
        # Done on the first GET → no sleep should have been recorded.
        assert no_sleep == []

    async def test_failed_status_raises_api_error(self, attach_transport, no_sleep):
        transport = _seq_handler(
            [
                (201, _report_payload(uid="rpt_1", status="running")),
                (200, _report_payload(uid="rpt_1", status="failed")),
            ]
        )
        client = attach_transport(transport)

        with pytest.raises(APIError, match="failed"):
            await client.analytics.run_report(
                start=datetime(2026, 1, 1, tzinfo=UTC),
                end=datetime(2026, 1, 31, tzinfo=UTC),
                metrics=[AnalyticsMetricId.AVG_FIRST_RESPONSE_TIME],
            )

    async def test_timeout_when_max_attempts_exhausted(
        self, attach_transport, no_sleep
    ):
        transport = _seq_handler(
            [
                (201, _report_payload(uid="rpt_1", status="running")),
                (200, _report_payload(uid="rpt_1", status="running")),
            ]
        )
        client = attach_transport(transport)

        with pytest.raises(TimeoutError, match="rpt_1"):
            await client.analytics.run_report(
                start=datetime(2026, 1, 1, tzinfo=UTC),
                end=datetime(2026, 1, 31, tzinfo=UTC),
                metrics=[AnalyticsMetricId.AVG_FIRST_RESPONSE_TIME],
                max_attempts=2,
                interval=0.01,
            )

    async def test_retry_after_header_overrides_interval(
        self, attach_transport, no_sleep
    ):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            if len(recorded) == 1:
                # POST create
                return httpx.Response(
                    201, json=_report_payload(uid="rpt_1", status="running")
                )
            if len(recorded) == 2:
                # First GET → running with Retry-After
                return httpx.Response(
                    200,
                    json=_report_payload(uid="rpt_1", status="running"),
                    headers={"Retry-After": "5"},
                )
            return httpx.Response(
                200, json=_report_payload(uid="rpt_1", status="done", progress=100)
            )

        client = attach_transport(httpx.MockTransport(handler))

        await client.analytics.run_report(
            start=datetime(2026, 1, 1, tzinfo=UTC),
            end=datetime(2026, 1, 31, tzinfo=UTC),
            metrics=[AnalyticsMetricId.AVG_FIRST_RESPONSE_TIME],
            interval=1.0,
        )
        # First sleep used the Retry-After value (5.0), not the default interval.
        assert no_sleep == [5.0]


# ---------------------------------------------------------------------------
# create_report / get_report
# ---------------------------------------------------------------------------


class TestCreateAndGetReport:
    async def test_create_returns_uid(self, attach_transport, make_mock_transport):
        client = attach_transport(
            make_mock_transport(
                _report_payload(uid="rpt_xyz", status="running"), status=201
            )
        )

        uid = await client.analytics.create_report(
            start=datetime(2026, 1, 1, tzinfo=UTC),
            end=datetime(2026, 1, 31, tzinfo=UTC),
            metrics=[AnalyticsMetricId.AVG_FIRST_RESPONSE_TIME],
        )
        assert uid == "rpt_xyz"

    async def test_get_returns_full_response(
        self, attach_transport, make_mock_transport
    ):
        client = attach_transport(
            make_mock_transport(
                _report_payload(uid="rpt_xyz", status="done", progress=100),
                status=200,
            )
        )

        report = await client.analytics.get_report("rpt_xyz")
        assert report.uid == "rpt_xyz"
        assert report.status == AnalyticsReportResponseStatus.DONE


# ---------------------------------------------------------------------------
# run_export — the export flow has an extra terminal state (too_big)
# ---------------------------------------------------------------------------


class TestRunExport:
    @pytest.fixture
    def no_sleep(self, monkeypatch):
        async def fake_sleep(_seconds: float) -> None:
            pass

        monkeypatch.setattr(
            "frontapp_public_api_client.helpers.analytics.asyncio.sleep",
            fake_sleep,
        )

    async def test_happy_path(self, attach_transport, no_sleep):
        from frontapp_public_api_client.models.analytics_messages_columns import (
            AnalyticsMessagesColumns,
        )
        from frontapp_public_api_client.models.analytics_messages_export_columns import (
            AnalyticsMessagesExportColumns,
        )

        transport = _seq_handler(
            [
                (201, _export_payload(id_="exp_1", status="running")),
                (
                    200,
                    _export_payload(
                        id_="exp_1",
                        status="done",
                        progress=100,
                        url="https://x/exp_1.csv",
                    ),
                ),
            ]
        )
        client = attach_transport(transport)
        body = AnalyticsMessagesExportColumns(
            columns=[AnalyticsMessagesColumns.CONVERSATION_ID]
        )
        result = await client.analytics.run_export(body)
        assert result.id == "exp_1"
        assert result.url == "https://x/exp_1.csv"

    async def test_too_big_raises_api_error_with_narrowing_hint(
        self, attach_transport, no_sleep
    ):
        from frontapp_public_api_client.models.analytics_messages_columns import (
            AnalyticsMessagesColumns,
        )
        from frontapp_public_api_client.models.analytics_messages_export_columns import (
            AnalyticsMessagesExportColumns,
        )

        transport = _seq_handler(
            [
                (201, _export_payload(id_="exp_big", status="running")),
                (200, _export_payload(id_="exp_big", status="too_big")),
            ]
        )
        client = attach_transport(transport)
        body = AnalyticsMessagesExportColumns(
            columns=[AnalyticsMessagesColumns.CONVERSATION_ID]
        )
        with pytest.raises(APIError, match="too large"):
            await client.analytics.run_export(body)


# ---------------------------------------------------------------------------
# Property wiring
# ---------------------------------------------------------------------------


class TestWiring:
    def test_client_analytics_returns_analytics_helper(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        assert isinstance(client.analytics, Analytics)

    def test_lazy_property_caches(self, mock_api_credentials):
        from frontapp_public_api_client import FrontappClient

        client = FrontappClient(**mock_api_credentials)
        first = client.analytics
        second = client.analytics
        assert first is second


# Reference (avoid unused-import lint when AsyncMock isn't directly invoked)
_ = AsyncMock
