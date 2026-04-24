from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_message_template_folder import CreateMessageTemplateFolder
from ...models.message_template_folder_response import MessageTemplateFolderResponse


def _get_kwargs(
    teammate_id: str = "tea_123",
    *,
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/teammates/{teammate_id}/message_template_folders".format(
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
) -> MessageTemplateFolderResponse | None:
    if response.status_code == 201:
        response_201 = MessageTemplateFolderResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[MessageTemplateFolderResponse]:
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
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> Response[MessageTemplateFolderResponse]:
    """Create teammate folder

     Create a new message template folder belonging to the requested teammate.

    Required scope: `message_templates:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreateMessageTemplateFolder | Unset): A message template folder that is used to
            store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateFolderResponse]
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
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> MessageTemplateFolderResponse | None:
    """Create teammate folder

     Create a new message template folder belonging to the requested teammate.

    Required scope: `message_templates:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreateMessageTemplateFolder | Unset): A message template folder that is used to
            store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateFolderResponse
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
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> Response[MessageTemplateFolderResponse]:
    """Create teammate folder

     Create a new message template folder belonging to the requested teammate.

    Required scope: `message_templates:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreateMessageTemplateFolder | Unset): A message template folder that is used to
            store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateFolderResponse]
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
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> MessageTemplateFolderResponse | None:
    """Create teammate folder

     Create a new message template folder belonging to the requested teammate.

    Required scope: `message_templates:write`

    Args:
        teammate_id (str):  Default: 'tea_123'.
        body (CreateMessageTemplateFolder | Unset): A message template folder that is used to
            store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateFolderResponse
    """

    return (
        await asyncio_detailed(
            teammate_id=teammate_id,
            client=client,
            body=body,
        )
    ).parsed
