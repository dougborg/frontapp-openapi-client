from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.message_template_response import MessageTemplateResponse
from ...models.update_message_template import UpdateMessageTemplate


def _get_kwargs(
    message_template_id: str = "rsp_123",
    *,
    body: UpdateMessageTemplate | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/message_templates/{message_template_id}".format(
            message_template_id=quote(str(message_template_id), safe=""),
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
    if response.status_code == 200:
        response_200 = MessageTemplateResponse.from_dict(response.json())

        return response_200

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
    message_template_id: str = "rsp_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMessageTemplate | Unset = UNSET,
) -> Response[MessageTemplateResponse]:
    """Update message template

     Update message template

    Required scope: `message_templates:write`

    Args:
        message_template_id (str):  Default: 'rsp_123'.
        body (UpdateMessageTemplate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateResponse]
    """

    kwargs = _get_kwargs(
        message_template_id=message_template_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    message_template_id: str = "rsp_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMessageTemplate | Unset = UNSET,
) -> MessageTemplateResponse | None:
    """Update message template

     Update message template

    Required scope: `message_templates:write`

    Args:
        message_template_id (str):  Default: 'rsp_123'.
        body (UpdateMessageTemplate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateResponse
    """

    return sync_detailed(
        message_template_id=message_template_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    message_template_id: str = "rsp_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMessageTemplate | Unset = UNSET,
) -> Response[MessageTemplateResponse]:
    """Update message template

     Update message template

    Required scope: `message_templates:write`

    Args:
        message_template_id (str):  Default: 'rsp_123'.
        body (UpdateMessageTemplate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateResponse]
    """

    kwargs = _get_kwargs(
        message_template_id=message_template_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    message_template_id: str = "rsp_123",
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMessageTemplate | Unset = UNSET,
) -> MessageTemplateResponse | None:
    """Update message template

     Update message template

    Required scope: `message_templates:write`

    Args:
        message_template_id (str):  Default: 'rsp_123'.
        body (UpdateMessageTemplate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateResponse
    """

    return (
        await asyncio_detailed(
            message_template_id=message_template_id,
            client=client,
            body=body,
        )
    ).parsed
