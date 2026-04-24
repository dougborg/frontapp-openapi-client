from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.add_contacts_to_list import AddContactsToList


def _get_kwargs(
    contact_list_id: str = "grp_123",
    *,
    body: AddContactsToList | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/contact_lists/{contact_list_id}/contacts".format(
            contact_list_id=quote(str(contact_list_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 204:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    contact_list_id: str = "grp_123",
    *,
    client: AuthenticatedClient | Client,
    body: AddContactsToList | Unset = UNSET,
) -> Response[Any]:
    """Add contacts to contact list

     Add contacts to the requested contact list.

    Required scope: `contacts:write`

    Args:
        contact_list_id (str):  Default: 'grp_123'.
        body (AddContactsToList | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        contact_list_id=contact_list_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    contact_list_id: str = "grp_123",
    *,
    client: AuthenticatedClient | Client,
    body: AddContactsToList | Unset = UNSET,
) -> Response[Any]:
    """Add contacts to contact list

     Add contacts to the requested contact list.

    Required scope: `contacts:write`

    Args:
        contact_list_id (str):  Default: 'grp_123'.
        body (AddContactsToList | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        contact_list_id=contact_list_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
