from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_message_reply_response_202 import CreateMessageReplyResponse202
from ...models.outbound_reply_message import OutboundReplyMessage


def _get_kwargs(
    conversation_id: str = "cnv_123",
    *,
    body: OutboundReplyMessage | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/conversations/{conversation_id}/messages".format(
            conversation_id=quote(str(conversation_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | CreateMessageReplyResponse202 | None:
    if response.status_code == 202:
        response_202 = CreateMessageReplyResponse202.from_dict(response.json())

        return response_202

    if response.status_code == 301:
        response_301 = cast(Any, None)
        return response_301

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | CreateMessageReplyResponse202]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: OutboundReplyMessage | Unset = UNSET,
) -> Response[Any | CreateMessageReplyResponse202]:
    """Create message reply

     Reply to a conversation by sending a message and appending it to the conversation.

    Required scope: `messages:send`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (OutboundReplyMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | CreateMessageReplyResponse202]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: OutboundReplyMessage | Unset = UNSET,
) -> Any | CreateMessageReplyResponse202 | None:
    """Create message reply

     Reply to a conversation by sending a message and appending it to the conversation.

    Required scope: `messages:send`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (OutboundReplyMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | CreateMessageReplyResponse202
    """

    return sync_detailed(
        conversation_id=conversation_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: OutboundReplyMessage | Unset = UNSET,
) -> Response[Any | CreateMessageReplyResponse202]:
    """Create message reply

     Reply to a conversation by sending a message and appending it to the conversation.

    Required scope: `messages:send`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (OutboundReplyMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | CreateMessageReplyResponse202]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: OutboundReplyMessage | Unset = UNSET,
) -> Any | CreateMessageReplyResponse202 | None:
    """Create message reply

     Reply to a conversation by sending a message and appending it to the conversation.

    Required scope: `messages:send`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (OutboundReplyMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | CreateMessageReplyResponse202
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            client=client,
            body=body,
        )
    ).parsed
