"""Tests for MCP analytics tools — argument shaping + helper delegation.

The polling-loop semantics live in the helper (`tests/test_analytics.py`).
These tests pin the tool layer:

- ISO 8601 date strings parse and reach the helper as ``datetime``
- ``timeout_seconds`` translates into ``max_attempts`` correctly
- Filter category selection (single category required by spec)
- Invalid metric / column ids return a validation error before calling
  the client
- ``run_analytics_export`` dispatches on ``export_type`` to the right
  generated body shape
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.tools.analytics import register_tools

from .conftest import create_mock_context


@pytest.fixture
def analytics_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_tools)


def _attrs_with_to_dict(payload: dict):
    """Mock object with a ``to_dict()`` returning ``payload`` (matches the
    attrs-style return type from ``client.analytics.run_*``)."""
    obj = AsyncMock()
    obj.to_dict = lambda: payload
    return obj


# ---------------------------------------------------------------------------
# run_analytics_report
# ---------------------------------------------------------------------------


class TestRunAnalyticsReport:
    async def test_parses_iso_dates_and_passes_metrics(self, analytics_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.analytics.run_report = AsyncMock(
            return_value=_attrs_with_to_dict(
                {"uid": "rpt_1", "status": "done", "progress": 100, "metrics": []}
            )
        )

        result = await analytics_tools["run_analytics_report"](
            context,
            start="2026-04-01T00:00:00Z",
            end="2026-04-30T23:59:59Z",
            metrics=["avg_first_response_time"],
        )

        assert result["status"] == "done"
        # Helper called with parsed datetimes (ISO 'Z' → UTC).
        call = lifespan.client.analytics.run_report.await_args
        assert call is not None
        assert call.kwargs["start"] == datetime(2026, 4, 1, 0, 0, 0, tzinfo=UTC)
        assert call.kwargs["end"] == datetime(2026, 4, 30, 23, 59, 59, tzinfo=UTC)

    async def test_invalid_metric_returns_error_without_calling_client(
        self, analytics_tools
    ):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked despite invalid metric")
        )

        result = await analytics_tools["run_analytics_report"](
            context,
            start="2026-04-01T00:00:00Z",
            end="2026-04-30T23:59:59Z",
            metrics=["definitely_not_a_metric"],
        )

        assert "error" in result
        assert "valid_metrics" in result

    async def test_multiple_filter_categories_rejected(self, analytics_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked despite filter conflict")
        )

        result = await analytics_tools["run_analytics_report"](
            context,
            start="2026-04-01T00:00:00Z",
            end="2026-04-30T23:59:59Z",
            metrics=["avg_first_response_time"],
            inbox_ids=["inb_1"],
            tag_ids=["tag_1"],
        )

        assert "error" in result
        assert "exactly one filter category" in result["error"]

    async def test_single_filter_category_threaded_through(self, analytics_tools):
        from frontapp_public_api_client.models.inbox_ids import InboxIds

        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.analytics.run_report = AsyncMock(
            return_value=_attrs_with_to_dict(
                {"uid": "rpt_1", "status": "done", "progress": 100, "metrics": []}
            )
        )

        await analytics_tools["run_analytics_report"](
            context,
            start="2026-04-01T00:00:00Z",
            end="2026-04-30T23:59:59Z",
            metrics=["avg_first_response_time"],
            inbox_ids=["inb_1", "inb_2"],
        )
        call = lifespan.client.analytics.run_report.await_args
        assert call is not None
        passed = call.kwargs["filters"]
        assert isinstance(passed, InboxIds)
        assert passed.inbox_ids == ["inb_1", "inb_2"]

    async def test_timeout_seconds_translates_to_max_attempts(self, analytics_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.analytics.run_report = AsyncMock(
            return_value=_attrs_with_to_dict(
                {"uid": "rpt_1", "status": "done", "progress": 100, "metrics": []}
            )
        )

        await analytics_tools["run_analytics_report"](
            context,
            start="2026-04-01T00:00:00Z",
            end="2026-04-30T23:59:59Z",
            metrics=["avg_first_response_time"],
            timeout_seconds=45,
        )
        call = lifespan.client.analytics.run_report.await_args
        assert call is not None
        # Report interval is 1.0s → 45 attempts.
        assert call.kwargs["max_attempts"] == 45
        assert call.kwargs["interval"] == 1.0

    async def test_helper_timeout_surfaces_as_error_dict(self, analytics_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.analytics.run_report = AsyncMock(
            side_effect=TimeoutError("Analytics report rpt_x did not complete")
        )

        result = await analytics_tools["run_analytics_report"](
            context,
            start="2026-04-01T00:00:00Z",
            end="2026-04-30T23:59:59Z",
            metrics=["avg_first_response_time"],
        )
        assert result["status"] == "timeout"
        assert "rpt_x" in result["error"]


# ---------------------------------------------------------------------------
# run_analytics_export
# ---------------------------------------------------------------------------


class TestRunAnalyticsExport:
    async def test_activities_dispatch_passes_activity_columns_body(
        self, analytics_tools
    ):
        from frontapp_public_api_client.models.analytics_activities_exports_columns import (
            AnalyticsActivitiesExportsColumns,
        )

        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.analytics.run_export = AsyncMock(
            return_value=_attrs_with_to_dict(
                {"id": "exp_1", "status": "done", "url": "https://x/exp_1.csv"}
            )
        )

        result = await analytics_tools["run_analytics_export"](
            context,
            export_type="activities",
            columns=["Activity ID", "Author"],
        )
        assert result["status"] == "done"
        call = lifespan.client.analytics.run_export.await_args
        assert call is not None
        assert isinstance(call.args[0], AnalyticsActivitiesExportsColumns)

    async def test_messages_dispatch_passes_messages_columns_body(
        self, analytics_tools
    ):
        from frontapp_public_api_client.models.analytics_messages_export_columns import (
            AnalyticsMessagesExportColumns,
        )

        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.analytics.run_export = AsyncMock(
            return_value=_attrs_with_to_dict(
                {"id": "exp_1", "status": "done", "url": "https://x/exp_1.csv"}
            )
        )

        await analytics_tools["run_analytics_export"](
            context,
            export_type="messages",
            columns=["Author"],
        )
        call = lifespan.client.analytics.run_export.await_args
        assert call is not None
        assert isinstance(call.args[0], AnalyticsMessagesExportColumns)

    async def test_invalid_column_returns_error(self, analytics_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked despite invalid column")
        )

        result = await analytics_tools["run_analytics_export"](
            context,
            export_type="messages",
            columns=["this_is_not_a_column"],
        )
        assert "error" in result
        assert "valid" in result

    async def test_export_timeout_seconds_uses_2s_interval(self, analytics_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()
        lifespan.client.analytics.run_export = AsyncMock(
            return_value=_attrs_with_to_dict(
                {"id": "exp_1", "status": "done", "url": "https://x"}
            )
        )

        await analytics_tools["run_analytics_export"](
            context,
            export_type="messages",
            columns=["Author"],
            timeout_seconds=120,
        )
        call = lifespan.client.analytics.run_export.await_args
        assert call is not None
        # Export interval is 2.0s → 60 attempts for a 120s budget.
        assert call.kwargs["max_attempts"] == 60
        assert call.kwargs["interval"] == 2.0
