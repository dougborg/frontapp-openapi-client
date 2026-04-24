from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_message_template_folder import CreateMessageTemplateFolder
from ...models.message_template_folder_response import MessageTemplateFolderResponse


def _get_kwargs(
    *,
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/message_template_folders",
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
    *,
    client: AuthenticatedClient | Client,
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> Response[MessageTemplateFolderResponse]:
    """Create folder

     Create a new message template folder in the oldest active workspace that the token has access to. If
    you need to specify the workspace, we recommend using the [Create team
    folder](https://dev.frontapp.com/reference/create-team-folder) endpoint instead.

    Required scope: `message_templates:write`

    Args:
        body (CreateMessageTemplateFolder | Unset): A message template folder that is used to
            store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateFolderResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> MessageTemplateFolderResponse | None:
    """Create folder

     Create a new message template folder in the oldest active workspace that the token has access to. If
    you need to specify the workspace, we recommend using the [Create team
    folder](https://dev.frontapp.com/reference/create-team-folder) endpoint instead.

    Required scope: `message_templates:write`

    Args:
        body (CreateMessageTemplateFolder | Unset): A message template folder that is used to
            store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateFolderResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> Response[MessageTemplateFolderResponse]:
    """Create folder

     Create a new message template folder in the oldest active workspace that the token has access to. If
    you need to specify the workspace, we recommend using the [Create team
    folder](https://dev.frontapp.com/reference/create-team-folder) endpoint instead.

    Required scope: `message_templates:write`

    Args:
        body (CreateMessageTemplateFolder | Unset): A message template folder that is used to
            store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateFolderResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateMessageTemplateFolder | Unset = UNSET,
) -> MessageTemplateFolderResponse | None:
    """Create folder

     Create a new message template folder in the oldest active workspace that the token has access to. If
    you need to specify the workspace, we recommend using the [Create team
    folder](https://dev.frontapp.com/reference/create-team-folder) endpoint instead.

    Required scope: `message_templates:write`

    Args:
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
            client=client,
            body=body,
        )
    ).parsed
