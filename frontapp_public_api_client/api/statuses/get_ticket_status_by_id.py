from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.status_response import StatusResponse


def _get_kwargs(
    status_id: str = "sts_5z",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/company/statuses/{status_id}".format(
            status_id=quote(str(status_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> StatusResponse | None:
    if response.status_code == 200:
        response_200 = StatusResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[StatusResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    status_id: str = "sts_5z",
    *,
    client: AuthenticatedClient | Client,
) -> Response[StatusResponse]:
    """Get ticket status

     Fetch a ticket status.

    Required scope: `statuses:read`

    Args:
        status_id (str):  Default: 'sts_5z'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[StatusResponse]
    """

    kwargs = _get_kwargs(
        status_id=status_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    status_id: str = "sts_5z",
    *,
    client: AuthenticatedClient | Client,
) -> StatusResponse | None:
    """Get ticket status

     Fetch a ticket status.

    Required scope: `statuses:read`

    Args:
        status_id (str):  Default: 'sts_5z'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        StatusResponse
    """

    return sync_detailed(
        status_id=status_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    status_id: str = "sts_5z",
    *,
    client: AuthenticatedClient | Client,
) -> Response[StatusResponse]:
    """Get ticket status

     Fetch a ticket status.

    Required scope: `statuses:read`

    Args:
        status_id (str):  Default: 'sts_5z'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[StatusResponse]
    """

    kwargs = _get_kwargs(
        status_id=status_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    status_id: str = "sts_5z",
    *,
    client: AuthenticatedClient | Client,
) -> StatusResponse | None:
    """Get ticket status

     Fetch a ticket status.

    Required scope: `statuses:read`

    Args:
        status_id (str):  Default: 'sts_5z'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        StatusResponse
    """

    return (
        await asyncio_detailed(
            status_id=status_id,
            client=client,
        )
    ).parsed
