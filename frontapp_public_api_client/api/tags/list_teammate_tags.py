from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_teammate_tags_response_200 import ListTeammateTagsResponse200
from ...models.list_teammate_tags_sort_order import ListTeammateTagsSortOrder


def _get_kwargs(
    teammate_id: str = "tea_123",
    *,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateTagsSortOrder | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

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
        "url": "/teammates/{teammate_id}/tags".format(
            teammate_id=quote(str(teammate_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListTeammateTagsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListTeammateTagsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListTeammateTagsResponse200]:
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
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateTagsSortOrder | Unset = UNSET,
) -> Response[ListTeammateTagsResponse200]:
    """List teammate tags

     List the tags for a teammate.

    Required scope: `tags:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListTeammateTagsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeammateTagsResponse200]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
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
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateTagsSortOrder | Unset = UNSET,
) -> ListTeammateTagsResponse200 | None:
    """List teammate tags

     List the tags for a teammate.

    Required scope: `tags:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListTeammateTagsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeammateTagsResponse200
    """

    return sync_detailed(
        teammate_id=teammate_id,
        client=client,
        limit=limit,
        page_token=page_token,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateTagsSortOrder | Unset = UNSET,
) -> Response[ListTeammateTagsResponse200]:
    """List teammate tags

     List the tags for a teammate.

    Required scope: `tags:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListTeammateTagsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListTeammateTagsResponse200]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
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
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListTeammateTagsSortOrder | Unset = UNSET,
) -> ListTeammateTagsResponse200 | None:
    """List teammate tags

     List the tags for a teammate.

    Required scope: `tags:read`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListTeammateTagsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListTeammateTagsResponse200
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
            limit=limit,
            page_token=page_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
