from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.link_response import LinkResponse


def _get_kwargs(
    link_id: str = "top_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/links/{link_id}".format(
            link_id=quote(str(link_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LinkResponse | None:
    if response.status_code == 200:
        response_200 = LinkResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[LinkResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    link_id: str = "top_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[LinkResponse]:
    """Get link

     Fetch a link.
    For more information on links, see the [Links](https://dev.frontapp.com/reference/links) topic.


    Required scope: `links:read`

    Args:
        link_id (str):  Default: 'top_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[LinkResponse]
    """

    kwargs = _get_kwargs(
        link_id=link_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    link_id: str = "top_123",
    *,
    client: AuthenticatedClient | Client,
) -> LinkResponse | None:
    """Get link

     Fetch a link.
    For more information on links, see the [Links](https://dev.frontapp.com/reference/links) topic.


    Required scope: `links:read`

    Args:
        link_id (str):  Default: 'top_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        LinkResponse
    """

    return sync_detailed(
        link_id=link_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    link_id: str = "top_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[LinkResponse]:
    """Get link

     Fetch a link.
    For more information on links, see the [Links](https://dev.frontapp.com/reference/links) topic.


    Required scope: `links:read`

    Args:
        link_id (str):  Default: 'top_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[LinkResponse]
    """

    kwargs = _get_kwargs(
        link_id=link_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    link_id: str = "top_123",
    *,
    client: AuthenticatedClient | Client,
) -> LinkResponse | None:
    """Get link

     Fetch a link.
    For more information on links, see the [Links](https://dev.frontapp.com/reference/links) topic.


    Required scope: `links:read`

    Args:
        link_id (str):  Default: 'top_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        LinkResponse
    """

    return (
        await asyncio_detailed(
            link_id=link_id,
            client=client,
        )
    ).parsed
