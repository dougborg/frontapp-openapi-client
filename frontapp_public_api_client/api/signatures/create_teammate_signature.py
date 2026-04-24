from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_private_signature import CreatePrivateSignature
from ...models.signature_response import SignatureResponse


def _get_kwargs(
    teammate_id: str = "tea_123",
    *,
    body: CreatePrivateSignature | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/teammates/{teammate_id}/signatures".format(
            teammate_id=quote(str(teammate_id), safe=""),
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
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreatePrivateSignature | Unset = UNSET,
) -> Response[SignatureResponse]:
    """Create teammate signature

     Create a new signature for the given teammate

    Required scope: `signatures:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreatePrivateSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SignatureResponse]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreatePrivateSignature | Unset = UNSET,
) -> SignatureResponse | None:
    """Create teammate signature

     Create a new signature for the given teammate

    Required scope: `signatures:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreatePrivateSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SignatureResponse
    """

    return sync_detailed(
        teammate_id=teammate_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreatePrivateSignature | Unset = UNSET,
) -> Response[SignatureResponse]:
    """Create teammate signature

     Create a new signature for the given teammate

    Required scope: `signatures:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreatePrivateSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SignatureResponse]
    """

    kwargs = _get_kwargs(
        teammate_id=teammate_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    teammate_id: str = "tea_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreatePrivateSignature | Unset = UNSET,
) -> SignatureResponse | None:
    """Create teammate signature

     Create a new signature for the given teammate

    Required scope: `signatures:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreatePrivateSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SignatureResponse
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
            body=body,
        )
    ).parsed
