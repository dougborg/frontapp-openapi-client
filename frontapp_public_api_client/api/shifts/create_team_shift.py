from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_shift import CreateShift
from ...models.shift_response import ShiftResponse


def _get_kwargs(
    team_id: str = "tim_123",
    *,
    body: CreateShift | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/teams/{team_id}/shifts".format(
            team_id=quote(str(team_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ShiftResponse | None:
    if response.status_code == 201:
        response_201 = ShiftResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ShiftResponse]:
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
    body: CreateShift | Unset = UNSET,
) -> Response[ShiftResponse]:
    """Create team shift

     Create a shift for a team (workspace).

    Required scope: `shifts:write`

    Args:
        team_id (str):  Default: 'tim_123'.
        body (CreateShift | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ShiftResponse]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateShift | Unset = UNSET,
) -> ShiftResponse | None:
    """Create team shift

     Create a shift for a team (workspace).

    Required scope: `shifts:write`

    Args:
        team_id (str):  Default: 'tim_123'.
        body (CreateShift | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ShiftResponse
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateShift | Unset = UNSET,
) -> Response[ShiftResponse]:
    """Create team shift

     Create a shift for a team (workspace).

    Required scope: `shifts:write`

    Args:
        team_id (str):  Default: 'tim_123'.
        body (CreateShift | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ShiftResponse]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateShift | Unset = UNSET,
) -> ShiftResponse | None:
    """Create team shift

     Create a shift for a team (workspace).

    Required scope: `shifts:write`

    Args:
        team_id (str):  Default: 'tim_123'.
        body (CreateShift | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ShiftResponse
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            body=body,
        )
    ).parsed
