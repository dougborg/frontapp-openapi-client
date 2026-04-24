from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_shared_signature import CreateSharedSignature
from ...models.signature_response import SignatureResponse


def _get_kwargs(
    team_id: str = "tim_123",
    *,
    body: CreateSharedSignature | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/teams/{team_id}/signatures".format(
            team_id=quote(str(team_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SignatureResponse | None:
    if response.status_code == 201:
        response_201 = SignatureResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SignatureResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateSharedSignature | Unset = UNSET,
) -> Response[SignatureResponse]:
    """Create team signature

     Create a new signature for the given team (workspace).

    Required scope: `signatures:write`

    Args:
        team_id (str):  Default: 'tim_123'.
        body (CreateSharedSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SignatureResponse]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateSharedSignature | Unset = UNSET,
) -> SignatureResponse | None:
    """Create team signature

     Create a new signature for the given team (workspace).

    Required scope: `signatures:write`

    Args:
        team_id (str):  Default: 'tim_123'.
        body (CreateSharedSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SignatureResponse
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateSharedSignature | Unset = UNSET,
) -> Response[SignatureResponse]:
    """Create team signature

     Create a new signature for the given team (workspace).

    Required scope: `signatures:write`

    Args:
        team_id (str):  Default: 'tim_123'.
        body (CreateSharedSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SignatureResponse]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str = "tim_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateSharedSignature | Unset = UNSET,
) -> SignatureResponse | None:
    """Create team signature

     Create a new signature for the given team (workspace).

    Required scope: `signatures:write`

    Args:
        team_id (str):  Default: 'tim_123'.
        body (CreateSharedSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SignatureResponse
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            body=body,
        )
    ).parsed
