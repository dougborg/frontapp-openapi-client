from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.account_patch import AccountPatch
from ...models.account_response import AccountResponse


def _get_kwargs(
    account_id: str = "acc_123",
    *,
    body: AccountPatch | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/accounts/{account_id}".format(
            account_id=quote(str(account_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountResponse | None:
    if response.status_code == 200:
        response_200 = AccountResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AccountResponse]:
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
    body: AccountPatch | Unset = UNSET,
) -> Response[AccountResponse]:
    """Update account

     Updates an account.

    Required scope: `accounts:write`

    Args:
        account_id (str):  Default: 'acc_123'.
        body (AccountPatch | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AccountResponse]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    account_id: str = "acc_123",
    *,
    client: AuthenticatedClient | Client,
    body: AccountPatch | Unset = UNSET,
) -> AccountResponse | None:
    """Update account

     Updates an account.

    Required scope: `accounts:write`

    Args:
        account_id (str):  Default: 'acc_123'.
        body (AccountPatch | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AccountResponse
    """

    return sync_detailed(
        account_id=account_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    account_id: str = "acc_123",
    *,
    client: AuthenticatedClient | Client,
    body: AccountPatch | Unset = UNSET,
) -> Response[AccountResponse]:
    """Update account

     Updates an account.

    Required scope: `accounts:write`

    Args:
        account_id (str):  Default: 'acc_123'.
        body (AccountPatch | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[AccountResponse]
    """

    kwargs = _get_kwargs(
        account_id=account_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    account_id: str = "acc_123",
    *,
    client: AuthenticatedClient | Client,
    body: AccountPatch | Unset = UNSET,
) -> AccountResponse | None:
    """Update account

     Updates an account.

    Required scope: `accounts:write`

    Args:
        account_id (str):  Default: 'acc_123'.
        body (AccountPatch | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        AccountResponse
    """

    return (
        await asyncio_detailed(
            account_id=account_id,
            client=client,
            body=body,
        )
    ).parsed
