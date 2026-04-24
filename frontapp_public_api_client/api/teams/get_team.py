from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.team_response import TeamResponse


def _get_kwargs(
    team_id: str = "tim_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/teams/{team_id}".format(
            team_id=quote(str(team_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> TeamResponse | None:
    if response.status_code == 200:
        response_200 = TeamResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[TeamResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[TeamResponse]:
    """Get team

     Fetch a team (workspace).

    Required scope: `teams:read`

    Args:
        team_id (str):  Default: 'tim_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[TeamResponse]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
) -> TeamResponse | None:
    """Get team

     Fetch a team (workspace).

    Required scope: `teams:read`

    Args:
        team_id (str):  Default: 'tim_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        TeamResponse
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[TeamResponse]:
    """Get team

     Fetch a team (workspace).

    Required scope: `teams:read`

    Args:
        team_id (str):  Default: 'tim_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[TeamResponse]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
) -> TeamResponse | None:
    """Get team

     Fetch a team (workspace).

    Required scope: `teams:read`

    Args:
        team_id (str):  Default: 'tim_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        TeamResponse
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
        )
    ).parsed
