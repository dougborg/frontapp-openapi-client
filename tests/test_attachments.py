"""Tests for the attachments vertical: FileSpec + Attachments helper.

Covers:
- FileSpec validation and from_path construction
- client.attachments.download single-shot
- client.attachments.stream chunked
- client.attachments.post_multipart wire shape
- drafts/conversations multipart upload integration
- Error mapping for 401/422/429/5xx on both download and upload paths
"""

from __future__ import annotations

import email.policy
import mimetypes
from email.parser import BytesParser
from pathlib import Path

import httpx
import pytest

from frontapp_public_api_client import FileSpec, FrontappClient
from frontapp_public_api_client.helpers.attachments import (
    MAX_ATTACHMENT_BYTES,
    _flatten_form_fields,
    preview_paths,
    resolve_paths,
)
from frontapp_public_api_client.utils import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ServerError,
    ValidationError,
)

# ---------------------------------------------------------------------------
# FileSpec
# ---------------------------------------------------------------------------


class TestFileSpec:
    def test_construct_from_bytes(self):
        spec = FileSpec(
            filename="doc.pdf", content=b"%PDF-1.4 hello", mime_type="application/pdf"
        )
        assert spec.filename == "doc.pdf"
        assert spec.mime_type == "application/pdf"
        assert spec.content == b"%PDF-1.4 hello"

    def test_default_mime_type(self):
        spec = FileSpec(filename="x.bin", content=b"\x00\x01")
        assert spec.mime_type == "application/octet-stream"

    def test_empty_filename_rejected(self):
        with pytest.raises(ValueError, match="filename must be non-empty"):
            FileSpec(filename="", content=b"x")

    def test_non_bytes_content_rejected(self):
        with pytest.raises(TypeError, match="must be bytes"):
            FileSpec(filename="x", content="not bytes")  # type: ignore[arg-type]

    def test_oversize_content_rejected(self):
        too_big = b"x" * (MAX_ATTACHMENT_BYTES + 1)
        with pytest.raises(ValueError, match="exceeding Front's 25 MB"):
            FileSpec(filename="big.bin", content=too_big)

    def test_to_httpx_tuple(self):
        spec = FileSpec(filename="a.txt", content=b"hello", mime_type="text/plain")
        assert spec.to_httpx_tuple() == ("a.txt", b"hello", "text/plain")

    def test_from_path_reads_file_and_infers_mime(self, tmp_path: Path):
        f = tmp_path / "report.pdf"
        f.write_bytes(b"%PDF-1.4 fake-pdf-bytes")
        spec = FileSpec.from_path(f)
        assert spec.filename == "report.pdf"
        # mimetypes registers application/pdf for .pdf cross-platform
        assert spec.mime_type == (
            mimetypes.guess_type("report.pdf")[0] or "application/octet-stream"
        )
        assert spec.content == b"%PDF-1.4 fake-pdf-bytes"

    def test_from_path_mime_override(self, tmp_path: Path):
        f = tmp_path / "x.bin"
        f.write_bytes(b"x")
        spec = FileSpec.from_path(f, mime_type="application/x-custom")
        assert spec.mime_type == "application/x-custom"

    def test_from_path_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            FileSpec.from_path(tmp_path / "nope.txt")

    def test_from_path_directory_rejected(self, tmp_path: Path):
        with pytest.raises(ValueError, match="not a regular file"):
            FileSpec.from_path(tmp_path)


# ---------------------------------------------------------------------------
# _flatten_form_fields
# ---------------------------------------------------------------------------


class TestFlattenFormFields:
    def test_drops_none_values(self):
        out = _flatten_form_fields({"a": "x", "b": None, "c": 0})
        assert out == {"a": "x", "c": "0"}

    def test_lists_passed_through_for_repeated_form_fields(self):
        out = _flatten_form_fields({"to": ["a@x", "b@x"]})
        assert out == {"to": ["a@x", "b@x"]}

    def test_drops_empty_lists(self):
        out = _flatten_form_fields({"to": [], "body": "hi"})
        assert out == {"body": "hi"}

    def test_booleans_lowercased(self):
        out = _flatten_form_fields({"flag": True, "off": False})
        assert out == {"flag": "true", "off": "false"}


# ---------------------------------------------------------------------------
# Attachments.download (single-shot)
# ---------------------------------------------------------------------------


