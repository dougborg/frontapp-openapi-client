from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.conversation_response import ConversationResponse
from ...models.create_conversation import CreateConversation


def _get_kwargs(
    *,
    body: CreateConversation | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/conversations",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ConversationResponse | None:
    if response.status_code == 201:
        response_201 = ConversationResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ConversationResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateConversation | Unset = UNSET,
) -> Response[ConversationResponse]:
    """Create discussion conversation

     Create a new [conversation](https://dev.frontapp.com/reference/conversations#creating-a-new-
    conversation) that only supports comments (known as discussions in Front). If you want to create a
    conversation that supports messages, use the [Create
    message](https://dev.frontapp.com/reference/post_channels-channel-id-messages) endpoint. If you want
    to add a comment to an existing conversation, use the [Add
    comment](https://dev.frontapp.com/reference/post_conversations-conversation-id-comments) endpoint.

    Required scope: `conversations:write`

    Args:
        body (CreateConversation | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ConversationResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CreateConversation | Unset = UNSET,
) -> ConversationResponse | None:
    """Create discussion conversation

     Create a new [conversation](https://dev.frontapp.com/reference/conversations#creating-a-new-
    conversation) that only supports comments (known as discussions in Front). If you want to create a
    conversation that supports messages, use the [Create
    message](https://dev.frontapp.com/reference/post_channels-channel-id-messages) endpoint. If you want
    to add a comment to an existing conversation, use the [Add
    comment](https://dev.frontapp.com/reference/post_conversations-conversation-id-comments) endpoint.

    Required scope: `conversations:write`

    Args:
        body (CreateConversation | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ConversationResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateConversation | Unset = UNSET,
) -> Response[ConversationResponse]:
    """Create discussion conversation

     Create a new [conversation](https://dev.frontapp.com/reference/conversations#creating-a-new-
    conversation) that only supports comments (known as discussions in Front). If you want to create a
    conversation that supports messages, use the [Create
    message](https://dev.frontapp.com/reference/post_channels-channel-id-messages) endpoint. If you want
    to add a comment to an existing conversation, use the [Add
    comment](https://dev.frontapp.com/reference/post_conversations-conversation-id-comments) endpoint.

    Required scope: `conversations:write`

    Args:
        body (CreateConversation | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ConversationResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateConversation | Unset = UNSET,
) -> ConversationResponse | None:
    """Create discussion conversation

     Create a new [conversation](https://dev.frontapp.com/reference/conversations#creating-a-new-
    conversation) that only supports comments (known as discussions in Front). If you want to create a
    conversation that supports messages, use the [Create
    message](https://dev.frontapp.com/reference/post_channels-channel-id-messages) endpoint. If you want
    to add a comment to an existing conversation, use the [Add
    comment](https://dev.frontapp.com/reference/post_conversations-conversation-id-comments) endpoint.

    Required scope: `conversations:write`

    Args:
        body (CreateConversation | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ConversationResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
