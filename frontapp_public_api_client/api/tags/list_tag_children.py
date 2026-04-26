from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.list_tag_children_response_200 import ListTagChildrenResponse200


def _get_kwargs(
    tag_id: str = "tag_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tags/{tag_id}/children".format(
            tag_id=quote(str(tag_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListTagChildrenResponse200 | None:
    if response.status_code == 200:
        response_200 = ListTagChildrenResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListTagChildrenResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tag_id: str = "tag_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListTagChildrenResponse200]:
    """List tag children

     List the children of a specific tag.

    Required scope: `tags:read`

    Args:
        tag_id (str):  Default: 'tag_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTagChildrenResponse200]
    """

    kwargs = _get_kwargs(
        tag_id=tag_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tag_id: str = "tag_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListTagChildrenResponse200 | None:
    """List tag children

     List the children of a specific tag.

    Required scope: `tags:read`

    Args:
        tag_id (str):  Default: 'tag_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTagChildrenResponse200
    """

    return sync_detailed(
        tag_id=tag_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    tag_id: str = "tag_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListTagChildrenResponse200]:
    """List tag children

     List the children of a specific tag.

    Required scope: `tags:read`

    Args:
        tag_id (str):  Default: 'tag_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTagChildrenResponse200]
    """

    kwargs = _get_kwargs(
        tag_id=tag_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tag_id: str = "tag_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListTagChildrenResponse200 | None:
    """List tag children

     List the children of a specific tag.

    Required scope: `tags:read`

    Args:
        tag_id (str):  Default: 'tag_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTagChildrenResponse200
    """

    return (
        await asyncio_detailed(
            tag_id=tag_id,
            client=client,
        )
    ).parsed
