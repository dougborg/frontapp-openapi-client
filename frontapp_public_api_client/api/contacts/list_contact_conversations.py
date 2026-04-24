from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_contact_conversations_response_200 import (
    ListContactConversationsResponse200,
)


def _get_kwargs(
    contact_id: str = "crd_123",
    *,
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["q"] = q

    params["limit"] = limit

    params["page_token"] = page_token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contacts/{contact_id}/conversations".format(
            contact_id=quote(str(contact_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListContactConversationsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListContactConversationsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListContactConversationsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[ListContactConversationsResponse200]:
    """List contact conversations

     List the conversations for a contact in reverse chronological order (newest first). For more
    advanced filtering, see the [search
    endpoint](https://dev.frontapp.com/reference/conversations#search-conversations).


    Required scope: `conversations:read`

    Args:
        contact_id (str):  Default: 'crd_123'.
        q (str | Unset):
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListContactConversationsResponse200]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        q=q,
        limit=limit,
        page_token=page_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> ListContactConversationsResponse200 | None:
    """List contact conversations

     List the conversations for a contact in reverse chronological order (newest first). For more
    advanced filtering, see the [search
    endpoint](https://dev.frontapp.com/reference/conversations#search-conversations).


    Required scope: `conversations:read`

    Args:
        contact_id (str):  Default: 'crd_123'.
        q (str | Unset):
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListContactConversationsResponse200
    """

    return sync_detailed(
        contact_id=contact_id,
        client=client,
        q=q,
        limit=limit,
        page_token=page_token,
    ).parsed


async def asyncio_detailed(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[ListContactConversationsResponse200]:
    """List contact conversations

     List the conversations for a contact in reverse chronological order (newest first). For more
    advanced filtering, see the [search
    endpoint](https://dev.frontapp.com/reference/conversations#search-conversations).


    Required scope: `conversations:read`

    Args:
        contact_id (str):  Default: 'crd_123'.
        q (str | Unset):
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListContactConversationsResponse200]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        q=q,
        limit=limit,
        page_token=page_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> ListContactConversationsResponse200 | None:
    """List contact conversations

     List the conversations for a contact in reverse chronological order (newest first). For more
    advanced filtering, see the [search
    endpoint](https://dev.frontapp.com/reference/conversations#search-conversations).


    Required scope: `conversations:read`

    Args:
        contact_id (str):  Default: 'crd_123'.
        q (str | Unset):
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListContactConversationsResponse200
    """

    return (
        await asyncio_detailed(
            contact_id=contact_id,
            client=client,
            q=q,
            limit=limit,
            page_token=page_token,
        )
    ).parsed
