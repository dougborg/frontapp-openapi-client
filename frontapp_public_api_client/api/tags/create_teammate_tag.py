from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_tag import CreateTag
from ...models.tag_response import TagResponse


def _get_kwargs(
    teammate_id: str = "tea_123",
    *,
    body: CreateTag | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/teammates/{teammate_id}/tags".format(
            teammate_id=quote(str(teammate_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> TagResponse | None:
    if response.status_code == 201:
        response_201 = TagResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[TagResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateTag | Unset = UNSET,
) -> Response[TagResponse]:
    """Create teammate tag

     Create a tag for a teammate.

    Required scope: `tags:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreateTag | Unset): A tag is a label that can be used to classify conversations.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[TagResponse]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateTag | Unset = UNSET,
) -> TagResponse | None:
    """Create teammate tag

     Create a tag for a teammate.

    Required scope: `tags:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreateTag | Unset): A tag is a label that can be used to classify conversations.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        TagResponse
    """

    return sync_detailed(
        teammate_id=teammate_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateTag | Unset = UNSET,
) -> Response[TagResponse]:
    """Create teammate tag

     Create a tag for a teammate.

    Required scope: `tags:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreateTag | Unset): A tag is a label that can be used to classify conversations.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[TagResponse]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateTag | Unset = UNSET,
) -> TagResponse | None:
    """Create teammate tag

     Create a tag for a teammate.

    Required scope: `tags:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreateTag | Unset): A tag is a label that can be used to classify conversations.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        TagResponse
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
            body=body,
        )
    ).parsed
