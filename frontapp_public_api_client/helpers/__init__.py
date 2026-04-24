"""Ergonomic helper facades for the Frontapp API client.

These classes wrap the generated API with domain-specific methods that reduce
boilerplate for common workflows. Each helper is accessed as an attribute on
``FrontappClient`` (e.g. ``client.conversations.list(...)``).
"""

from frontapp_public_api_client.helpers.base import Base

__all__ = [
    "Base",
]
