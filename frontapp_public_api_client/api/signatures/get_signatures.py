from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.signature_response import SignatureResponse


def _get_kwargs(
    signature_id: str = "sig_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/signatures/{signature_id}".format(
            signature_id=quote(str(signature_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SignatureResponse | None:
    if response.status_code == 200:
        response_200 = SignatureResponse.from_dict(response.json())

        return response_200

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
    signature_id: str = "sig_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[SignatureResponse]:
    """Get signatures

     Get the given signature.

    Required scope: `signatures:read`

    Args:
        signature_id (str):  Default: 'sig_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SignatureResponse]
    """

    kwargs = _get_kwargs(
        signature_id=signature_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    signature_id: str = "sig_123",
    *,
    client: AuthenticatedClient | Client,
) -> SignatureResponse | None:
    """Get signatures

     Get the given signature.

    Required scope: `signatures:read`

    Args:
        signature_id (str):  Default: 'sig_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SignatureResponse
    """

    return sync_detailed(
        signature_id=signature_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    signature_id: str = "sig_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[SignatureResponse]:
    """Get signatures

     Get the given signature.

    Required scope: `signatures:read`

    Args:
        signature_id (str):  Default: 'sig_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SignatureResponse]
    """

    kwargs = _get_kwargs(
        signature_id=signature_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    signature_id: str = "sig_123",
    *,
    client: AuthenticatedClient | Client,
) -> SignatureResponse | None:
    """Get signatures

     Get the given signature.

    Required scope: `signatures:read`

    Args:
        signature_id (str):  Default: 'sig_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SignatureResponse
    """

    return (
        await asyncio_detailed(
            signature_id=signature_id,
            client=client,
        )
    ).parsed
