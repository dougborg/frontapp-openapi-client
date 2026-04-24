from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_teammate_contacts_response_200 import (
    ListTeammateContactsResponse200,
)
from ...models.list_teammate_contacts_sort_order import ListTeammateContactsSortOrder


def _get_kwargs(
    teammate_id: str = "tea_123",
    *,
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateContactsSortOrder | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["q"] = q

    params["limit"] = limit

    params["page_token"] = page_token

    params["sort_by"] = sort_by

    json_sort_order: str | Unset = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order.value

    params["sort_order"] = json_sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/teammates/{teammate_id}/contacts".format(
            teammate_id=quote(str(teammate_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListTeammateContactsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListTeammateContactsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListTeammateContactsResponse200]:
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
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateContactsSortOrder | Unset = UNSET,
) -> Response[ListTeammateContactsResponse200]:
    """List teammate contacts

     List the contacts of a teammate.

    Required scope: `contacts:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        q (str | Unset):
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListTeammateContactsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeammateContactsResponse200]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
        q=q,
        limit=limit,
        page_token=page_token,
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
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateContactsSortOrder | Unset = UNSET,
) -> ListTeammateContactsResponse200 | None:
    """List teammate contacts

     List the contacts of a teammate.

    Required scope: `contacts:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        q (str | Unset):
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListTeammateContactsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeammateContactsResponse200
    """

    return sync_detailed(
        teammate_id=teammate_id,
        client=client,
        q=q,
        limit=limit,
        page_token=page_token,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateContactsSortOrder | Unset = UNSET,
) -> Response[ListTeammateContactsResponse200]:
    """List teammate contacts

     List the contacts of a teammate.

    Required scope: `contacts:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        q (str | Unset):
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListTeammateContactsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeammateContactsResponse200]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
        q=q,
        limit=limit,
        page_token=page_token,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateContactsSortOrder | Unset = UNSET,
) -> ListTeammateContactsResponse200 | None:
    """List teammate contacts

     List the contacts of a teammate.

    Required scope: `contacts:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        q (str | Unset):
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListTeammateContactsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeammateContactsResponse200
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
            q=q,
            limit=limit,
            page_token=page_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
