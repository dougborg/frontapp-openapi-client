from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.comment_response import CommentResponse
from ...models.update_comment import UpdateComment


def _get_kwargs(
    comment_id: str = "com_123",
    *,
    body: UpdateComment | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/comments/{comment_id}/".format(
            comment_id=quote(str(comment_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CommentResponse | None:
    if response.status_code == 200:
        response_200 = CommentResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CommentResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    comment_id: str = "com_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateComment | Unset = UNSET,
) -> Response[CommentResponse]:
    """Update comment

     Update a comment in a [conversation](https://dev.frontapp.com/reference/conversations).

    Required scope: `comments:write`

    Args:
        comment_id (str):  Default: 'com_123'.
        body (UpdateComment | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[CommentResponse]
    """

    kwargs = _get_kwargs(
        comment_id=comment_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    comment_id: str = "com_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateComment | Unset = UNSET,
) -> CommentResponse | None:
    """Update comment

     Update a comment in a [conversation](https://dev.frontapp.com/reference/conversations).

    Required scope: `comments:write`

    Args:
        comment_id (str):  Default: 'com_123'.
        body (UpdateComment | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        CommentResponse
    """

    return sync_detailed(
        comment_id=comment_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    comment_id: str = "com_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateComment | Unset = UNSET,
) -> Response[CommentResponse]:
    """Update comment

     Update a comment in a [conversation](https://dev.frontapp.com/reference/conversations).

    Required scope: `comments:write`

    Args:
        comment_id (str):  Default: 'com_123'.
        body (UpdateComment | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[CommentResponse]
    """

    kwargs = _get_kwargs(
        comment_id=comment_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    comment_id: str = "com_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateComment | Unset = UNSET,
) -> CommentResponse | None:
    """Update comment

     Update a comment in a [conversation](https://dev.frontapp.com/reference/conversations).

    Required scope: `comments:write`

    Args:
        comment_id (str):  Default: 'com_123'.
        body (UpdateComment | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        CommentResponse
    """

    return (
        await asyncio_detailed(
            comment_id=comment_id,
            client=client,
            body=body,
        )
    ).parsed
