from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.conversation_response import ConversationResponse


def _get_kwargs(
    conversation_id: str = "cnv_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/conversations/{conversation_id}".format(
            conversation_id=quote(str(conversation_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ConversationResponse | None:
    if response.status_code == 200:
        response_200 = ConversationResponse.from_dict(response.json())

        return response_200

    if response.status_code == 301:
        response_301 = cast(Any, None)
        return response_301

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ConversationResponse]:
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
) -> Response[Any | ConversationResponse]:
    """Get conversation

     Fetch a conversation.


    Required scope: `conversations:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | ConversationResponse]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
) -> Any | ConversationResponse | None:
    """Get conversation

     Fetch a conversation.


    Required scope: `conversations:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | ConversationResponse
    """

    return sync_detailed(
        conversation_id=conversation_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | ConversationResponse]:
    """Get conversation

     Fetch a conversation.


    Required scope: `conversations:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | ConversationResponse]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
) -> Any | ConversationResponse | None:
    """Get conversation

     Fetch a conversation.


    Required scope: `conversations:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | ConversationResponse
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            client=client,
        )
    ).parsed
