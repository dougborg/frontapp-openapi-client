from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_contacts_in_group_response_200 import ListContactsInGroupResponse200


def _get_kwargs(
    contact_group_id: str = "grp_123",
    *,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["page_token"] = page_token

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contact_groups/{contact_group_id}/contacts".format(
            contact_group_id=quote(str(contact_group_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListContactsInGroupResponse200 | None:
    if response.status_code == 200:
        response_200 = ListContactsInGroupResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListContactsInGroupResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    contact_group_id: str = "grp_123",
    *,
    client: AuthenticatedClient | Client,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> Response[ListContactsInGroupResponse200]:
    """List contacts in group

     List the contacts belonging to the requested group.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the compatible contact list endpoints instead.
    > - `GET /contact_lists/{contact_list_id}/contacts`.


    Required scope: `contacts:read`

    Args:
        contact_group_id (str):  Default: 'grp_123'.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        limit (int | Unset):  Example: 25.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListContactsInGroupResponse200]
    """

    kwargs = _get_kwargs(
        contact_group_id=contact_group_id,
        page_token=page_token,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    contact_group_id: str = "grp_123",
    *,
    client: AuthenticatedClient | Client,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> ListContactsInGroupResponse200 | None:
    """List contacts in group

     List the contacts belonging to the requested group.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the compatible contact list endpoints instead.
    > - `GET /contact_lists/{contact_list_id}/contacts`.


    Required scope: `contacts:read`

    Args:
        contact_group_id (str):  Default: 'grp_123'.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        limit (int | Unset):  Example: 25.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListContactsInGroupResponse200
    """

    return sync_detailed(
        contact_group_id=contact_group_id,
        client=client,
        page_token=page_token,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    contact_group_id: str = "grp_123",
    *,
    client: AuthenticatedClient | Client,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> Response[ListContactsInGroupResponse200]:
    """List contacts in group

     List the contacts belonging to the requested group.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the compatible contact list endpoints instead.
    > - `GET /contact_lists/{contact_list_id}/contacts`.


    Required scope: `contacts:read`

    Args:
        contact_group_id (str):  Default: 'grp_123'.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        limit (int | Unset):  Example: 25.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListContactsInGroupResponse200]
    """

    kwargs = _get_kwargs(
        contact_group_id=contact_group_id,
        page_token=page_token,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    contact_group_id: str = "grp_123",
    *,
    client: AuthenticatedClient | Client,
    page_token: str | Unset = UNSET,
    limit: int | Unset = UNSET,
) -> ListContactsInGroupResponse200 | None:
    """List contacts in group

     List the contacts belonging to the requested group.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the compatible contact list endpoints instead.
    > - `GET /contact_lists/{contact_list_id}/contacts`.


    Required scope: `contacts:read`

    Args:
        contact_group_id (str):  Default: 'grp_123'.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.
        limit (int | Unset):  Example: 25.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListContactsInGroupResponse200
    """

    return (
        await asyncio_detailed(
            contact_group_id=contact_group_id,
            client=client,
            page_token=page_token,
            limit=limit,
        )
    ).parsed
