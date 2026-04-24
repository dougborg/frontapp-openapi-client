from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_teammate_group import CreateTeammateGroup
from ...models.teammate_group_response import TeammateGroupResponse


def _get_kwargs(
    *,
    body: CreateTeammateGroup | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/teammate_groups",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> TeammateGroupResponse | None:
    if response.status_code == 201:
        response_201 = TeammateGroupResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[TeammateGroupResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateTeammateGroup | Unset = UNSET,
) -> Response[TeammateGroupResponse]:
    """Create teammate group

     Create a new teammate group.

    Required scope: `teammate_groups:write`

    Args:
        body (CreateTeammateGroup | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[TeammateGroupResponse]
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
    body: CreateTeammateGroup | Unset = UNSET,
) -> TeammateGroupResponse | None:
    """Create teammate group

     Create a new teammate group.

    Required scope: `teammate_groups:write`

    Args:
        body (CreateTeammateGroup | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        TeammateGroupResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateTeammateGroup | Unset = UNSET,
) -> Response[TeammateGroupResponse]:
    """Create teammate group

     Create a new teammate group.

    Required scope: `teammate_groups:write`

    Args:
        body (CreateTeammateGroup | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[TeammateGroupResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateTeammateGroup | Unset = UNSET,
) -> TeammateGroupResponse | None:
    """Create teammate group

     Create a new teammate group.

    Required scope: `teammate_groups:write`

    Args:
        body (CreateTeammateGroup | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        TeammateGroupResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
