from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_accounts_response_200 import ListAccountsResponse200
from ...models.list_accounts_sort_order import ListAccountsSortOrder


def _get_kwargs(
    *,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountsSortOrder | Unset = UNSET,
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
        "url": "/accounts",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListAccountsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListAccountsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListAccountsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountsSortOrder | Unset = UNSET,
) -> Response[ListAccountsResponse200]:
    """List Accounts

     List the accounts of the company.

    Required scope: `accounts:read`

    Args:
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListAccountsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListAccountsResponse200]
    """

    kwargs = _get_kwargs(
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
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountsSortOrder | Unset = UNSET,
) -> ListAccountsResponse200 | None:
    """List Accounts

     List the accounts of the company.

    Required scope: `accounts:read`

    Args:
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListAccountsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListAccountsResponse200
    """

    return sync_detailed(
        client=client,
        limit=limit,
        page_token=page_token,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountsSortOrder | Unset = UNSET,
) -> Response[ListAccountsResponse200]:
    """List Accounts

     List the accounts of the company.

    Required scope: `accounts:read`

    Args:
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListAccountsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListAccountsResponse200]
    """

    kwargs = _get_kwargs(
        limit=limit,
        page_token=page_token,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountsSortOrder | Unset = UNSET,
) -> ListAccountsResponse200 | None:
    """List Accounts

     List the accounts of the company.

    Required scope: `accounts:read`

    Args:
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        sort_by (str | Unset):
        sort_order (ListAccountsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListAccountsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            page_token=page_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
