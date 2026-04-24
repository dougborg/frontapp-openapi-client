from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_teammate_folders_response_200 import ListTeammateFoldersResponse200
from ...models.list_teammate_folders_sort_order import ListTeammateFoldersSortOrder


def _get_kwargs(
    teammate_id: str = "tea_123",
    *,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateFoldersSortOrder | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["sort_by"] = sort_by

    json_sort_order: str | Unset = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order.value

    params["sort_order"] = json_sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/teammates/{teammate_id}/message_template_folders".format(
            teammate_id=quote(str(teammate_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListTeammateFoldersResponse200 | None:
    if response.status_code == 200:
        response_200 = ListTeammateFoldersResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListTeammateFoldersResponse200]:
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
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateFoldersSortOrder | Unset = UNSET,
) -> Response[ListTeammateFoldersResponse200]:
    """List teammate folders

     List the message template folders belonging to the requested teammate.

    Required scope: `message_templates:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        sort_by (str | Unset):
        sort_order (ListTeammateFoldersSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeammateFoldersResponse200]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateFoldersSortOrder | Unset = UNSET,
) -> ListTeammateFoldersResponse200 | None:
    """List teammate folders

     List the message template folders belonging to the requested teammate.

    Required scope: `message_templates:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        sort_by (str | Unset):
        sort_order (ListTeammateFoldersSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeammateFoldersResponse200
    """

    return sync_detailed(
        teammate_id=teammate_id,
        client=client,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateFoldersSortOrder | Unset = UNSET,
) -> Response[ListTeammateFoldersResponse200]:
    """List teammate folders

     List the message template folders belonging to the requested teammate.

    Required scope: `message_templates:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        sort_by (str | Unset):
        sort_order (ListTeammateFoldersSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeammateFoldersResponse200]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateFoldersSortOrder | Unset = UNSET,
) -> ListTeammateFoldersResponse200 | None:
    """List teammate folders

     List the message template folders belonging to the requested teammate.

    Required scope: `message_templates:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        sort_by (str | Unset):
        sort_order (ListTeammateFoldersSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeammateFoldersResponse200
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
