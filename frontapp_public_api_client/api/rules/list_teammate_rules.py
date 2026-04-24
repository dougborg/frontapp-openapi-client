from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.list_teammate_rules_response_200 import ListTeammateRulesResponse200


def _get_kwargs(
    teammate_id: str = "tea_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/teammates/{teammate_id}/rules".format(
            teammate_id=quote(str(teammate_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListTeammateRulesResponse200 | None:
    if response.status_code == 200:
        response_200 = ListTeammateRulesResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListTeammateRulesResponse200]:
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
) -> Response[ListTeammateRulesResponse200]:
    """List teammate rules

     List the rules of a teammate.

    Required scope: `rules:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeammateRulesResponse200]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListTeammateRulesResponse200 | None:
    """List teammate rules

     List the rules of a teammate.

    Required scope: `rules:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeammateRulesResponse200
    """

    return sync_detailed(
        teammate_id=teammate_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListTeammateRulesResponse200]:
    """List teammate rules

     List the rules of a teammate.

    Required scope: `rules:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeammateRulesResponse200]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListTeammateRulesResponse200 | None:
    """List teammate rules

     List the rules of a teammate.

    Required scope: `rules:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeammateRulesResponse200
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
        )
    ).parsed
