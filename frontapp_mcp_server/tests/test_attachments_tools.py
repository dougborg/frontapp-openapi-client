"""Tests for MCP attachment tools — download path-safety and confirm flow,
plus attachment-path plumbing through draft tools.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from frontapp_mcp.tools.attachments import register_tools as register_attachments
from frontapp_mcp.tools.drafts import register_tools as register_drafts

from frontapp_public_api_client import FileSpec
from frontapp_public_api_client.domain import Draft

from .conftest import create_mock_context


@pytest.fixture
def attachments_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_attachments)


@pytest.fixture
def drafts_tools(mcp_tool_capture) -> dict[str, object]:
    return mcp_tool_capture(register_drafts)


# ---------------------------------------------------------------------------
# download_attachment
# ---------------------------------------------------------------------------


class TestDownloadAttachment:
    async def test_relative_save_path_rejected(self, attachments_tools):
        context, _ = create_mock_context()

        result = await attachments_tools["download_attachment"](
            context,
            attachment_url="https://api.frontapp.test/download/fil_x",
            save_path="relative.bin",
        )
        assert result["confirmed"] is False
        assert "must be absolute" in result["error"]

    async def test_missing_parent_directory_rejected(
        self, attachments_tools, tmp_path: Path
    ):
        context, _ = create_mock_context()
        bogus = tmp_path / "does" / "not" / "exist" / "f.bin"

        result = await attachments_tools["download_attachment"](
            context,
            attachment_url="https://api.frontapp.test/download/fil_x",
            save_path=str(bogus),
        )
        assert result["confirmed"] is False
        assert "Parent path" in result["error"]
        assert "does not exist" in result["error"]

    async def test_preview_path(self, attachments_tools, tmp_path: Path):
        context, lifespan = create_mock_context()
        # Crash if any client method is called during preview.
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )

        target = tmp_path / "out.bin"
        result = await attachments_tools["download_attachment"](
            context,
            attachment_url="https://api.frontapp.test/download/fil_x",
            save_path=str(target),
            confirm=False,
        )
        assert result == {
            "preview": {
                "action": "download_attachment",
                "attachment_url": "https://api.frontapp.test/download/fil_x",
                "save_path": str(target),
                "parent_exists": True,
                "will_overwrite": False,
            },
            "confirmed": False,
        }
        context.elicit.assert_not_called()

    async def test_will_overwrite_flag_when_target_exists(
        self, attachments_tools, tmp_path: Path
    ):
        context, _ = create_mock_context()
        target = tmp_path / "exists.bin"
        target.write_bytes(b"old")

        result = await attachments_tools["download_attachment"](
            context,
            attachment_url="https://api.frontapp.test/download/fil_x",
            save_path=str(target),
            confirm=False,
        )
        assert result["preview"]["will_overwrite"] is True

    async def test_writes_bytes_when_confirmed(self, attachments_tools, tmp_path: Path):
        context, lifespan = create_mock_context(elicit_confirm=True)

        async def fake_stream(_url, *, chunk_size=65536):
            yield b"chunk-1-"
            yield b"chunk-2"

        lifespan.client = AsyncMock()
        lifespan.client.attachments.stream = fake_stream

        target = tmp_path / "saved.bin"
        result = await attachments_tools["download_attachment"](
            context,
            attachment_url="https://api.frontapp.test/download/fil_x",
            save_path=str(target),
            confirm=True,
        )
        assert result == {
            "confirmed": True,
            "save_path": str(target),
            "size_bytes": len(b"chunk-1-chunk-2"),
        }
        assert target.read_bytes() == b"chunk-1-chunk-2"
        context.elicit.assert_called_once()

    async def test_declined_elicitation_does_not_write(
        self, attachments_tools, tmp_path: Path
    ):
        context, lifespan = create_mock_context(
            elicit_confirm=False, elicit_action="accept"
        )
        # If stream is invoked, the test should fail.
        lifespan.client = AsyncMock()
        lifespan.client.attachments.stream = AsyncMock(
            side_effect=AssertionError("stream invoked on declined elicitation")
        )

        target = tmp_path / "saved.bin"
        result = await attachments_tools["download_attachment"](
            context,
            attachment_url="https://api.frontapp.test/download/fil_x",
            save_path=str(target),
            confirm=True,
        )
        assert result["confirmed"] is False
        assert result["result"] == "declined"
        assert not target.exists()

    async def test_partial_write_cleaned_up_on_error(
        self, attachments_tools, tmp_path: Path
    ):
        context, lifespan = create_mock_context(elicit_confirm=True)

        async def fake_stream(_url, *, chunk_size=65536):
            yield b"first chunk"
            raise RuntimeError("network blew up")

        lifespan.client = AsyncMock()
        lifespan.client.attachments.stream = fake_stream

        target = tmp_path / "saved.bin"
        with pytest.raises(RuntimeError, match="network blew up"):
            await attachments_tools["download_attachment"](
                context,
                attachment_url="https://api.frontapp.test/download/fil_x",
                save_path=str(target),
                confirm=True,
            )
        # Partial file should have been cleaned up.
        assert not target.exists()


# ---------------------------------------------------------------------------
# attachment_paths plumbing through draft tools
# ---------------------------------------------------------------------------


class TestDraftAttachmentPaths:
    async def test_create_draft_on_channel_resolves_paths(
        self, drafts_tools, tmp_path: Path
    ):
        context, lifespan = create_mock_context(elicit_confirm=True)
        f1 = tmp_path / "doc.pdf"
        f1.write_bytes(b"%PDF-fake")
        f2 = tmp_path / "image.png"
        f2.write_bytes(b"\x89PNG fake")

        returned_draft = Draft.model_validate(
            {"id": "msg_new", "subject": "Hi", "draft_mode": "shared"}
        )
        lifespan.client = AsyncMock()
        lifespan.client.drafts.create_on_channel = AsyncMock(
            return_value=returned_draft
        )

        result = await drafts_tools["create_draft_on_channel"](
            context,
            channel_id="cha_abc",
            body="hi",
            subject="Hi",
            attachment_paths=[str(f1), str(f2)],
            confirm=True,
        )

        assert result["confirmed"] is True
        # Helper called with FileSpec list
        call = lifespan.client.drafts.create_on_channel.await_args
        assert call is not None
        attachments = call.kwargs["attachments"]
        assert len(attachments) == 2
        assert all(isinstance(a, FileSpec) for a in attachments)
        assert attachments[0].filename == "doc.pdf"
        assert attachments[1].filename == "image.png"

    async def test_preview_includes_attachment_metadata(
        self, drafts_tools, tmp_path: Path
    ):
        context, lifespan = create_mock_context()
        # Crash if helper called on preview
        lifespan.client = AsyncMock(
            side_effect=AssertionError("client invoked on preview path")
        )
        f = tmp_path / "report.txt"
        f.write_bytes(b"abc")

        result = await drafts_tools["create_draft_on_channel"](
            context,
            channel_id="cha_abc",
            body="hi",
            attachment_paths=[str(f)],
            confirm=False,
        )
        assert result["confirmed"] is False
        assert result["preview"]["attachments"] == [
            {
                "path": str(f),
                "filename": "report.txt",
                "mime_type": "text/plain",
                "size_bytes": 3,
            }
        ]

    async def test_relative_attachment_path_rejected(self, drafts_tools):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()

        with pytest.raises(ValueError, match="must be absolute"):
            await drafts_tools["create_draft_on_channel"](
                context,
                channel_id="cha_abc",
                body="hi",
                attachment_paths=["relative.txt"],
                confirm=False,
            )

    async def test_missing_attachment_path_rejected(self, drafts_tools, tmp_path: Path):
        context, lifespan = create_mock_context()
        lifespan.client = AsyncMock()

        with pytest.raises(FileNotFoundError):
            await drafts_tools["create_draft_on_channel"](
                context,
                channel_id="cha_abc",
                body="hi",
                attachment_paths=[str(tmp_path / "missing.txt")],
                confirm=False,
            )
