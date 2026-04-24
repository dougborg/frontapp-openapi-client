from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.analytics_export_response import AnalyticsExportResponse


def _get_kwargs(
    export_id: str = "exp_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/analytics/exports/{export_id}".format(
            export_id=quote(str(export_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AnalyticsExportResponse | None:
    if response.status_code == 200:
        response_200 = AnalyticsExportResponse.from_dict(response.json())

        return response_200

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
    export_id: str = "exp_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[AnalyticsExportResponse]:
    """Fetch an analytics export

     Fetch an analytics exports. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics)
    topic for details about specific metrics.

    Required scope: `analytics:read`

    Args:
        export_id (str):  Default: 'exp_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AnalyticsExportResponse]
    """

    kwargs = _get_kwargs(
        export_id=export_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    export_id: str = "exp_123",
    *,
    client: AuthenticatedClient | Client,
) -> AnalyticsExportResponse | None:
    """Fetch an analytics export

     Fetch an analytics exports. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics)
    topic for details about specific metrics.

    Required scope: `analytics:read`

    Args:
        export_id (str):  Default: 'exp_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AnalyticsExportResponse
    """

    return sync_detailed(
        export_id=export_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    export_id: str = "exp_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[AnalyticsExportResponse]:
    """Fetch an analytics export

     Fetch an analytics exports. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics)
    topic for details about specific metrics.

    Required scope: `analytics:read`

    Args:
        export_id (str):  Default: 'exp_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AnalyticsExportResponse]
    """

    kwargs = _get_kwargs(
        export_id=export_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    export_id: str = "exp_123",
    *,
    client: AuthenticatedClient | Client,
) -> AnalyticsExportResponse | None:
    """Fetch an analytics export

     Fetch an analytics exports. Refer to the [Analytics](https://dev.frontapp.com/reference/analytics)
    topic for details about specific metrics.

    Required scope: `analytics:read`

    Args:
        export_id (str):  Default: 'exp_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AnalyticsExportResponse
    """

    return (
        await asyncio_detailed(
            export_id=export_id,
            client=client,
        )
    ).parsed
