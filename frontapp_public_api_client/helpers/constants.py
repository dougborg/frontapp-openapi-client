"""Shared constants and small validators for the helper layer.

These are extracted to a single module so a Front-side cap change (or a
new server-imposed maxItems anywhere in the spec) lands in one place
instead of drifting across helpers and MCP tools.
"""

from __future__ import annotations

from typing import Any

# Front's server-side cap on the bulk-remove endpoint for contact lists
# AND the deprecated contact groups (both share the same
# ``RemoveContactsFromList`` request body model with ``maxItems: 50``).
CONTACT_BUCKET_REMOVE_CAP = 50


def cap_error_message(*, count: int, cap: int, operation: str) -> str:
    """Build the standard 'over the cap' error message.

    Used by both the helper-layer ``ValueError`` and the MCP-tool error
    dict, so the wording stays consistent if Front ever adjusts a cap.
    """
    return (
        f"Got {count} entries; Front caps {operation} at {cap} per call. "
        "Batch the call manually."
    )


def check_list_size_cap(items: list[Any], *, cap: int, operation: str) -> None:
    """Raise ValueError if ``items`` exceeds Front's server-side ``cap``.

    Helper-layer convenience for failing fast before the HTTP call when a
    bulk-mutation endpoint has a documented per-request cap. MCP tools
    cannot use this directly because they need to return a structured
    error dict instead of raising — they construct the same message via
    ``cap_error_message`` so the wording stays in sync.
    """
    if len(items) > cap:
        raise ValueError(
            cap_error_message(count=len(items), cap=cap, operation=operation)
        )


__all__ = [
    "CONTACT_BUCKET_REMOVE_CAP",
    "cap_error_message",
    "check_list_size_cap",
]
