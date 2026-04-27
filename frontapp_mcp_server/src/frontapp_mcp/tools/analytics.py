"""MCP tools for Frontapp analytics — async create→poll wrapped as one call.

Front's analytics endpoints are server-side asynchronous: POST creates a
job and returns an id; GET polls until ``status == "done"``. The helper
(``client.analytics.run_report`` / ``run_export``) does the polling
loop. These MCP tools are the same surface, exposing only the parameters
an LLM caller needs.

No two-step confirm — these are read/query operations (the server-side
job is just how Front computes a report or export, not a write to
workspace state).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.services import get_services
from frontapp_public_api_client.helpers.analytics import attempts_for
from frontapp_public_api_client.utils import APIError

# Default polling cadence — fixed (matches the legacy TS prototype). The
# tool exposes ``timeout_seconds``; we derive ``max_attempts`` from it.
_REPORT_INTERVAL = 1.0
_EXPORT_INTERVAL = 2.0


def register_tools(mcp: FastMCP) -> None:
    """Register analytics tools with the FastMCP server."""

    @mcp.tool(
        name="run_analytics_report",
        description=(
            "Create an analytics report for a metric set over a time range, "
            "then poll Front until the report is ready (server-side async; "
            "typically a few seconds). Returns the final report dict with "
            "`uid`, `status`, `progress`, and `metrics`. "
            "Filters are AND-combined across categories (e.g. `inbox_ids` "
            "AND `tag_ids`); IDs within one category are OR-combined. Pass "
            "exactly one filter category — the spec doesn't allow combining "
            "filter types in a single report. If the timeout elapses, the "
            "tool raises a TimeoutError; the report continues running on "
            "Front and can be retrieved later via the underlying client."
        ),
    )
    async def run_analytics_report(
        context: Context,
        start: Annotated[
            str, Field(description="ISO 8601 datetime, e.g. '2026-04-01T00:00:00Z'")
        ],
        end: Annotated[
            str, Field(description="ISO 8601 datetime, e.g. '2026-04-30T23:59:59Z'")
        ],
        metrics: Annotated[
            list[str],
            Field(
                description=(
                    "Metric ids — see Front's analytics docs for the full "
                    "list (e.g. 'avg_handle_time', 'sla_breach_count')."
                )
            ),
        ],
        timezone: Annotated[
            str | None,
            Field(
                description=(
                    "IANA timezone name (e.g. 'America/Los_Angeles'). "
                    "Defaults to UTC if omitted."
                )
            ),
        ] = None,
        inbox_ids: Annotated[
            list[str] | None,
            Field(description="Filter to these inboxes (e.g. 'inb_abc')."),
        ] = None,
        tag_ids: Annotated[
            list[str] | None,
            Field(description="Filter to these tags (e.g. 'tag_abc')."),
        ] = None,
        teammate_ids: Annotated[
            list[str] | None,
            Field(description="Filter to these teammates (e.g. 'tea_abc')."),
        ] = None,
        team_ids: Annotated[
            list[str] | None,
            Field(description="Filter to these teams (e.g. 'tim_abc')."),
        ] = None,
        channel_ids: Annotated[
            list[str] | None,
            Field(description="Filter to these channels (e.g. 'cha_abc')."),
        ] = None,
        account_ids: Annotated[
            list[str] | None,
            Field(description="Filter to these accounts (e.g. 'acc_abc')."),
        ] = None,
        timeout_seconds: Annotated[
            int,
            Field(
                description=(
                    "How long to poll before giving up. Defaults to 30s; "
                    "raise to 60-90s for large date ranges."
                )
            ),
        ] = 30,
    ) -> dict[str, Any]:
        from frontapp_public_api_client.models.analytics_metric_id import (
            AnalyticsMetricId,
        )

        services = get_services(context)

        try:
            metric_ids = [AnalyticsMetricId(m) for m in metrics]
        except ValueError as e:
            return {
                "error": f"Invalid metric id: {e}",
                "valid_metrics": [m.value for m in AnalyticsMetricId],
            }

        filter_args = {
            "inbox_ids": inbox_ids,
            "tag_ids": tag_ids,
            "teammate_ids": teammate_ids,
            "team_ids": team_ids,
            "channel_ids": channel_ids,
            "account_ids": account_ids,
        }
        populated = [name for name, ids in filter_args.items() if ids]
        if len(populated) > 1:
            return {
                "error": (
                    "Pass exactly one filter category — Front's report spec "
                    "doesn't allow combining filter types. Got: "
                    f"{', '.join(populated)}"
                )
            }
        filters = _build_report_filters(filter_args)

        try:
            report = await services.client.analytics.run_report(
                start=datetime.fromisoformat(start.replace("Z", "+00:00")),
                end=datetime.fromisoformat(end.replace("Z", "+00:00")),
                metrics=metric_ids,
                timezone=timezone,
                filters=filters,
                max_attempts=attempts_for(timeout_seconds, _REPORT_INTERVAL),
                interval=_REPORT_INTERVAL,
            )
        except TimeoutError as e:
            return {"error": str(e), "status": "timeout"}
        except APIError as e:
            return {"error": str(e), "status": "failed"}

        return report.to_dict()

    @mcp.tool(
        name="run_analytics_export",
        description=(
            "Create an analytics export of teammate-activity or message-level "
            "rows, then poll Front until ready (server-side async; can take "
            "1-2 minutes for large date ranges). Returns the final export "
            "dict with `id`, `status`, `url` (download link), `filename`, "
            "and `size`. If Front responds `too_big`, narrow the date range "
            "or column set and retry."
        ),
    )
    async def run_analytics_export(
        context: Context,
        export_type: Annotated[
            Literal["activities", "messages"],
            Field(
                description=(
                    "Which export shape to produce. 'activities' = teammate "
                    "activity rows; 'messages' = message-level rows."
                )
            ),
        ],
        columns: Annotated[
            list[str],
            Field(
                description=(
                    "Columns to include. The valid set depends on "
                    "`export_type` — see Front's analytics docs."
                )
            ),
        ],
        timeout_seconds: Annotated[
            int,
            Field(
                description=(
                    "How long to poll before giving up. Defaults to 120s; "
                    "exports of large date ranges may need more."
                )
            ),
        ] = 120,
    ) -> dict[str, Any]:
        from frontapp_public_api_client.models.analytics_activities_columns import (
            AnalyticsActivitiesColumns,
        )
        from frontapp_public_api_client.models.analytics_activities_exports_columns import (
            AnalyticsActivitiesExportsColumns,
        )
        from frontapp_public_api_client.models.analytics_messages_columns import (
            AnalyticsMessagesColumns,
        )
        from frontapp_public_api_client.models.analytics_messages_export_columns import (
            AnalyticsMessagesExportColumns,
        )

        services = get_services(context)

        body: AnalyticsActivitiesExportsColumns | AnalyticsMessagesExportColumns
        try:
            if export_type == "activities":
                activity_cols: list[AnalyticsActivitiesColumns | str] = [
                    AnalyticsActivitiesColumns(c) for c in columns
                ]
                body = AnalyticsActivitiesExportsColumns(columns=activity_cols)
            else:
                msg_cols = [AnalyticsMessagesColumns(c) for c in columns]
                body = AnalyticsMessagesExportColumns(columns=msg_cols)
        except ValueError as e:
            valid = (
                [c.value for c in AnalyticsActivitiesColumns]
                if export_type == "activities"
                else [c.value for c in AnalyticsMessagesColumns]
            )
            return {"error": f"Invalid column for {export_type}: {e}", "valid": valid}

        try:
            export = await services.client.analytics.run_export(
                body,
                max_attempts=attempts_for(timeout_seconds, _EXPORT_INTERVAL),
                interval=_EXPORT_INTERVAL,
            )
        except TimeoutError as e:
            return {"error": str(e), "status": "timeout"}
        except APIError as e:
            return {"error": str(e), "status": "failed"}

        return export.to_dict()


def _build_report_filters(
    filter_args: dict[str, list[str] | None],
) -> Any:
    """Construct the single filter object the caller specified, or None.

    Caller is responsible for verifying ``len(populated) <= 1`` first
    (Front's report spec is ``oneOf`` — combining categories is rejected
    server-side). Returns the typed ``AccountIds`` / ``ChannelIds`` /
    etc. filter object, or ``None`` when the caller passed no filters.
    The return type is ``Any`` because the caller branches on the choice
    of filter — none of the six filter classes share a common base.
    """
    from frontapp_public_api_client.models.account_ids import AccountIds
    from frontapp_public_api_client.models.channel_ids import ChannelIds
    from frontapp_public_api_client.models.inbox_ids import InboxIds
    from frontapp_public_api_client.models.tag_ids import TagIds
    from frontapp_public_api_client.models.team_ids import TeamIds
    from frontapp_public_api_client.models.teammate_ids import TeammateIds

    classes = {
        "inbox_ids": InboxIds,
        "tag_ids": TagIds,
        "teammate_ids": TeammateIds,
        "team_ids": TeamIds,
        "channel_ids": ChannelIds,
        "account_ids": AccountIds,
    }
    for name, ids in filter_args.items():
        if ids:
            return classes[name](**{name: ids})
    return None
