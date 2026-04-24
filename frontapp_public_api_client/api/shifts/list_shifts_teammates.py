from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.list_shifts_teammates_response_200 import ListShiftsTeammatesResponse200


def _get_kwargs(
    shift_id: str = "shf_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/shifts/{shift_id}/teammates".format(
            shift_id=quote(str(shift_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListShiftsTeammatesResponse200 | None:
    if response.status_code == 200:
        response_200 = ListShiftsTeammatesResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListShiftsTeammatesResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    shift_id: str = "shf_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListShiftsTeammatesResponse200]:
    """List shift's teammates

     List the teammates assigned to a shift.

    Required scope: `teammates:read`

    Args:
        shift_id (str):  Default: 'shf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListShiftsTeammatesResponse200]
    """

    kwargs = _get_kwargs(
        shift_id=shift_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    shift_id: str = "shf_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListShiftsTeammatesResponse200 | None:
    """List shift's teammates

     List the teammates assigned to a shift.

    Required scope: `teammates:read`

    Args:
        shift_id (str):  Default: 'shf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListShiftsTeammatesResponse200
    """

    return sync_detailed(
        shift_id=shift_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    shift_id: str = "shf_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListShiftsTeammatesResponse200]:
    """List shift's teammates

     List the teammates assigned to a shift.

    Required scope: `teammates:read`

    Args:
        shift_id (str):  Default: 'shf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListShiftsTeammatesResponse200]
    """

    kwargs = _get_kwargs(
        shift_id=shift_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    shift_id: str = "shf_123",
    *,
    client: AuthenticatedClient | Client,
) -> ListShiftsTeammatesResponse200 | None:
    """List shift's teammates

     List the teammates assigned to a shift.

    Required scope: `teammates:read`

    Args:
        shift_id (str):  Default: 'shf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListShiftsTeammatesResponse200
    """

    return (
        await asyncio_detailed(
            shift_id=shift_id,
            client=client,
        )
    ).parsed
