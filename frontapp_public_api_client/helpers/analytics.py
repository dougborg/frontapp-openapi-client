"""Analytics helper facade — wraps the create→poll pattern for Front's async
``/analytics/reports`` and ``/analytics/exports`` endpoints.

Front's analytics endpoints are asynchronous on the server side: the POST
returns immediately with an id and ``status: "running"``, and a follow-up
GET polls until ``status == "done"`` (or ``"failed"``, or ``"too_big"``
for exports). The legacy TypeScript MCP at ``dougborg/Frontapp-MCP``
implemented a 10-attempt / 1-second-interval polling loop; this helper
ports the same pattern into Python with configurable bounds and proper
error mapping.

Public surface:

- ``client.analytics.create_report(...)`` — POST + return ``report_uid``
- ``client.analytics.get_report(uid)`` — single GET (may return placeholder)
- ``client.analytics.run_report(...)`` — one-shot create → poll → return
- ``client.analytics.create_export(body)`` / ``get_export(id)`` / ``run_export(body)``

The `run_*` methods raise ``TimeoutError`` after ``max_attempts * interval``
seconds and ``APIError`` on a terminal ``failed`` (or ``too_big`` for
exports) status. They honor a ``Retry-After`` response header on the
GET poll if Front sends one (overrides ``interval`` for that single
sleep).
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from math import ceil
from typing import TYPE_CHECKING, Any

from frontapp_public_api_client.helpers.base import Base
from frontapp_public_api_client.utils import APIError, unwrap_as

if TYPE_CHECKING:
    from frontapp_public_api_client.models.account_ids import AccountIds
    from frontapp_public_api_client.models.analytics_activities_exports_columns import (
        AnalyticsActivitiesExportsColumns,
    )
    from frontapp_public_api_client.models.analytics_export_response import (
        AnalyticsExportResponse,
    )
    from frontapp_public_api_client.models.analytics_messages_export_columns import (
        AnalyticsMessagesExportColumns,
    )
    from frontapp_public_api_client.models.analytics_metric_id import AnalyticsMetricId
    from frontapp_public_api_client.models.analytics_report_response import (
        AnalyticsReportResponse,
    )
    from frontapp_public_api_client.models.channel_ids import ChannelIds
    from frontapp_public_api_client.models.inbox_ids import InboxIds
    from frontapp_public_api_client.models.tag_ids import TagIds
    from frontapp_public_api_client.models.team_ids import TeamIds
    from frontapp_public_api_client.models.teammate_ids import TeammateIds

# Filter types Front's report endpoint accepts (oneOf in the spec). Combined
# at the field type to satisfy the generated request model's union.
ReportFilters = "AccountIds | ChannelIds | InboxIds | TagIds | TeamIds | TeammateIds"
ExportBody = "AnalyticsActivitiesExportsColumns | AnalyticsMessagesExportColumns"


class Analytics(Base):
    """Ergonomic operations over Frontapp's ``/analytics/*`` async endpoints."""

    # -- reports ------------------------------------------------------------

    async def create_report(
        self,
        *,
        start: datetime,
        end: datetime,
        metrics: list[AnalyticsMetricId],
        timezone: str | None = None,
        filters: AccountIds
        | ChannelIds
        | InboxIds
        | TagIds
        | TeamIds
        | TeammateIds
        | None = None,
    ) -> str:
        """POST ``/analytics/reports``; returns the new report's ``uid``.

        The report runs asynchronously on Front's side. Use ``get_report(uid)``
        to poll the result, or ``run_report(...)`` to do the whole loop in
        one call.
        """
        from frontapp_public_api_client.api.analytics import create_analytics_report
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.models.analytics_report_request import (
            AnalyticsReportRequest,
        )

        body = AnalyticsReportRequest(
            start=start.timestamp(),
            end=end.timestamp(),
            metrics=metrics,
            timezone=to_unset(timezone),
            filters=to_unset(filters),
        )
        response = await create_analytics_report.asyncio_detailed(
            client=self._client, body=body
        )
        from frontapp_public_api_client.models.analytics_report_response import (
            AnalyticsReportResponse,
        )

        parsed = unwrap_as(response, AnalyticsReportResponse)
        return parsed.uid

    async def get_report(self, report_uid: str) -> AnalyticsReportResponse:
        """GET ``/analytics/reports/{uid}``; returns the current report state.

        While the report is still processing, the response will have
        ``status == "running"`` (or ``"failed"`` if the report errored).
        Use ``run_report`` to poll until ``"done"``.
        """
        from frontapp_public_api_client.api.analytics import get_analytics_report
        from frontapp_public_api_client.models.analytics_report_response import (
            AnalyticsReportResponse,
        )

        response = await get_analytics_report.asyncio_detailed(
            client=self._client, report_uid=report_uid
        )
        return unwrap_as(response, AnalyticsReportResponse)

    async def run_report(
        self,
        *,
        start: datetime,
        end: datetime,
        metrics: list[AnalyticsMetricId],
        timezone: str | None = None,
        filters: AccountIds
        | ChannelIds
        | InboxIds
        | TagIds
        | TeamIds
        | TeammateIds
        | None = None,
        max_attempts: int = 20,
        interval: float = 1.0,
    ) -> AnalyticsReportResponse:
        """Create the report, poll until done, return the final result.

        ``start`` / ``end`` / ``metrics`` / ``timezone`` / ``filters``
        match ``create_report``.

        Args:
            max_attempts: Maximum number of GET polls before giving up.
                Defaults to 20 (with the default 1.0s interval that's a
                20s budget — long enough for typical reports, short
                enough to fail an MCP call gracefully).
            interval: Seconds to sleep between polls. Honors a
                ``Retry-After`` response header if Front sends one (it
                overrides ``interval`` for that single sleep).

        Raises:
            TimeoutError: All ``max_attempts`` polls returned non-terminal
                status; the report id is in the message for resumption.
            APIError: Front returned ``status: "failed"``.
        """
        from frontapp_public_api_client.api.analytics import get_analytics_report
        from frontapp_public_api_client.models.analytics_report_response import (
            AnalyticsReportResponse,
        )
        from frontapp_public_api_client.models.analytics_report_response_status import (
            AnalyticsReportResponseStatus,
        )

        report_uid = await self.create_report(
            start=start,
            end=end,
            metrics=metrics,
            timezone=timezone,
            filters=filters,
        )

        for _attempt in range(max_attempts):
            response = await get_analytics_report.asyncio_detailed(
                client=self._client, report_uid=report_uid
            )
            parsed = unwrap_as(response, AnalyticsReportResponse)

            if parsed.status == AnalyticsReportResponseStatus.DONE:
                return parsed
            if parsed.status == AnalyticsReportResponseStatus.FAILED:
                raise APIError(
                    f"Analytics report {report_uid} failed",
                    response.status_code,
                    parsed,
                )

            sleep_for = _retry_after_or(response.headers, interval)
            await asyncio.sleep(sleep_for)

        raise TimeoutError(
            f"Analytics report {report_uid} did not complete within "
            f"{max_attempts} polls (~{max_attempts * interval:.0f}s); "
            f"call client.analytics.get_report({report_uid!r}) to resume."
        )

    # -- exports ------------------------------------------------------------

    async def create_export(
        self,
        body: AnalyticsActivitiesExportsColumns | AnalyticsMessagesExportColumns,
    ) -> str:
        """POST ``/analytics/exports``; returns the export's ``id``.

        ``body`` is one of two typed columnar specs depending on what
        you want to export:

        - ``AnalyticsActivitiesExportsColumns`` — teammate activity rows
        - ``AnalyticsMessagesExportColumns`` — message-level rows

        Construct the spec directly from the generated models; the helper
        passes it through unchanged.
        """
        from frontapp_public_api_client.api.analytics import create_analytics_export
        from frontapp_public_api_client.models.analytics_export_response import (
            AnalyticsExportResponse,
        )

        response = await create_analytics_export.asyncio_detailed(
            client=self._client, body=body
        )
        parsed = unwrap_as(response, AnalyticsExportResponse)
        return parsed.id

    async def get_export(self, export_id: str) -> AnalyticsExportResponse:
        """GET ``/analytics/exports/{id}``; returns the current export state."""
        from frontapp_public_api_client.api.analytics import get_analytics_export
        from frontapp_public_api_client.models.analytics_export_response import (
            AnalyticsExportResponse,
        )

        response = await get_analytics_export.asyncio_detailed(
            client=self._client, export_id=export_id
        )
        return unwrap_as(response, AnalyticsExportResponse)

    async def run_export(
        self,
        body: AnalyticsActivitiesExportsColumns | AnalyticsMessagesExportColumns,
        *,
        max_attempts: int = 60,
        interval: float = 2.0,
    ) -> AnalyticsExportResponse:
        """Create the export, poll until done, return the final result.

        Defaults are tuned higher than ``run_report`` because exports
        process bulk data (60 polls at 2.0s each = 120s budget).

        Raises:
            TimeoutError: Polls exhausted before a terminal status.
            APIError: Front returned ``status: "failed"`` or ``status:
                "too_big"`` (the latter means the date range was too
                large; the caller should narrow it and retry).
        """
        from frontapp_public_api_client.api.analytics import get_analytics_export
        from frontapp_public_api_client.models.analytics_export_response import (
            AnalyticsExportResponse,
        )
        from frontapp_public_api_client.models.analytics_export_response_status import (
            AnalyticsExportResponseStatus,
        )

        export_id = await self.create_export(body)

        for _attempt in range(max_attempts):
            response = await get_analytics_export.asyncio_detailed(
                client=self._client, export_id=export_id
            )
            parsed = unwrap_as(response, AnalyticsExportResponse)

            if parsed.status == AnalyticsExportResponseStatus.DONE:
                return parsed
            if parsed.status == AnalyticsExportResponseStatus.FAILED:
                raise APIError(
                    f"Analytics export {export_id} failed",
                    response.status_code,
                    parsed,
                )
            if parsed.status == AnalyticsExportResponseStatus.TOO_BIG:
                raise APIError(
                    f"Analytics export {export_id} is too large to produce; "
                    "narrow the date range or column set and retry.",
                    response.status_code,
                    parsed,
                )

            sleep_for = _retry_after_or(response.headers, interval)
            await asyncio.sleep(sleep_for)

        raise TimeoutError(
            f"Analytics export {export_id} did not complete within "
            f"{max_attempts} polls (~{max_attempts * interval:.0f}s); "
            f"call client.analytics.get_export({export_id!r}) to resume."
        )


def _retry_after_or(headers: Any, default: float) -> float:
    """Parse ``Retry-After`` (seconds) if present and positive, else default.

    Front follows RFC 7231 — the header value is delta-seconds. We don't
    handle the HTTP-date form; if Front ever sends one it'll fail to
    parse and we fall back to the default interval.
    """
    raw = headers.get("Retry-After") if hasattr(headers, "get") else None
    if not raw:
        return default
    try:
        seconds = float(raw)
    except (TypeError, ValueError):
        return default
    return seconds if seconds > 0 else default


def attempts_for(timeout_seconds: float, interval: float) -> int:
    """How many polls fit in ``timeout_seconds`` at the given ``interval``.

    Public so the MCP layer can convert its ``timeout_seconds`` parameter
    into the helper's ``max_attempts`` argument without each tool having
    to re-derive the formula.
    """
    return max(1, ceil(timeout_seconds / interval))
