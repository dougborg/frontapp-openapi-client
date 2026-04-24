from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.contact_note_responses import ContactNoteResponses
from ...models.create_contact_note import CreateContactNote


def _get_kwargs(
    contact_id: str = "crd_123",
    *,
    body: CreateContactNote | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/contacts/{contact_id}/notes".format(
            contact_id=quote(str(contact_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContactNoteResponses | None:
    if response.status_code == 201:
        response_201 = ContactNoteResponses.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ContactNoteResponses]:
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
    body: CreateContactNote | Unset = UNSET,
) -> Response[ContactNoteResponses]:
    """Add note

     Create a new note on a contact.

    Required scope: `contacts:write`

    Args:
        contact_id (str):  Default: 'crd_123'.
        body (CreateContactNote | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ContactNoteResponses]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateContactNote | Unset = UNSET,
) -> ContactNoteResponses | None:
    """Add note

     Create a new note on a contact.

    Required scope: `contacts:write`

    Args:
        contact_id (str):  Default: 'crd_123'.
        body (CreateContactNote | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ContactNoteResponses
    """

    return sync_detailed(
        contact_id=contact_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateContactNote | Unset = UNSET,
) -> Response[ContactNoteResponses]:
    """Add note

     Create a new note on a contact.

    Required scope: `contacts:write`

    Args:
        contact_id (str):  Default: 'crd_123'.
        body (CreateContactNote | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ContactNoteResponses]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    contact_id: str = "crd_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateContactNote | Unset = UNSET,
) -> ContactNoteResponses | None:
    """Add note

     Create a new note on a contact.

    Required scope: `contacts:write`

    Args:
        contact_id (str):  Default: 'crd_123'.
        body (CreateContactNote | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ContactNoteResponses
    """

    return (
        await asyncio_detailed(
            contact_id=contact_id,
            client=client,
            body=body,
        )
    ).parsed
