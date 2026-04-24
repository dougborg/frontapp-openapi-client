from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, File, FileTypes, Unset
from ..models.edit_draft_mode import EditDraftMode

T = TypeVar("T", bound="EditDraft")


@_attrs_define
class EditDraft:
    body: str
    channel_id: str
    author_id: str | Unset = UNSET
    to: list[str] | Unset = UNSET
    cc: list[str] | Unset = UNSET
    bcc: list[str] | Unset = UNSET
    subject: str | Unset = UNSET
    quote_body: str | Unset = UNSET
    attachments: list[File] | Unset = UNSET
    mode: EditDraftMode | Unset = UNSET
    signature_id: str | Unset = UNSET
    should_add_default_signature: bool | Unset = UNSET
    version: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        body = self.body

        channel_id = self.channel_id

        author_id = self.author_id

        to: list[str] | Unset = UNSET
        if not isinstance(self.to, Unset):
            to = self.to

        cc: list[str] | Unset = UNSET
        if not isinstance(self.cc, Unset):
            cc = self.cc

        bcc: list[str] | Unset = UNSET
        if not isinstance(self.bcc, Unset):
            bcc = self.bcc

        subject = self.subject

        quote_body = self.quote_body

        attachments: list[FileTypes] | Unset = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_tuple()

                attachments.append(attachments_item)

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        signature_id = self.signature_id

        should_add_default_signature = self.should_add_default_signature

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "body": body,
                "channel_id": channel_id,
            }
        )
        if author_id is not UNSET:
            field_dict["author_id"] = author_id
        if to is not UNSET:
            field_dict["to"] = to
        if cc is not UNSET:
            field_dict["cc"] = cc
        if bcc is not UNSET:
            field_dict["bcc"] = bcc
        if subject is not UNSET:
            field_dict["subject"] = subject
        if quote_body is not UNSET:
            field_dict["quote_body"] = quote_body
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if mode is not UNSET:
            field_dict["mode"] = mode
        if signature_id is not UNSET:
            field_dict["signature_id"] = signature_id
        if should_add_default_signature is not UNSET:
            field_dict["should_add_default_signature"] = should_add_default_signature
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        body = d.pop("body")

        channel_id = d.pop("channel_id")

        author_id = d.pop("author_id", UNSET)

        to = cast(list[str], d.pop("to", UNSET))

        cc = cast(list[str], d.pop("cc", UNSET))

        bcc = cast(list[str], d.pop("bcc", UNSET))

        subject = d.pop("subject", UNSET)

        quote_body = d.pop("quote_body", UNSET)

        _attachments = d.pop("attachments", UNSET)
        attachments: list[File] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = File(payload=BytesIO(attachments_item_data))

                attachments.append(attachments_item)

        _mode = d.pop("mode", UNSET)
        mode: EditDraftMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = EditDraftMode(_mode)

        signature_id = d.pop("signature_id", UNSET)

        should_add_default_signature = d.pop("should_add_default_signature", UNSET)

        version = d.pop("version", UNSET)

        edit_draft = cls(
            body=body,
            channel_id=channel_id,
            author_id=author_id,
            to=to,
            cc=cc,
            bcc=bcc,
            subject=subject,
            quote_body=quote_body,
            attachments=attachments,
            mode=mode,
            signature_id=signature_id,
            should_add_default_signature=should_add_default_signature,
            version=version,
        )

        edit_draft.additional_properties = d
        return edit_draft

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
