from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.shared_view_response import SharedViewResponse


def _get_kwargs(
    view_id: str = "lns_abc123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/views/{view_id}".format(
            view_id=quote(str(view_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SharedViewResponse | None:
    if response.status_code == 200:
        response_200 = SharedViewResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SharedViewResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    view_id: str = "lns_abc123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[SharedViewResponse]:
    """Get view

     Fetch a view.

    Required scope: `views:read`

    Args:
        view_id (str):  Default: 'lns_abc123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SharedViewResponse]
    """

    kwargs = _get_kwargs(
        view_id=view_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    view_id: str = "lns_abc123",
    *,
    client: AuthenticatedClient | Client,
) -> SharedViewResponse | None:
    """Get view

     Fetch a view.

    Required scope: `views:read`

    Args:
        view_id (str):  Default: 'lns_abc123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SharedViewResponse
    """

    return sync_detailed(
        view_id=view_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    view_id: str = "lns_abc123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[SharedViewResponse]:
    """Get view

     Fetch a view.

    Required scope: `views:read`

    Args:
        view_id (str):  Default: 'lns_abc123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SharedViewResponse]
    """

    kwargs = _get_kwargs(
        view_id=view_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    view_id: str = "lns_abc123",
    *,
    client: AuthenticatedClient | Client,
) -> SharedViewResponse | None:
    """Get view

     Fetch a view.

    Required scope: `views:read`

    Args:
        view_id (str):  Default: 'lns_abc123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SharedViewResponse
    """

    return (
        await asyncio_detailed(
            view_id=view_id,
            client=client,
        )
    ).parsed
