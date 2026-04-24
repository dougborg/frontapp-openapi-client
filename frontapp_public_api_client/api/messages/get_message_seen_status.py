from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.get_message_seen_status_response_200 import (
    GetMessageSeenStatusResponse200,
)


def _get_kwargs(
    message_id: str = "msg_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/messages/{message_id}/seen".format(
            message_id=quote(str(message_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetMessageSeenStatusResponse200 | None:
    if response.status_code == 200:
        response_200 = GetMessageSeenStatusResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetMessageSeenStatusResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetMessageSeenStatusResponse200]:
    """Get message seen status

     Get the seen receipts for the given message. If no seen-by information is available, there will be a
    single entry for the first time the message was seen by any recipient. If seen-by information is
    available, there will be an entry for each recipient who has seen the message.

    Required scope: `messages:read`

    Args:
        message_id (str):  Default: 'msg_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[GetMessageSeenStatusResponse200]
    """

    kwargs = _get_kwargs(
        message_id=message_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
) -> GetMessageSeenStatusResponse200 | None:
    """Get message seen status

     Get the seen receipts for the given message. If no seen-by information is available, there will be a
    single entry for the first time the message was seen by any recipient. If seen-by information is
    available, there will be an entry for each recipient who has seen the message.

    Required scope: `messages:read`

    Args:
        message_id (str):  Default: 'msg_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        GetMessageSeenStatusResponse200
    """

    return sync_detailed(
        message_id=message_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetMessageSeenStatusResponse200]:
    """Get message seen status

     Get the seen receipts for the given message. If no seen-by information is available, there will be a
    single entry for the first time the message was seen by any recipient. If seen-by information is
    available, there will be an entry for each recipient who has seen the message.

    Required scope: `messages:read`

    Args:
        message_id (str):  Default: 'msg_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[GetMessageSeenStatusResponse200]
    """

    kwargs = _get_kwargs(
        message_id=message_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
) -> GetMessageSeenStatusResponse200 | None:
    """Get message seen status

     Get the seen receipts for the given message. If no seen-by information is available, there will be a
    single entry for the first time the message was seen by any recipient. If seen-by information is
    available, there will be an entry for each recipient who has seen the message.

    Required scope: `messages:read`

    Args:
        message_id (str):  Default: 'msg_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        GetMessageSeenStatusResponse200
    """

    return (
        await asyncio_detailed(
            message_id=message_id,
            client=client,
        )
    ).parsed
