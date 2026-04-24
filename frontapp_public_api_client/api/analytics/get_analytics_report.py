from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.analytics_report_response import AnalyticsReportResponse


def _get_kwargs(
    report_uid: str = "723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analytics/reports/{report_uid}".format(
            report_uid=quote(str(report_uid), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AnalyticsReportResponse | None:
    if response.status_code == 200:
        response_200 = AnalyticsReportResponse.from_dict(response.json())

        return response_200

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
    report_uid: str = "723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0",
    *,
    client: AuthenticatedClient | Client,
) -> Response[AnalyticsReportResponse]:
    """Fetch an analytics report

     Fetch an analytics report. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics)
    topic for details about specific metrics.

    Required scope: `analytics:read`

    Args:
        report_uid (str):  Default:
            '723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AnalyticsReportResponse]
    """

    kwargs = _get_kwargs(
        report_uid=report_uid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    report_uid: str = "723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0",
    *,
    client: AuthenticatedClient | Client,
) -> AnalyticsReportResponse | None:
    """Fetch an analytics report

     Fetch an analytics report. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics)
    topic for details about specific metrics.

    Required scope: `analytics:read`

    Args:
        report_uid (str):  Default:
            '723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AnalyticsReportResponse
    """

    return sync_detailed(
        report_uid=report_uid,
        client=client,
    ).parsed


async def asyncio_detailed(
    report_uid: str = "723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0",
    *,
    client: AuthenticatedClient | Client,
) -> Response[AnalyticsReportResponse]:
    """Fetch an analytics report

     Fetch an analytics report. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics)
    topic for details about specific metrics.

    Required scope: `analytics:read`

    Args:
        report_uid (str):  Default:
            '723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AnalyticsReportResponse]
    """

    kwargs = _get_kwargs(
        report_uid=report_uid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    report_uid: str = "723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0",
    *,
    client: AuthenticatedClient | Client,
) -> AnalyticsReportResponse | None:
    """Fetch an analytics report

     Fetch an analytics report. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics)
    topic for details about specific metrics.

    Required scope: `analytics:read`

    Args:
        report_uid (str):  Default:
            '723ec32796f12c6f05f6b124d8ef76191a38cec990e0f65d549206c51373f1a0'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AnalyticsReportResponse
    """

    return (
        await asyncio_detailed(
            report_uid=report_uid,
            client=client,
        )
    ).parsed
