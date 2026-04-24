from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.shift_response import ShiftResponse


def _get_kwargs(
    shift_id: str = "shf_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/shifts/{shift_id}".format(
            shift_id=quote(str(shift_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ShiftResponse | None:
    if response.status_code == 200:
        response_200 = ShiftResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ShiftResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    shift_id: str = "shf_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ShiftResponse]:
    """Get shift

     Fetch a shift.

    Required scope: `shifts:read`

    Args:
        shift_id (str):  Default: 'shf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ShiftResponse]
    """

    kwargs = _get_kwargs(
        shift_id=shift_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    shift_id: str = "shf_123",
    *,
    client: AuthenticatedClient | Client,
) -> ShiftResponse | None:
    """Get shift

     Fetch a shift.

    Required scope: `shifts:read`

    Args:
        shift_id (str):  Default: 'shf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ShiftResponse
    """

    return sync_detailed(
        shift_id=shift_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    shift_id: str = "shf_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ShiftResponse]:
    """Get shift

     Fetch a shift.

    Required scope: `shifts:read`

    Args:
        shift_id (str):  Default: 'shf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ShiftResponse]
    """

    kwargs = _get_kwargs(
        shift_id=shift_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    shift_id: str = "shf_123",
    *,
    client: AuthenticatedClient | Client,
) -> ShiftResponse | None:
    """Get shift

     Fetch a shift.

    Required scope: `shifts:read`

    Args:
        shift_id (str):  Default: 'shf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ShiftResponse
    """

    return (
        await asyncio_detailed(
            shift_id=shift_id,
            client=client,
        )
    ).parsed
