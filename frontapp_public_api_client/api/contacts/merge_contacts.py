from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.contact_response import ContactResponse
from ...models.merge_contacts import MergeContacts


def _get_kwargs(
    *,
    body: MergeContacts | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/contacts/merge",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    *,
    client: AuthenticatedClient | Client,
    body: MergeContacts | Unset = UNSET,
) -> Response[ContactResponse]:
    """Merge contacts

     Merges the contacts specified into a single contact, deleting the merged-in contacts.
    If a target contact ID is supplied, the other contacts will be merged into that one.
    Otherwise, some contact in the contact ID list will be treated as the target contact.
    Merge conflicts will be resolved in the following ways:
      * name will prioritize manually-updated and non-private contact names
      * descriptions will be concatenated and separated by newlines in order from
        oldest to newest with the (optional) target contact's description first
      * all handles, groups, links, and notes will be preserved
      * other conflicts will use the most recently updated contact's value


    Required scope: `contacts:write`

    Args:
        body (MergeContacts | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ContactResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: MergeContacts | Unset = UNSET,
) -> ContactResponse | None:
    """Merge contacts

     Merges the contacts specified into a single contact, deleting the merged-in contacts.
    If a target contact ID is supplied, the other contacts will be merged into that one.
    Otherwise, some contact in the contact ID list will be treated as the target contact.
    Merge conflicts will be resolved in the following ways:
      * name will prioritize manually-updated and non-private contact names
      * descriptions will be concatenated and separated by newlines in order from
        oldest to newest with the (optional) target contact's description first
      * all handles, groups, links, and notes will be preserved
      * other conflicts will use the most recently updated contact's value


    Required scope: `contacts:write`

    Args:
        body (MergeContacts | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ContactResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: MergeContacts | Unset = UNSET,
) -> Response[ContactResponse]:
    """Merge contacts

     Merges the contacts specified into a single contact, deleting the merged-in contacts.
    If a target contact ID is supplied, the other contacts will be merged into that one.
    Otherwise, some contact in the contact ID list will be treated as the target contact.
    Merge conflicts will be resolved in the following ways:
      * name will prioritize manually-updated and non-private contact names
      * descriptions will be concatenated and separated by newlines in order from
        oldest to newest with the (optional) target contact's description first
      * all handles, groups, links, and notes will be preserved
      * other conflicts will use the most recently updated contact's value


    Required scope: `contacts:write`

    Args:
        body (MergeContacts | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ContactResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: MergeContacts | Unset = UNSET,
) -> ContactResponse | None:
    """Merge contacts

     Merges the contacts specified into a single contact, deleting the merged-in contacts.
    If a target contact ID is supplied, the other contacts will be merged into that one.
    Otherwise, some contact in the contact ID list will be treated as the target contact.
    Merge conflicts will be resolved in the following ways:
      * name will prioritize manually-updated and non-private contact names
      * descriptions will be concatenated and separated by newlines in order from
        oldest to newest with the (optional) target contact's description first
      * all handles, groups, links, and notes will be preserved
      * other conflicts will use the most recently updated contact's value


    Required scope: `contacts:write`

    Args:
        body (MergeContacts | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ContactResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
