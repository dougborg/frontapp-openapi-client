from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response


def _get_kwargs(
    teammate_group_id: str = "cir_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/teammate_groups/{teammate_group_id}".format(
            teammate_group_id=quote(str(teammate_group_id), safe=""),
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
    teammate_group_id: str = "cir_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any]:
    """Delete teammate group

     Deletes a teammate group. Note - You cannot delete a teammate group that is managed by SCIM.

    Required scope: `teammate_groups:delete`

    Args:
        teammate_group_id (str):  Default: 'cir_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        teammate_group_id=teammate_group_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    teammate_group_id: str = "cir_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any]:
    """Delete teammate group

     Deletes a teammate group. Note - You cannot delete a teammate group that is managed by SCIM.

    Required scope: `teammate_groups:delete`

    Args:
        teammate_group_id (str):  Default: 'cir_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        teammate_group_id=teammate_group_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
