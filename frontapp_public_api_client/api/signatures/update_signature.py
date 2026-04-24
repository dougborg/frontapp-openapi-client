from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.signature_response import SignatureResponse
from ...models.update_signature import UpdateSignature


def _get_kwargs(
    signature_id: str = "sig_123",
    *,
    body: UpdateSignature | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/signatures/{signature_id}".format(
            signature_id=quote(str(signature_id), safe=""),
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
    body: UpdateSignature | Unset = UNSET,
) -> Response[SignatureResponse]:
    """Update signature

     Update signature

    Required scope: `signatures:write`

    Args:
        signature_id (str):  Default: 'sig_123'.
        body (UpdateSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SignatureResponse]
    """

    kwargs = _get_kwargs(
        signature_id=signature_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    signature_id: str = "sig_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateSignature | Unset = UNSET,
) -> SignatureResponse | None:
    """Update signature

     Update signature

    Required scope: `signatures:write`

    Args:
        signature_id (str):  Default: 'sig_123'.
        body (UpdateSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SignatureResponse
    """

    return sync_detailed(
        signature_id=signature_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    signature_id: str = "sig_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateSignature | Unset = UNSET,
) -> Response[SignatureResponse]:
    """Update signature

     Update signature

    Required scope: `signatures:write`

    Args:
        signature_id (str):  Default: 'sig_123'.
        body (UpdateSignature | Unset): A signature that can be used to sign messages.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SignatureResponse]
    """

    kwargs = _get_kwargs(
        signature_id=signature_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    signature_id: str = "sig_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateSignature | Unset = UNSET,
) -> SignatureResponse | None:
    """Update signature

     Update signature

    Required scope: `signatures:write`

    Args:
        signature_id (str):  Default: 'sig_123'.
        body (UpdateSignature | Unset): A signature that can be used to sign messages.


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
            body=body,
        )
    ).parsed
