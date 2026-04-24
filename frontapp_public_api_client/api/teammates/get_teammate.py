from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.teammate_response import TeammateResponse


def _get_kwargs(
    teammate_id: str = "tea_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/teammates/{teammate_id}".format(
            teammate_id=quote(str(teammate_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> TeammateResponse | None:
    if response.status_code == 200:
        response_200 = TeammateResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[TeammateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[TeammateResponse]:
    """Get teammate

     Fetch a teammate.

    Required scope: `teammates:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[TeammateResponse]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
) -> TeammateResponse | None:
    """Get teammate

     Fetch a teammate.

    Required scope: `teammates:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        TeammateResponse
    """

    return sync_detailed(
        teammate_id=teammate_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[TeammateResponse]:
    """Get teammate

     Fetch a teammate.

    Required scope: `teammates:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[TeammateResponse]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
) -> TeammateResponse | None:
    """Get teammate

     Fetch a teammate.

    Required scope: `teammates:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        TeammateResponse
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
        )
    ).parsed
