from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.contact_response import ContactResponse


def _get_kwargs(
    contact_id: str = "crd_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contacts/{contact_id}".format(
            contact_id=quote(str(contact_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContactResponse | None:
    if response.status_code == 200:
        response_200 = ContactResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ContactResponse]:
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
) -> Response[ContactResponse]:
    """Get contact

     Fetch a contact.

    Required scope: `contacts:read`

    Args:
        contact_id (str):  Default: 'crd_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ContactResponse]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
) -> ContactResponse | None:
    """Get contact

     Fetch a contact.

    Required scope: `contacts:read`

    Args:
        contact_id (str):  Default: 'crd_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ContactResponse
    """

    return sync_detailed(
        contact_id=contact_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ContactResponse]:
    """Get contact

     Fetch a contact.

    Required scope: `contacts:read`

    Args:
        contact_id (str):  Default: 'crd_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ContactResponse]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
) -> ContactResponse | None:
    """Get contact

     Fetch a contact.

    Required scope: `contacts:read`

    Args:
        contact_id (str):  Default: 'crd_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ContactResponse
    """

    return (
        await asyncio_detailed(
            contact_id=contact_id,
            client=client,
        )
    ).parsed
