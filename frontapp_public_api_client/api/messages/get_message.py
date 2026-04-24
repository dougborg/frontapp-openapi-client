from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.message_response import MessageResponse


def _get_kwargs(
    message_id: str = "msg_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/messages/{message_id}".format(
            message_id=quote(str(message_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> MessageResponse | None:
    if response.status_code == 200:
        response_200 = MessageResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[MessageResponse]:
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
) -> Response[MessageResponse]:
    """Get message

     Fetch a message.

    > i️ The HTTP Header `Accept` can be used to request the message in a different format.
    > By default, Front will return the documented JSON response. By requesting `message/rfc822`, the
    response will contain the message in the EML format (for email messages only).


    Required scope: `messages:read`

    Args:
        message_id (str):  Default: 'msg_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageResponse]
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
) -> MessageResponse | None:
    """Get message

     Fetch a message.

    > i️ The HTTP Header `Accept` can be used to request the message in a different format.
    > By default, Front will return the documented JSON response. By requesting `message/rfc822`, the
    response will contain the message in the EML format (for email messages only).


    Required scope: `messages:read`

    Args:
        message_id (str):  Default: 'msg_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageResponse
    """

    return sync_detailed(
        message_id=message_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[MessageResponse]:
    """Get message

     Fetch a message.

    > i️ The HTTP Header `Accept` can be used to request the message in a different format.
    > By default, Front will return the documented JSON response. By requesting `message/rfc822`, the
    response will contain the message in the EML format (for email messages only).


    Required scope: `messages:read`

    Args:
        message_id (str):  Default: 'msg_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageResponse]
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
) -> MessageResponse | None:
    """Get message

     Fetch a message.

    > i️ The HTTP Header `Accept` can be used to request the message in a different format.
    > By default, Front will return the documented JSON response. By requesting `message/rfc822`, the
    response will contain the message in the EML format (for email messages only).


    Required scope: `messages:read`

    Args:
        message_id (str):  Default: 'msg_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageResponse
    """

    return (
        await asyncio_detailed(
            message_id=message_id,
            client=client,
        )
    ).parsed
