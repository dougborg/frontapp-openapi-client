from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.analytics_activities_exports_columns import (
    AnalyticsActivitiesExportsColumns,
)
from ...models.analytics_export_response import AnalyticsExportResponse
from ...models.analytics_messages_export_columns import AnalyticsMessagesExportColumns


def _get_kwargs(
    *,
    body: AnalyticsActivitiesExportsColumns
    | AnalyticsMessagesExportColumns
    | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/analytics/exports",
    }

    if isinstance(body, AnalyticsMessagesExportColumns):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AnalyticsExportResponse | None:
    if response.status_code == 201:
        response_201 = AnalyticsExportResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AnalyticsExportResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AnalyticsActivitiesExportsColumns
    | AnalyticsMessagesExportColumns
    | Unset = UNSET,
) -> Response[AnalyticsExportResponse]:
    """Create a new analytics export

     Create a new analytics export of messages or events (activities) over a specific time span.
    The export will be executed asynchronously. The response will include a link that can be used to
    retrieve the export status & result. Refer to the
    [Analytics](https://dev.frontapp.com/reference/analytics) topic for details about specific metrics.


    Required scope: `analytics:read`

    Args:
        body (AnalyticsActivitiesExportsColumns | AnalyticsMessagesExportColumns | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AnalyticsExportResponse]
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
    body: AnalyticsActivitiesExportsColumns
    | AnalyticsMessagesExportColumns
    | Unset = UNSET,
) -> AnalyticsExportResponse | None:
    """Create a new analytics export

     Create a new analytics export of messages or events (activities) over a specific time span.
    The export will be executed asynchronously. The response will include a link that can be used to
    retrieve the export status & result. Refer to the
    [Analytics](https://dev.frontapp.com/reference/analytics) topic for details about specific metrics.


    Required scope: `analytics:read`

    Args:
        body (AnalyticsActivitiesExportsColumns | AnalyticsMessagesExportColumns | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AnalyticsExportResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AnalyticsActivitiesExportsColumns
    | AnalyticsMessagesExportColumns
    | Unset = UNSET,
) -> Response[AnalyticsExportResponse]:
    """Create a new analytics export

     Create a new analytics export of messages or events (activities) over a specific time span.
    The export will be executed asynchronously. The response will include a link that can be used to
    retrieve the export status & result. Refer to the
    [Analytics](https://dev.frontapp.com/reference/analytics) topic for details about specific metrics.


    Required scope: `analytics:read`

    Args:
        body (AnalyticsActivitiesExportsColumns | AnalyticsMessagesExportColumns | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AnalyticsExportResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: AnalyticsActivitiesExportsColumns
    | AnalyticsMessagesExportColumns
    | Unset = UNSET,
) -> AnalyticsExportResponse | None:
    """Create a new analytics export

     Create a new analytics export of messages or events (activities) over a specific time span.
    The export will be executed asynchronously. The response will include a link that can be used to
    retrieve the export status & result. Refer to the
    [Analytics](https://dev.frontapp.com/reference/analytics) topic for details about specific metrics.


    Required scope: `analytics:read`

    Args:
        body (AnalyticsActivitiesExportsColumns | AnalyticsMessagesExportColumns | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AnalyticsExportResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
