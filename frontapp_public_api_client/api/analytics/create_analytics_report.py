from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.analytics_report_request import AnalyticsReportRequest
from ...models.analytics_report_response import AnalyticsReportResponse


def _get_kwargs(
    *,
    body: AnalyticsReportRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/analytics/reports",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AnalyticsReportResponse | None:
    if response.status_code == 201:
        response_201 = AnalyticsReportResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AnalyticsReportResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AnalyticsReportRequest | Unset = UNSET,
) -> Response[AnalyticsReportResponse]:
    """Create a new analytics report

     Create a new analytics report for a set of metrics over a specific time span. Different filters
    (e.g. Inbox v Tag v Teammates) will be joined with AND logic, but the IDs within a filter will be
    joined with OR logic (e.g. Inbox A or Inbox B, Tag A or Tag B).
    The report will be executed asynchronously. The response will include a link that can be used to
    retrieve the
    report status & result. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics) topic
    for details about specific metrics.


    Required scope: `analytics:read`

    Args:
        body (AnalyticsReportRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AnalyticsReportResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: AnalyticsReportRequest | Unset = UNSET,
) -> AnalyticsReportResponse | None:
    """Create a new analytics report

     Create a new analytics report for a set of metrics over a specific time span. Different filters
    (e.g. Inbox v Tag v Teammates) will be joined with AND logic, but the IDs within a filter will be
    joined with OR logic (e.g. Inbox A or Inbox B, Tag A or Tag B).
    The report will be executed asynchronously. The response will include a link that can be used to
    retrieve the
    report status & result. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics) topic
    for details about specific metrics.


    Required scope: `analytics:read`

    Args:
        body (AnalyticsReportRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AnalyticsReportResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AnalyticsReportRequest | Unset = UNSET,
) -> Response[AnalyticsReportResponse]:
    """Create a new analytics report

     Create a new analytics report for a set of metrics over a specific time span. Different filters
    (e.g. Inbox v Tag v Teammates) will be joined with AND logic, but the IDs within a filter will be
    joined with OR logic (e.g. Inbox A or Inbox B, Tag A or Tag B).
    The report will be executed asynchronously. The response will include a link that can be used to
    retrieve the
    report status & result. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics) topic
    for details about specific metrics.


    Required scope: `analytics:read`

    Args:
        body (AnalyticsReportRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AnalyticsReportResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: AnalyticsReportRequest | Unset = UNSET,
) -> AnalyticsReportResponse | None:
    """Create a new analytics report

     Create a new analytics report for a set of metrics over a specific time span. Different filters
    (e.g. Inbox v Tag v Teammates) will be joined with AND logic, but the IDs within a filter will be
    joined with OR logic (e.g. Inbox A or Inbox B, Tag A or Tag B).
    The report will be executed asynchronously. The response will include a link that can be used to
    retrieve the
    report status & result. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics) topic
    for details about specific metrics.


    Required scope: `analytics:read`

    Args:
        body (AnalyticsReportRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AnalyticsReportResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
