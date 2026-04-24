"""Data-driven registry mapping accessor names to generated API modules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceConfig:
    """Maps a logical resource to its generated API module functions.

    Attributes:
        module: Directory name under ``api/`` (e.g. ``"orders"``).
        get_one: Module name for single-resource GET, or ``None``.
        get_all: Module name for list GET, or ``None``.
        create: Module name for POST, or ``None``.
        update: Module name for PATCH/PUT, or ``None``.
        delete: Module name for DELETE, or ``None``.
    """

    module: str
    get_one: str | None = None
    get_all: str | None = None
    create: str | None = None
    update: str | None = None
    delete: str | None = None


# Populate this as generic CRUD resources are identified in Front's API.
# Endpoints that don't fit clean CRUD shape (e.g. Front's /conversations/{id}/messages,
# /conversations/{id}/comments, analytics report polling) should be exposed via
# hand-written domain helpers (client.conversations, client.contacts) instead.
RESOURCE_REGISTRY: dict[str, ResourceConfig] = {}
