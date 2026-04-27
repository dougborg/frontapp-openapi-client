"""Ergonomic helper facades for the Frontapp API client.

These classes wrap the generated API with domain-specific methods that reduce
boilerplate for common workflows. Each helper is accessed as an attribute on
``FrontappClient`` (e.g. ``client.conversations.list(...)``).
"""

from frontapp_public_api_client.helpers.attachments import (
    MAX_ATTACHMENT_BYTES,
    Attachments,
    FileSpec,
)
from frontapp_public_api_client.helpers.base import Base
from frontapp_public_api_client.helpers.contact_groups import ContactGroups
from frontapp_public_api_client.helpers.contact_lists import ContactLists
from frontapp_public_api_client.helpers.contacts import Contacts
from frontapp_public_api_client.helpers.conversations import Conversations
from frontapp_public_api_client.helpers.drafts import Drafts
from frontapp_public_api_client.helpers.inboxes import Inboxes
from frontapp_public_api_client.helpers.messages import Messages
from frontapp_public_api_client.helpers.tags import Tags
from frontapp_public_api_client.helpers.teammates import Teammates

__all__ = [
    "MAX_ATTACHMENT_BYTES",
    "Attachments",
    "Base",
    "ContactGroups",
    "ContactLists",
    "Contacts",
    "Conversations",
    "Drafts",
    "FileSpec",
    "Inboxes",
    "Messages",
    "Tags",
    "Teammates",
]
