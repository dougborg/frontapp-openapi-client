"""Attachments helper — upload (via multipart bypass) and download.

Front's OpenAPI spec models ``attachments: array<binary>`` on draft / message
/ comment / template request bodies, but the generated openapi-python-client
serializes those endpoints as ``Content-Type: application/json``. That is
incorrect for any request that actually carries binary data — Front expects
``Content-Type: multipart/form-data`` with the file content as form parts.

This module bypasses the generated path for the multipart case and exposes
download support for the five binary-response paths that
``scripts/vendor_spec.py`` strips from the spec (``/download/...``,
``/messages/{id}/download/...``, etc.).

Public surface:

- ``FileSpec`` — a small dataclass describing one upload (filename, bytes,
  mime type). Construct directly or via ``FileSpec.from_path(path)``.
- ``client.attachments.download(url)`` — fetch attachment bytes by the URL
  Front returns on ``Attachment.url``. Uses the same ``FrontappClient``'s
  authenticated httpx session, so transport-layer retries / rate-limit
  awareness still apply. The URL host is validated against the client's
  configured ``base_url`` so the API token is never sent to a third-party
  domain.
- ``client.attachments.stream(url)`` — same as ``download`` but yields
  chunks for large files.
- ``client.attachments.post_multipart(...)`` — low-level multipart sender
  used internally by ``drafts`` and ``conversations`` helpers when the
  caller passes ``attachments=[FileSpec(...)]``. Library callers can use
  it directly to attach files to any Front endpoint that accepts binary
  attachments (10 today: 3 drafts, 1 reply, 2 messages, 2 comments,
  2 message-templates).
- ``preview_paths(paths)`` / ``resolve_paths(paths)`` — module-level helpers
  used by MCP tools to validate filesystem paths before / during upload.
  ``preview_paths`` only stats the file; ``resolve_paths`` reads it.
"""

from __future__ import annotations

import mimetypes
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from frontapp_public_api_client.helpers.base import Base

# Front's per-attachment size limit (25 MB) — enforced server-side; we surface
# it here so callers can fail fast instead of round-tripping a guaranteed 413.
MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024

# Multipart form-field name Front expects for the array of binary attachments.
# Confirmed against Front's published example
# (https://gist.github.com/hdornier/e04d04921032e98271f46ff8a539a4cb): the
# field name is plain ``attachments`` — httpx repeats it once per file, which
# Front parses as an array.
_MULTIPART_FIELD = "attachments"


