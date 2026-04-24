from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_account_contacts_response_200 import ListAccountContactsResponse200
from ...models.list_account_contacts_sort_order import ListAccountContactsSortOrder


def _get_kwargs(
    account_id: str = "acc_123",
    *,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountContactsSortOrder | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["page_token"] = page_token

    params["limit"] = limit

    params["sort_by"] = sort_by

    json_sort_order: str | Unset = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order.value

    params["sort_order"] = json_sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/accounts/{account_id}/contacts".format(
            account_id=quote(str(account_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListAccountContactsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListAccountContactsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListAccountContactsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    account_id: str = "acc_123",
    *,
    client: AuthenticatedClient | Client,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountContactsSortOrder | Unset = UNSET,
) -> Response[ListAccountContactsResponse200]:
    """List account contacts

     Lists the contacts associated with an Account

    Required scope: `contacts:read`

    Args:
        account_id (str):  Default: 'acc_123'.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        limit (int | Unset):  Example: 25.
        sort_by (str | Unset):
        sort_order (ListAccountContactsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListAccountContactsResponse200]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        page_token=page_token,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str = "acc_123",
    *,
    client: AuthenticatedClient | Client,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountContactsSortOrder | Unset = UNSET,
) -> ListAccountContactsResponse200 | None:
    """List account contacts

     Lists the contacts associated with an Account

    Required scope: `contacts:read`

    Args:
        account_id (str):  Default: 'acc_123'.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        limit (int | Unset):  Example: 25.
        sort_by (str | Unset):
        sort_order (ListAccountContactsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListAccountContactsResponse200
    """

    return sync_detailed(
        account_id=account_id,
        client=client,
        page_token=page_token,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    account_id: str = "acc_123",
    *,
    client: AuthenticatedClient | Client,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountContactsSortOrder | Unset = UNSET,
) -> Response[ListAccountContactsResponse200]:
    """List account contacts

     Lists the contacts associated with an Account

    Required scope: `contacts:read`

    Args:
        account_id (str):  Default: 'acc_123'.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        limit (int | Unset):  Example: 25.
        sort_by (str | Unset):
        sort_order (ListAccountContactsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListAccountContactsResponse200]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        page_token=page_token,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str = "acc_123",
    *,
    client: AuthenticatedClient | Client,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    sort_by: str | Unset = UNSET,
    sort_order: ListAccountContactsSortOrder | Unset = UNSET,
) -> ListAccountContactsResponse200 | None:
    """List account contacts

     Lists the contacts associated with an Account

    Required scope: `contacts:read`

    Args:
        account_id (str):  Default: 'acc_123'.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        limit (int | Unset):  Example: 25.
        sort_by (str | Unset):
        sort_order (ListAccountContactsSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListAccountContactsResponse200
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            client=client,
            page_token=page_token,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
