from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.list_inbox_channels_response_200 import ListInboxChannelsResponse200


def _get_kwargs(
    inbox_id: str = "inb_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/inboxes/{inbox_id}/channels".format(
            inbox_id=quote(str(inbox_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListInboxChannelsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListInboxChannelsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListInboxChannelsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    inbox_id: str = "inb_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListInboxChannelsResponse200]:
    """List inbox channels

     List the channels in an inbox.

    Required scope: `channels:read`

    Args:
        inbox_id (str):  Default: 'inb_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListInboxChannelsResponse200]
    """

    kwargs = _get_kwargs(
        inbox_id=inbox_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    inbox_id: str = "inb_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListInboxChannelsResponse200 | None:
    """List inbox channels

     List the channels in an inbox.

    Required scope: `channels:read`

    Args:
        inbox_id (str):  Default: 'inb_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListInboxChannelsResponse200
    """

    return sync_detailed(
        inbox_id=inbox_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    inbox_id: str = "inb_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListInboxChannelsResponse200]:
    """List inbox channels

     List the channels in an inbox.

    Required scope: `channels:read`

    Args:
        inbox_id (str):  Default: 'inb_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListInboxChannelsResponse200]
    """

    kwargs = _get_kwargs(
        inbox_id=inbox_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    inbox_id: str = "inb_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListInboxChannelsResponse200 | None:
    """List inbox channels

     List the channels in an inbox.

    Required scope: `channels:read`

    Args:
        inbox_id (str):  Default: 'inb_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListInboxChannelsResponse200
    """

    return (
        await asyncio_detailed(
            inbox_id=inbox_id,
            client=client,
        )
    ).parsed
