from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_team_views_response_200 import ListTeamViewsResponse200


def _get_kwargs(
    team_id: str = "tim_xyz",
    *,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["page_token"] = page_token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/teams/{team_id}/views".format(
            team_id=quote(str(team_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListTeamViewsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListTeamViewsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListTeamViewsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str = "tim_xyz",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[ListTeamViewsResponse200]:
    """List team views

     List the views of a team.

    Required scope: `views:read`

    Args:
        team_id (str):  Default: 'tim_xyz'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeamViewsResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        limit=limit,
        page_token=page_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str = "tim_xyz",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> ListTeamViewsResponse200 | None:
    """List team views

     List the views of a team.

    Required scope: `views:read`

    Args:
        team_id (str):  Default: 'tim_xyz'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeamViewsResponse200
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        limit=limit,
        page_token=page_token,
    ).parsed


async def asyncio_detailed(
    team_id: str = "tim_xyz",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[ListTeamViewsResponse200]:
    """List team views

     List the views of a team.

    Required scope: `views:read`

    Args:
        team_id (str):  Default: 'tim_xyz'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeamViewsResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        limit=limit,
        page_token=page_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str = "tim_xyz",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> ListTeamViewsResponse200 | None:
    """List team views

     List the views of a team.

    Required scope: `views:read`

    Args:
        team_id (str):  Default: 'tim_xyz'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeamViewsResponse200
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            limit=limit,
            page_token=page_token,
        )
    ).parsed