class TestDownload:
    async def test_returns_response_bytes(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(200, content=b"\x89PNG\r\n\x1a\n binary-blob")

        client = attach_transport(httpx.MockTransport(handler))
        url = "https://api.frontapp.test/download/fil_abc"
        body = await client.attachments.download(url)
        assert body == b"\x89PNG\r\n\x1a\n binary-blob"
        # Authentication header should have been added by AuthenticatedClient.
        assert len(recorded) == 1
        assert recorded[0].url.path == "/download/fil_abc"

    async def test_raises_auth_error_on_401(self, attach_transport):
        def handler(_request):
            return httpx.Response(401, content=b'{"message": "no"}')

        client = attach_transport(httpx.MockTransport(handler))
        with pytest.raises(AuthenticationError):
            await client.attachments.download(
                "https://api.frontapp.test/download/fil_x"
            )

    async def test_raises_validation_on_422(self, attach_transport):
        def handler(_request):
            return httpx.Response(422, content=b"")

        client = attach_transport(httpx.MockTransport(handler))
        with pytest.raises(ValidationError):
            await client.attachments.download(
                "https://api.frontapp.test/download/fil_x"
            )

    async def test_raises_rate_limit_on_429(self, attach_transport):
        def handler(_request):
            return httpx.Response(429, content=b"")

        client = attach_transport(httpx.MockTransport(handler))
        with pytest.raises(RateLimitError):
            await client.attachments.download(
                "https://api.frontapp.test/download/fil_x"
            )

    async def test_raises_server_error_on_500(self, attach_transport):
        def handler(_request):
            return httpx.Response(503, content=b"")

        client = attach_transport(httpx.MockTransport(handler))
        with pytest.raises(ServerError):
            await client.attachments.download(
                "https://api.frontapp.test/download/fil_x"
            )

    async def test_raises_api_error_on_unexpected(self, attach_transport):
        def handler(_request):
            return httpx.Response(404, content=b"")

        client = attach_transport(httpx.MockTransport(handler))
        with pytest.raises(APIError):
            await client.attachments.download(
                "https://api.frontapp.test/download/fil_x"
            )


# ---------------------------------------------------------------------------
# Attachments.stream
# ---------------------------------------------------------------------------


class TestStream:
    async def test_yields_chunks(self, attach_transport):
        body = b"x" * 200_000  # 200 KB

        def handler(_request):
            return httpx.Response(200, content=body)

        client = attach_transport(httpx.MockTransport(handler))
        chunks = []
        async for chunk in client.attachments.stream(
            "https://api.frontapp.test/download/fil_big", chunk_size=4096
        ):
            chunks.append(chunk)
        assert b"".join(chunks) == body

    async def test_stream_raises_auth_error(self, attach_transport):
        def handler(_request):
            return httpx.Response(401)

        client = attach_transport(httpx.MockTransport(handler))
        with pytest.raises(AuthenticationError):
            async for _ in client.attachments.stream(
                "https://api.frontapp.test/download/fil_x"
            ):
                pass


# ---------------------------------------------------------------------------
# Attachments.post_multipart
# ---------------------------------------------------------------------------


class TestPostMultipart:
    async def test_sends_multipart_with_file_and_fields(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(200, json={"id": "msg_xyz"})

        client = attach_transport(httpx.MockTransport(handler))
        result = await client.attachments.post_multipart(
            method="POST",
            path="/conversations/cnv_abc/drafts",
            fields={"body": "Hello", "to": ["a@example.com", "b@example.com"]},
            files=[
                FileSpec(
                    filename="r.pdf", content=b"%PDF-1.4 x", mime_type="application/pdf"
                )
            ],
        )
        assert result == {"id": "msg_xyz"}

        req = recorded[0]
        assert req.method == "POST"
        assert req.url.path == "/conversations/cnv_abc/drafts"
        # Content-Type should be multipart with a boundary
        ct = req.headers.get("content-type", "")
        assert ct.startswith("multipart/form-data; boundary=")

        # Parse the multipart envelope; verify body/to/attachments parts present.
        parsed = BytesParser(policy=email.policy.default).parsebytes(
            b"Content-Type: " + ct.encode() + b"\r\n\r\n" + req.content
        )
        assert parsed.is_multipart()
        parts_by_name: dict[str, list[bytes]] = {}
        filenames: list[str] = []
        for part in parsed.iter_parts():
            disp = str(part.get("Content-Disposition", ""))
            name = ""
            for raw_piece in disp.split(";"):
                piece = raw_piece.strip()
                if piece.startswith("name="):
                    name = piece[len("name=") :].strip('"')
                elif piece.startswith("filename="):
                    filenames.append(piece[len("filename=") :].strip('"'))
            payload = part.get_payload(decode=True) or b""
            assert isinstance(payload, bytes)
            parts_by_name.setdefault(name, []).append(payload)

        assert parts_by_name.get("body") == [b"Hello"]
        assert parts_by_name.get("to") == [b"a@example.com", b"b@example.com"]
        assert parts_by_name.get("attachments") == [b"%PDF-1.4 x"]
        assert "r.pdf" in filenames

    async def test_returns_none_for_204(self, attach_transport):
        def handler(_request):
            return httpx.Response(204, content=b"")

        client = attach_transport(httpx.MockTransport(handler))
        result = await client.attachments.post_multipart(
            method="POST",
            path="/x",
            fields={"body": "hi"},
            files=[FileSpec(filename="a.txt", content=b"x")],
        )
        assert result is None

    async def test_raises_validation_error_on_422(self, attach_transport):
        def handler(_request):
            return httpx.Response(422, content=b'{"message": "bad"}')

        client = attach_transport(httpx.MockTransport(handler))
        with pytest.raises(ValidationError):
            await client.attachments.post_multipart(
                method="POST",
                path="/x",
                fields={},
                files=[FileSpec(filename="a", content=b"x")],
            )


# ---------------------------------------------------------------------------
# Helper integration: drafts + conversations
# ---------------------------------------------------------------------------


class TestDraftsWithAttachments:
    async def test_create_on_channel_uses_multipart_when_attachments(
        self, attach_transport
    ):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(
                200,
                json={
                    "id": "msg_new",
                    "type": "email",
                    "is_inbound": False,
                    "subject": "Hi",
                },
            )

        client = attach_transport(httpx.MockTransport(handler))
        draft = await client.drafts.create_on_channel(
            "cha_abc",
            body="<p>hi</p>",
            subject="Hi",
            attachments=[FileSpec(filename="a.txt", content=b"x")],
        )
        assert draft.id == "msg_new"
        assert recorded[0].method == "POST"
        assert recorded[0].url.path == "/channels/cha_abc/drafts"
        assert recorded[0].headers["content-type"].startswith("multipart/form-data")

    async def test_create_on_channel_uses_json_when_no_attachments(
        self, attach_transport
    ):
        """Confirms the no-attachment path still uses the generated JSON code."""
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(
                200,
                json={"id": "msg_json", "type": "email", "is_inbound": False},
            )

        client = attach_transport(httpx.MockTransport(handler))
        draft = await client.drafts.create_on_channel("cha_abc", body="<p>hi</p>")
        assert draft.id == "msg_json"
        assert recorded[0].headers["content-type"] == "application/json"

    async def test_create_reply_with_attachments(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(200, json={"id": "msg_r", "type": "email"})

        client = attach_transport(httpx.MockTransport(handler))
        draft = await client.drafts.create_reply(
            "cnv_abc",
            body="re: hello",
            channel_id="cha_xyz",
            attachments=[FileSpec(filename="r.pdf", content=b"%PDF")],
        )
        assert draft.id == "msg_r"
        assert recorded[0].url.path == "/conversations/cnv_abc/drafts"
        assert recorded[0].headers["content-type"].startswith("multipart/form-data")

    async def test_edit_with_attachments_uses_patch(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(200, json={"id": "msg_e", "type": "email"})

        client = attach_transport(httpx.MockTransport(handler))
        draft = await client.drafts.edit(
            "msg_e",
            body="updated",
            channel_id="cha_xyz",
            attachments=[FileSpec(filename="r.pdf", content=b"%PDF")],
        )
        assert draft.id == "msg_e"
        assert recorded[0].method == "PATCH"
        assert recorded[0].url.path == "/drafts/msg_e/"


class TestConversationsWithAttachments:
    async def test_reply_with_attachments(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            # 202 Accepted is what Front returns on reply
            return httpx.Response(202, content=b"")

        client = attach_transport(httpx.MockTransport(handler))
        result = await client.conversations.reply(
            "cnv_abc",
            body="thanks",
            attachments=[FileSpec(filename="x.txt", content=b"x")],
        )
        # post_multipart returns None for empty 2xx bodies
        assert result is None
        assert recorded[0].method == "POST"
        assert recorded[0].url.path == "/conversations/cnv_abc/messages"
        assert recorded[0].headers["content-type"].startswith("multipart/form-data")

    async def test_add_comment_with_attachments(self, attach_transport):
        recorded: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            recorded.append(request)
            return httpx.Response(201, json={"id": "com_abc", "body": "internal"})

        client = attach_transport(httpx.MockTransport(handler))
        result = await client.conversations.add_comment(
            "cnv_abc",
            body="internal",
            author_id="tea_1",
            attachments=[FileSpec(filename="x.txt", content=b"x")],
        )
        assert isinstance(result, dict)
        assert result["id"] == "com_abc"
        assert recorded[0].url.path == "/conversations/cnv_abc/comments"


# ---------------------------------------------------------------------------
# Lazy property
# ---------------------------------------------------------------------------


def test_attachments_property_lazy_caches(mock_api_credentials):
    client = FrontappClient(**mock_api_credentials)
    first = client.attachments
    second = client.attachments
    assert first is second


# ---------------------------------------------------------------------------
# preview_paths vs resolve_paths
# ---------------------------------------------------------------------------


class TestPreviewPaths:
    def test_returns_metadata_without_reading_bytes(self, tmp_path: Path):
        f = tmp_path / "doc.txt"
        f.write_bytes(b"hello world" * 100)
        rows = preview_paths([str(f)])
        assert len(rows) == 1
        row = rows[0]
        assert row["filename"] == "doc.txt"
        assert row["size_bytes"] == len(b"hello world" * 100)
        assert "text" in row["mime_type"]

    def test_relative_path_rejected(self):
        with pytest.raises(ValueError, match="must be absolute"):
            preview_paths(["doc.txt"])

    def test_oversize_rejected_via_stat(self, tmp_path: Path, monkeypatch):
        # Don't actually allocate 25 MB+ on disk just to exercise the gate —
        # patch the size cap down to a small value and write a small file
        # that exceeds it. Tests the same code path (Path.stat().st_size
        # vs MAX_ATTACHMENT_BYTES check inside preview_paths).
        from frontapp_public_api_client.helpers import attachments as attachments_mod

        monkeypatch.setattr(attachments_mod, "MAX_ATTACHMENT_BYTES", 100)
        f = tmp_path / "tiny-but-over.bin"
        f.write_bytes(b"x" * 200)  # 200 bytes > new 100-byte cap

        with pytest.raises(ValueError, match="exceeding Front's 25 MB"):
            preview_paths([str(f)])

    def test_empty_input_returns_empty(self):
        assert preview_paths(None) == []
        assert preview_paths([]) == []


class TestResolvePaths:
    def test_returns_specs_and_preview(self, tmp_path: Path):
        f = tmp_path / "x.bin"
        f.write_bytes(b"abc")
        specs, preview = resolve_paths([str(f)])
        assert len(specs) == 1
        assert specs[0].content == b"abc"
        assert preview[0]["size_bytes"] == 3

    def test_empty_input_returns_empty(self):
        specs, preview = resolve_paths(None)
        assert specs == [] and preview == []


# ---------------------------------------------------------------------------
# URL host validation on download / stream
# ---------------------------------------------------------------------------


class TestDownloadHostValidation:
    async def test_foreign_host_rejected(self, attach_transport):
        client = attach_transport(httpx.MockTransport(lambda _: httpx.Response(200)))
        with pytest.raises(ValueError, match="does not match"):
            await client.attachments.download("https://evil.example.com/download/x")

    async def test_frontapp_subdomain_allowed(self, attach_transport):
        # *.frontapp.com is allowlisted even when base_url is api.frontapp.test
        captured = []

        def handler(request):
            captured.append(request)
            return httpx.Response(200, content=b"ok")

        client = attach_transport(httpx.MockTransport(handler))
        body = await client.attachments.download(
            "https://acme.api.frontapp.com/download/fil_x"
        )
        assert body == b"ok"

    async def test_base_host_allowed(self, attach_transport):
        # The mock_api_credentials base_url is api.frontapp.test
        client = attach_transport(
            httpx.MockTransport(lambda _: httpx.Response(200, content=b"ok"))
        )
        body = await client.attachments.download(
            "https://api.frontapp.test/download/fil_x"
        )
        assert body == b"ok"

    async def test_non_http_scheme_rejected(self, attach_transport):
        client = attach_transport(
            httpx.MockTransport(lambda _: httpx.Response(200, content=b"ok"))
        )
        with pytest.raises(ValueError, match="must be http or https"):
            await client.attachments.download("file:///etc/passwd")

    async def test_stream_also_validates(self, attach_transport):
        client = attach_transport(httpx.MockTransport(lambda _: httpx.Response(200)))
        with pytest.raises(ValueError, match="does not match"):
            async for _ in client.attachments.stream(
                "https://evil.example.com/download/x"
            ):
                pass
