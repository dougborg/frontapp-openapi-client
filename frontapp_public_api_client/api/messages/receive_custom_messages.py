from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.custom_message import CustomMessage
from ...models.receive_custom_messages_response_202 import (
    ReceiveCustomMessagesResponse202,
)


def _get_kwargs(
    channel_id: str = "cha_123",
    *,
    body: CustomMessage | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/channels/{channel_id}/incoming_messages".format(
            channel_id=quote(str(channel_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ReceiveCustomMessagesResponse202 | None:
    if response.status_code == 202:
        response_202 = ReceiveCustomMessagesResponse202.from_dict(response.json())

        return response_202

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ReceiveCustomMessagesResponse202]:
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
    body: CustomMessage | Unset = UNSET,
) -> Response[ReceiveCustomMessagesResponse202]:
    """Receive custom messages

     Receive a custom message in Front. This endpoint is available for custom channels **ONLY**.

    Required scope: `messages:write`

    Args:
        channel_id (str):  Default: 'cha_123'.
        body (CustomMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ReceiveCustomMessagesResponse202]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
    body: CustomMessage | Unset = UNSET,
) -> ReceiveCustomMessagesResponse202 | None:
    """Receive custom messages

     Receive a custom message in Front. This endpoint is available for custom channels **ONLY**.

    Required scope: `messages:write`

    Args:
        channel_id (str):  Default: 'cha_123'.
        body (CustomMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ReceiveCustomMessagesResponse202
    """

    return sync_detailed(
        channel_id=channel_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
    body: CustomMessage | Unset = UNSET,
) -> Response[ReceiveCustomMessagesResponse202]:
    """Receive custom messages

     Receive a custom message in Front. This endpoint is available for custom channels **ONLY**.

    Required scope: `messages:write`

    Args:
        channel_id (str):  Default: 'cha_123'.
        body (CustomMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ReceiveCustomMessagesResponse202]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
    body: CustomMessage | Unset = UNSET,
) -> ReceiveCustomMessagesResponse202 | None:
    """Receive custom messages

     Receive a custom message in Front. This endpoint is available for custom channels **ONLY**.

    Required scope: `messages:write`

    Args:
        channel_id (str):  Default: 'cha_123'.
        body (CustomMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ReceiveCustomMessagesResponse202
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            client=client,
            body=body,
        )
    ).parsed
