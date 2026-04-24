"""Thin CRUD wrappers over generated Frontapp API modules.

Each resource registered in ``RESOURCE_REGISTRY`` gets a ``Resource``
instance that lazy-loads the matching generated module and exposes
``list``/``get``/``create``/``update``/``delete`` methods returning raw
attrs response models.

The registry is currently empty (populated as verticals ship — see the
issue tracker for upcoming resources). For the conversations vertical,
use the hand-written ergonomic helper ``client.conversations`` instead.

Usage (once a resource is registered)::

    async with FrontappClient() as client:
        # Example: once contacts are registered
        contacts = await client.api.contacts.list()
        contact = await client.api.contacts.get("crd_abc")
"""

from ._namespace import ApiNamespace
from ._registry import RESOURCE_REGISTRY, ResourceConfig
from ._resource import Resource

__all__ = ["RESOURCE_REGISTRY", "ApiNamespace", "Resource", "ResourceConfig"]
