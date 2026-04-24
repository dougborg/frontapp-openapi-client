from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_private_message_template import CreatePrivateMessageTemplate
from ...models.message_template_response import MessageTemplateResponse


def _get_kwargs(
    teammate_id: str = "tea_123",
    *,
    body: CreatePrivateMessageTemplate | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/teammates/{teammate_id}/message_templates".format(
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
) -> MessageTemplateResponse | None:
    if response.status_code == 201:
        response_201 = MessageTemplateResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[MessageTemplateResponse]:
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
    body: CreatePrivateMessageTemplate | Unset = UNSET,
) -> Response[MessageTemplateResponse]:
    """Create teammate message template

     Create a new message template for the given teammate

    Required scope: `message_templates:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreatePrivateMessageTemplate | Unset): A message template that is used for pre-
            written responses

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateResponse]
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
    body: CreatePrivateMessageTemplate | Unset = UNSET,
) -> MessageTemplateResponse | None:
    """Create teammate message template

     Create a new message template for the given teammate

    Required scope: `message_templates:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreatePrivateMessageTemplate | Unset): A message template that is used for pre-
            written responses

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateResponse
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
    body: CreatePrivateMessageTemplate | Unset = UNSET,
) -> Response[MessageTemplateResponse]:
    """Create teammate message template

     Create a new message template for the given teammate

    Required scope: `message_templates:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreatePrivateMessageTemplate | Unset): A message template that is used for pre-
            written responses

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateResponse]
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
    body: CreatePrivateMessageTemplate | Unset = UNSET,
) -> MessageTemplateResponse | None:
    """Create teammate message template

     Create a new message template for the given teammate

    Required scope: `message_templates:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreatePrivateMessageTemplate | Unset): A message template that is used for pre-
            written responses

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateResponse
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
            body=body,
        )
    ).parsed
