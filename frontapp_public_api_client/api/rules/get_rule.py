from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.rule_response import RuleResponse


def _get_kwargs(
    rule_id: str = "rul_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/rules/{rule_id}".format(
            rule_id=quote(str(rule_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RuleResponse | None:
    if response.status_code == 200:
        response_200 = RuleResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[RuleResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    rule_id: str = "rul_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[RuleResponse]:
    """Get rule

     Fetch a rule.

    Required scope: `rules:read`

    Args:
        rule_id (str):  Default: 'rul_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[RuleResponse]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    rule_id: str = "rul_123",
    *,
    client: AuthenticatedClient | Client,
) -> RuleResponse | None:
    """Get rule

     Fetch a rule.

    Required scope: `rules:read`

    Args:
        rule_id (str):  Default: 'rul_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        RuleResponse
    """

    return sync_detailed(
        rule_id=rule_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    rule_id: str = "rul_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[RuleResponse]:
    """Get rule

     Fetch a rule.

    Required scope: `rules:read`

    Args:
        rule_id (str):  Default: 'rul_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[RuleResponse]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    rule_id: str = "rul_123",
    *,
    client: AuthenticatedClient | Client,
) -> RuleResponse | None:
    """Get rule

     Fetch a rule.

    Required scope: `rules:read`

    Args:
        rule_id (str):  Default: 'rul_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        RuleResponse
    """

    return (
        await asyncio_detailed(
            rule_id=rule_id,
            client=client,
        )
    ).parsed
