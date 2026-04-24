from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.comment_response import CommentResponse
from ...models.create_comment import CreateComment


def _get_kwargs(
    conversation_id: str = "cnv_123",
    *,
    body: CreateComment | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/conversations/{conversation_id}/comments".format(
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
) -> Any | CommentResponse | None:
    if response.status_code == 201:
        response_201 = CommentResponse.from_dict(response.json())

        return response_201

    if response.status_code == 301:
        response_301 = cast(Any, None)
        return response_301

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | CommentResponse]:
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
    body: CreateComment | Unset = UNSET,
) -> Response[Any | CommentResponse]:
    """Add comment

     Add a comment to a [conversation](https://dev.frontapp.com/reference/conversations). If you want to
    create a new comment-only conversation, use the [Create discussion
    conversation](https://dev.frontapp.com/reference/create-conversation) endpoint.

    Required scope: `comments:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (CreateComment | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | CommentResponse]
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
    body: CreateComment | Unset = UNSET,
) -> Any | CommentResponse | None:
    """Add comment

     Add a comment to a [conversation](https://dev.frontapp.com/reference/conversations). If you want to
    create a new comment-only conversation, use the [Create discussion
    conversation](https://dev.frontapp.com/reference/create-conversation) endpoint.

    Required scope: `comments:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (CreateComment | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | CommentResponse
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
    body: CreateComment | Unset = UNSET,
) -> Response[Any | CommentResponse]:
    """Add comment

     Add a comment to a [conversation](https://dev.frontapp.com/reference/conversations). If you want to
    create a new comment-only conversation, use the [Create discussion
    conversation](https://dev.frontapp.com/reference/create-conversation) endpoint.

    Required scope: `comments:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (CreateComment | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | CommentResponse]
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
    body: CreateComment | Unset = UNSET,
) -> Any | CommentResponse | None:
    """Add comment

     Add a comment to a [conversation](https://dev.frontapp.com/reference/conversations). If you want to
    create a new comment-only conversation, use the [Create discussion
    conversation](https://dev.frontapp.com/reference/create-conversation) endpoint.

    Required scope: `comments:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (CreateComment | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | CommentResponse
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            client=client,
            body=body,
        )
    ).parsed
