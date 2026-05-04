"""MCP tools for Frontapp attachment download.

Front's binary-download endpoints (``/download/{attachment_link_id}``,
``/messages/{id}/download/...``, etc.) are stripped from the spec by
``scripts/vendor_spec.py`` because openapi-python-client can't model them.
The client-side ``client.attachments.download`` helper bypasses the
generated API to fetch them; this module exposes that as an MCP tool.

Returning raw binary blobs over MCP would balloon the agent's token budget
(and most LLMs can't do useful work with random bytes anyway), so the tool
writes the bytes to a filesystem path the user explicitly passes and
returns metadata only. Two-step confirm protects against accidental writes
into unintended paths.
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import (
    DESTRUCTIVE,
    confirm_or_preview,
)


def register_tools(mcp: FastMCP) -> None:
    """Register attachment-related tools with the FastMCP server."""

    @mcp.tool(
        name="download_attachment",
        description=(
            "Download a Front attachment by URL and write it to a local "
            "file. The URL is the value Front returns on Attachment.url "
            "(e.g. https://yourCompany.api.frontapp.com/download/fil_abc). "
            "Two-step confirm: confirm=False returns a preview of where "
            "the file will be written; confirm=True performs the download. "
            "Returns the saved path and byte count."
        ),
        annotations=DESTRUCTIVE,
    )
    async def download_attachment(
        context: Context,
        attachment_url: Annotated[
            str,
            Field(
                description=(
                    "Full attachment download URL from Attachment.url, e.g. "
                    "'https://yourCompany.api.frontapp.com/download/fil_abc'"
                )
            ),
        ],
        save_path: Annotated[
            str,
            Field(
                description=(
                    "Absolute filesystem path to write the bytes to. The "
                    "parent directory must already exist; the file will be "
                    "created or overwritten."
                )
            ),
        ],
        confirm: Annotated[
            bool, Field(description="Must be true to perform the download")
        ] = False,
    ) -> dict[str, Any]:
        path = Path(save_path)
        if not path.is_absolute():
            return {
                "error": (
                    f"save_path {save_path!r} must be absolute — pass a full "
                    "filesystem path so the location is unambiguous."
                ),
                "confirmed": False,
            }
        if not path.parent.is_dir():
            reason = (
                "does not exist"
                if not path.parent.exists()
                else "is not a directory (it's a file)"
            )
            return {
                "error": (
                    f"Parent path {str(path.parent)!r} {reason}. "
                    "Choose a save_path inside an existing directory."
                ),
                "confirmed": False,
            }

        preview = {
            "action": "download_attachment",
            "attachment_url": attachment_url,
            "save_path": str(path),
            "parent_exists": True,
            "will_overwrite": path.exists(),
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        services = get_services(context)
        # Stream to disk so we don't buffer large attachments in memory.
        size_bytes = 0
        try:
            with path.open("wb") as fh:
                async for chunk in services.client.attachments.stream(attachment_url):
                    fh.write(chunk)
                    size_bytes += len(chunk)
        except Exception:
            # Don't leave a partial file on the user's disk.
            with contextlib.suppress(OSError):
                path.unlink(missing_ok=True)
            raise

        return {
            "confirmed": True,
            "save_path": str(path),
            "size_bytes": size_bytes,
        }


__all__ = ["register_tools"]
