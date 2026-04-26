"""Ergonomic helper facades for the Frontapp API client.

These classes wrap the generated API with domain-specific methods that reduce
boilerplate for common workflows. Each helper is accessed as an attribute on
``FrontappClient`` (e.g. ``client.conversations.list(...)``).
"""

from frontapp_public_api_client.helpers.base import Base
from frontapp_public_api_client.helpers.contacts import Contacts
from frontapp_public_api_client.helpers.conversations import Conversations
from frontapp_public_api_client.helpers.drafts import Drafts
from frontapp_public_api_client.helpers.inboxes import Inboxes
from frontapp_public_api_client.helpers.messages import Messages
from frontapp_public_api_client.helpers.tags import Tags

__all__ = [
    "Base",
    "Contacts",
    "Conversations",
    "Drafts",
    "Inboxes",
    "Messages",
    "Tags",
]
