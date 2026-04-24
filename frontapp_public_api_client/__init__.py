"""Frontapp Public API Client — Python client for the Frontapp API."""

from .client import AuthenticatedClient, Client
from .frontapp_client import FrontappClient
from .utils import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ServerError,
    ValidationError,
    get_error_message,
    handle_response,
    is_error,
    is_success,
    unwrap,
    unwrap_as,
    unwrap_data,
)

__all__ = [
    "APIError",
    "AuthenticatedClient",
    "AuthenticationError",
    "Client",
    "FrontappClient",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    "get_error_message",
    "handle_response",
    "is_error",
    "is_success",
    "unwrap",
    "unwrap_as",
    "unwrap_data",
]