@dataclass(frozen=True)
class FileSpec:
    """One attachment to upload.

    Attributes:
        filename: Display filename Front will record on the attachment.
        content: File contents as bytes. ``BinaryIO`` is not supported here —
            read the file fully before constructing the FileSpec so the size
            can be validated up-front.
        mime_type: MIME type (e.g. ``"application/pdf"``). Defaults to
            ``"application/octet-stream"`` when omitted.
    """

    filename: str
    content: bytes
    mime_type: str = "application/octet-stream"

    def __post_init__(self) -> None:
        if not self.filename:
            raise ValueError("FileSpec.filename must be non-empty")
        if not isinstance(self.content, bytes | bytearray):
            raise TypeError(
                "FileSpec.content must be bytes (got "
                f"{type(self.content).__name__}); read the file before constructing"
            )
        if len(self.content) > MAX_ATTACHMENT_BYTES:
            raise ValueError(
                f"FileSpec '{self.filename}' is {len(self.content):,} bytes, "
                f"exceeding Front's 25 MB attachment limit"
            )

    @classmethod
    def from_path(cls, path: str | Path, *, mime_type: str | None = None) -> FileSpec:
        """Construct a FileSpec by reading a file from disk.

        Args:
            path: Filesystem path to the file. Must exist and be a regular file.
            mime_type: Override the auto-detected MIME type. When omitted,
                ``mimetypes.guess_type`` infers from the filename extension;
                falls back to ``application/octet-stream`` if no match.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Attachment path does not exist: {p}")
        if not p.is_file():
            raise ValueError(f"Attachment path is not a regular file: {p}")
        resolved_mime = (
            mime_type or mimetypes.guess_type(p.name)[0] or ("application/octet-stream")
        )
        return cls(filename=p.name, content=p.read_bytes(), mime_type=resolved_mime)

    def to_httpx_tuple(self) -> tuple[str, bytes, str]:
        """Render as the (filename, content, mime_type) tuple httpx expects."""
        return (self.filename, bytes(self.content), self.mime_type)


def _validate_path(raw: str | Path) -> Path:
    """Validate a single attachment path: absolute, exists, regular file.

    Raises ValueError (non-absolute), FileNotFoundError (missing), or
    ValueError (not a regular file). Caller decides whether to also enforce
    the size limit (handled separately by ``FileSpec.__post_init__``).
    """
    p = Path(raw)
    if not p.is_absolute():
        raise ValueError(
            f"Attachment path {str(raw)!r} must be absolute (avoid relative "
            "paths to keep tool behavior deterministic across working "
            "directories)"
        )
    if not p.exists():
        raise FileNotFoundError(f"Attachment path does not exist: {p}")
    if not p.is_file():
        raise ValueError(f"Attachment path is not a regular file: {p}")
    return p


def preview_paths(
    paths: list[str | Path] | None,
) -> list[dict[str, Any]]:
    """Stat-only preview of attachment paths — no file bytes are read.

    Returns one preview row per path with ``{path, filename, mime_type,
    size_bytes}``. Validates the path is absolute / exists / is a regular
    file, and that the size is within Front's 25 MB limit. Use this on the
    preview path of an MCP tool (``confirm=False``) so the LLM can show
    the human what would be uploaded without burning the read until
    they actually confirm.
    """
    if not paths:
        return []
    rows: list[dict[str, Any]] = []
    for raw in paths:
        p = _validate_path(raw)
        size = p.stat().st_size
        if size > MAX_ATTACHMENT_BYTES:
            raise ValueError(
                f"Attachment {p.name!r} is {size:,} bytes, exceeding Front's "
                "25 MB limit"
            )
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        rows.append(
            {
                "path": str(p),
                "filename": p.name,
                "mime_type": mime,
                "size_bytes": size,
            }
        )
    return rows


def resolve_paths(
    paths: list[str | Path] | None,
) -> tuple[list[FileSpec], list[dict[str, Any]]]:
    """Resolve filesystem paths to FileSpec instances + a preview list.

    Reads each file's bytes (the multipart upload needs them) and produces
    the same preview rows ``preview_paths`` returns. Validates absolute /
    exists / regular file / ≤25 MB.

    Use this on the execute path (``confirm=True``) of an MCP tool, after
    ``preview_paths`` has already been called for the preview. Library
    callers (e.g. Python scripts) can call directly.

    Raises ``ValueError`` (relative path or oversize), ``FileNotFoundError``
    (missing). MCP tools let these bubble so the LLM gets a clear "this
    path won't work" message instead of a multipart request that 4xx's at
    Front.
    """
    if not paths:
        return [], []
    specs: list[FileSpec] = []
    preview: list[dict[str, Any]] = []
    for raw in paths:
        p = _validate_path(raw)
        spec = FileSpec.from_path(p)
        specs.append(spec)
        preview.append(
            {
                "path": str(p),
                "filename": spec.filename,
                "mime_type": spec.mime_type,
                "size_bytes": len(spec.content),
            }
        )
    return specs, preview


def _raise_for_status(
    status: int,
    body: bytes,
    *,
    operation: str,
) -> None:
    """Raise the correct typed exception for a non-2xx httpx response.

    Mirrors ``utils.unwrap``'s status-based dispatch but operates on raw
    httpx responses (not the generated ``Response[T]`` wrapper), so we can
    use it from the multipart-bypass and download paths that don't go
    through the generated API.
    """
    from frontapp_public_api_client.utils import (
        APIError,
        AuthenticationError,
        RateLimitError,
        ServerError,
        ValidationError,
    )

    if 200 <= status < 300:
        return
    if status == 401:
        raise AuthenticationError(f"Authentication failed: {operation}", status, body)
    if status == 422:
        raise ValidationError(f"Validation failed: {operation}", status, body)
    if status == 429:
        raise RateLimitError(f"Rate limit exceeded: {operation}", status, body)
    if 500 <= status < 600:
        raise ServerError(f"Server error ({status}): {operation}", status, body)
    raise APIError(f"Request failed ({status}): {operation}", status, body)


class Attachments(Base):
    """Ergonomic operations for Frontapp attachments — upload and download."""

    def _check_url_host(self, url: str) -> None:
        """Reject download URLs whose host doesn't match the client's base_url.

        Front populates ``Attachment.url`` with a fully-qualified URL on the
        workspace's own subdomain (``https://<workspace>.api.frontapp.com/
        download/...``) — but the client carries an authenticated bearer
        token in headers, so following an attacker-controlled URL would
        leak the token to a third party. Verify the host before issuing the
        request.

        The match is hostname-only against ``base_url`` (port and scheme
        intentionally not compared — Front uses https on the standard port).
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(
                f"Attachment URL must be http or https, got {parsed.scheme!r}"
            )
        target_host = (parsed.hostname or "").lower()
        base = urlparse(str(self._client._base_url))
        base_host = (base.hostname or "").lower()
        if not target_host:
            raise ValueError(f"Attachment URL has no host: {url!r}")
        # Allow the configured base host directly OR any subdomain of
        # frontapp.com (Front workspace subdomains end with this suffix).
        if target_host != base_host and not target_host.endswith(".frontapp.com"):
            raise ValueError(
                f"Attachment URL host {target_host!r} does not match the "
                f"client's base host ({base_host!r}) or *.frontapp.com — "
                "refusing to send the API token to a foreign domain"
            )

    # -- download ----------------------------------------------------------

    async def download(self, url: str) -> bytes:
        """Download an attachment by URL and return its bytes.

        Use the URL value from ``AttachmentSummary.url`` (Front populates this
        on every attachment that lives inside a message, comment, or draft).
        The request goes through the same authenticated httpx session as
        every other client call, so retries and rate-limit handling apply.

        The URL host is validated against the client's base URL (or the
        ``*.frontapp.com`` subdomain space) so the API token is never sent
        to a third-party domain.

        Args:
            url: Full attachment download URL — typically of the form
                ``https://yourCompany.api.frontapp.com/download/fil_xxx``.

        Returns:
            Raw bytes of the attachment.

        Raises:
            ValueError: If the URL host doesn't match the client's base URL
                or the ``*.frontapp.com`` allowlist.
            APIError: and its subclasses on non-2xx responses; see
                ``utils.unwrap``'s exception hierarchy.
        """
        self._check_url_host(url)
        httpx_client = self._client.get_async_httpx_client()
        response = await httpx_client.get(url)
        _raise_for_status(
            response.status_code, response.content, operation="downloading attachment"
        )
        return response.content

    async def stream(
        self, url: str, *, chunk_size: int = 65536
    ) -> AsyncIterator[bytes]:
        """Stream attachment bytes for large files.

        Yields chunks of ``chunk_size`` bytes (default 64 KiB). Use this in
        place of ``download`` when the attachment is too large to comfortably
        buffer in memory. URL host is validated like ``download``.

        Args:
            url: Same URL as ``download``.
            chunk_size: Bytes per chunk. Default 64 KiB.

        Yields:
            Successive ``bytes`` chunks of the attachment body.

        Raises:
            ValueError: If the URL host doesn't match the client's base URL.
            APIError: and its subclasses on non-2xx responses.
        """
        self._check_url_host(url)
        httpx_client = self._client.get_async_httpx_client()
        async with httpx_client.stream("GET", url) as response:
            _raise_for_status(
                response.status_code, b"", operation="streaming attachment"
            )
            async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                yield chunk

    # -- upload (low-level multipart) -------------------------------------

    async def post_multipart(
        self,
        *,
        method: Literal["POST", "PATCH"],
        path: str,
        fields: dict[str, Any],
        files: list[FileSpec],
    ) -> dict[str, Any] | None:
        """Send a multipart/form-data request to a Front endpoint.

        Bypasses the generated client to send the request body as
        ``multipart/form-data`` rather than the broken ``application/json``
        path the generated code uses for binary-bearing endpoints. The
        authenticated httpx session is shared with the generated API, so all
        transport-layer behaviors (retries, rate-limit awareness, error
        logging) still apply.

        Args:
            method: HTTP method — ``"POST"`` (every create endpoint) or
                ``"PATCH"`` (the edit-draft and edit-template endpoints).
                Anything else means the call is wrong; the type narrows
                to those two.
            path: Path relative to the client's ``base_url``, e.g.
                ``"/conversations/cnv_abc/drafts"``. The base URL is joined
                automatically.
            fields: Non-file form fields. List values become repeated
                form parts (``to[]`` / ``cc[]`` semantics); other values
                are stringified.
            files: List of ``FileSpec`` instances. Each becomes one
                ``attachments`` part in the multipart envelope.

        Returns:
            The parsed JSON response body, or ``None`` for empty/non-JSON
            success responses (204, etc.).

        Raises:
            APIError: and its subclasses (AuthenticationError, ValidationError,
                RateLimitError, ServerError) on non-2xx responses; see
                ``utils.unwrap``'s exception hierarchy.
        """
        data = _flatten_form_fields(fields)
        httpx_files = [
            (_MULTIPART_FIELD, file_spec.to_httpx_tuple()) for file_spec in files
        ]

        httpx_client = self._client.get_async_httpx_client()
        response = await httpx_client.request(
            method=method,
            url=path,
            data=data,
            files=httpx_files,
        )
        _raise_for_status(
            response.status_code, response.content, operation="multipart upload"
        )
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return None


def _flatten_form_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """Render form-field values into shapes httpx can encode.

    httpx's ``data=`` mapping encodes list values as repeated form parts
    (e.g. ``to=a@x&to=b@x``), which is exactly what Front's API expects for
    array-valued form fields. So we keep list values as lists, drop
    ``None`` values, stringify booleans, and pass everything else through
    after a ``str()`` for safety.
    """
    out: dict[str, Any] = {}
    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, list | tuple):
            cleaned = [str(item) for item in value if item is not None]
            if cleaned:
                out[key] = cleaned
        elif isinstance(value, bool):
            out[key] = "true" if value else "false"
        elif isinstance(value, int | float):
            out[key] = str(value)
        else:
            out[key] = str(value)
    return out


__all__ = [
    "MAX_ATTACHMENT_BYTES",
    "Attachments",
    "FileSpec",
    "preview_paths",
    "resolve_paths",
]
