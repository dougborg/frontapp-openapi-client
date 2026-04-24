from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.list_comment_mentions_response_200 import ListCommentMentionsResponse200


def _get_kwargs(
    comment_id: str = "com_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/comments/{comment_id}/mentions".format(
            comment_id=quote(str(comment_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListCommentMentionsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListCommentMentionsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListCommentMentionsResponse200]:
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
) -> Response[ListCommentMentionsResponse200]:
    """List comment mentions

     List the teammates mentioned in a comment.

    Required scope: `teammates:read`

    Args:
        comment_id (str):  Default: 'com_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListCommentMentionsResponse200]
    """

    kwargs = _get_kwargs(
        comment_id=comment_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    comment_id: str = "com_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListCommentMentionsResponse200 | None:
    """List comment mentions

     List the teammates mentioned in a comment.

    Required scope: `teammates:read`

    Args:
        comment_id (str):  Default: 'com_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListCommentMentionsResponse200
    """

    return sync_detailed(
        comment_id=comment_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    comment_id: str = "com_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListCommentMentionsResponse200]:
    """List comment mentions

     List the teammates mentioned in a comment.

    Required scope: `teammates:read`

    Args:
        comment_id (str):  Default: 'com_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListCommentMentionsResponse200]
    """

    kwargs = _get_kwargs(
        comment_id=comment_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    comment_id: str = "com_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListCommentMentionsResponse200 | None:
    """List comment mentions

     List the teammates mentioned in a comment.

    Required scope: `teammates:read`

    Args:
        comment_id (str):  Default: 'com_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListCommentMentionsResponse200
    """

    return (
        await asyncio_detailed(
            comment_id=comment_id,
            client=client,
        )
    ).parsed
