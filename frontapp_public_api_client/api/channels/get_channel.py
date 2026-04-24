from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.channel_response import ChannelResponse


def _get_kwargs(
    channel_id: str = "cha_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/channels/{channel_id}".format(
            channel_id=quote(str(channel_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ChannelResponse | None:
    if response.status_code == 200:
        response_200 = ChannelResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ChannelResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ChannelResponse]:
    """Get channel

     Fetch a channel.

    Required scope: `channels:read`

    Args:
        channel_id (str):  Default: 'cha_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ChannelResponse]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
) -> ChannelResponse | None:
    """Get channel

     Fetch a channel.

    Required scope: `channels:read`

    Args:
        channel_id (str):  Default: 'cha_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ChannelResponse
    """

    return sync_detailed(
        channel_id=channel_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ChannelResponse]:
    """Get channel

     Fetch a channel.

    Required scope: `channels:read`

    Args:
        channel_id (str):  Default: 'cha_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ChannelResponse]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
) -> ChannelResponse | None:
    """Get channel

     Fetch a channel.

    Required scope: `channels:read`

    Args:
        channel_id (str):  Default: 'cha_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ChannelResponse
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            client=client,
        )
    ).parsed
