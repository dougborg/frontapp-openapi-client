from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response


def _get_kwargs(
    contact_group_id: str = "grp_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/contact_groups/{contact_group_id}".format(
            contact_group_id=quote(str(contact_group_id), safe=""),
        ),
    }

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
    contact_group_id: str = "grp_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any]:
    """Delete group

     Delete a contact group.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the compatible contact list endpoints instead.
    > - `DELETE /contact_lists/{contact_list_id}`.


    Required scope: `contacts:delete`

    Args:
        contact_group_id (str):  Default: 'grp_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        contact_group_id=contact_group_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    contact_group_id: str = "grp_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any]:
    """Delete group

     Delete a contact group.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the compatible contact list endpoints instead.
    > - `DELETE /contact_lists/{contact_list_id}`.


    Required scope: `contacts:delete`

    Args:
        contact_group_id (str):  Default: 'grp_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        contact_group_id=contact_group_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
