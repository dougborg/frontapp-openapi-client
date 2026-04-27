"""Shared constants used by the contact_lists / contact_groups helpers.

These were duplicated across both helpers and both MCP tool modules until
PR #70's review surfaced the drift risk. Centralizing here keeps the
50-contact cap and its error message in one place — change it once if
Front ever lifts the limit.
"""

from __future__ import annotations

# Front's server-side cap on the bulk-remove endpoint for contact lists
# AND the deprecated contact groups (both share the same
# ``RemoveContactsFromList`` request body model with ``maxItems: 50``).
CONTACT_BUCKET_REMOVE_CAP = 50

CONTACT_BUCKET_REMOVE_OVER_CAP_MSG = (
    "contact_ids has {count} entries; Front caps remove_contacts at "
    f"{CONTACT_BUCKET_REMOVE_CAP} per call. Batch the removals manually."
)


__all__ = [
    "CONTACT_BUCKET_REMOVE_CAP",
    "CONTACT_BUCKET_REMOVE_OVER_CAP_MSG",
]
