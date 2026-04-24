from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, File, FileTypes, Unset

if TYPE_CHECKING:
    from ..models.outbound_reply_message_options import OutboundReplyMessageOptions


T = TypeVar("T", bound="OutboundReplyMessage")


@_attrs_define
class OutboundReplyMessage:
    body: str
    to: list[str] | Unset = UNSET
    cc: list[str] | Unset = UNSET
    bcc: list[str] | Unset = UNSET
    sender_name: str | Unset = UNSET
    subject: str | Unset = UNSET
    author_id: str | Unset = UNSET
    channel_id: str | Unset = UNSET
    text: str | Unset = UNSET
    quote_body: str | Unset = UNSET
    options: OutboundReplyMessageOptions | Unset = UNSET
    attachments: list[File] | Unset = UNSET
    signature_id: str | Unset = UNSET
    should_add_default_signature: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        body = self.body

        to: list[str] | Unset = UNSET
        if not isinstance(self.to, Unset):
            to = self.to

        cc: list[str] | Unset = UNSET
        if not isinstance(self.cc, Unset):
            cc = self.cc

        bcc: list[str] | Unset = UNSET
        if not isinstance(self.bcc, Unset):
            bcc = self.bcc

        sender_name = self.sender_name

        subject = self.subject

        author_id = self.author_id

        channel_id = self.channel_id

        text = self.text

        quote_body = self.quote_body

        options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        attachments: list[FileTypes] | Unset = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_tuple()

                attachments.append(attachments_item)

        signature_id = self.signature_id

        should_add_default_signature = self.should_add_default_signature

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "body": body,
            }
        )
        if to is not UNSET:
            field_dict["to"] = to
        if cc is not UNSET:
            field_dict["cc"] = cc
        if bcc is not UNSET:
            field_dict["bcc"] = bcc
        if sender_name is not UNSET:
            field_dict["sender_name"] = sender_name
        if subject is not UNSET:
            field_dict["subject"] = subject
        if author_id is not UNSET:
            field_dict["author_id"] = author_id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if text is not UNSET:
            field_dict["text"] = text
        if quote_body is not UNSET:
            field_dict["quote_body"] = quote_body
        if options is not UNSET:
            field_dict["options"] = options
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if signature_id is not UNSET:
            field_dict["signature_id"] = signature_id
        if should_add_default_signature is not UNSET:
            field_dict["should_add_default_signature"] = should_add_default_signature

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.outbound_reply_message_options import OutboundReplyMessageOptions

        d = dict(src_dict)
        body = d.pop("body")

        to = cast(list[str], d.pop("to", UNSET))

        cc = cast(list[str], d.pop("cc", UNSET))

        bcc = cast(list[str], d.pop("bcc", UNSET))

        sender_name = d.pop("sender_name", UNSET)

        subject = d.pop("subject", UNSET)

        author_id = d.pop("author_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        text = d.pop("text", UNSET)

        quote_body = d.pop("quote_body", UNSET)

        _options = d.pop("options", UNSET)
        options: OutboundReplyMessageOptions | Unset
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = OutboundReplyMessageOptions.from_dict(_options)

        _attachments = d.pop("attachments", UNSET)
        attachments: list[File] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = File(payload=BytesIO(attachments_item_data))

                attachments.append(attachments_item)

        signature_id = d.pop("signature_id", UNSET)

        should_add_default_signature = d.pop("should_add_default_signature", UNSET)

        outbound_reply_message = cls(
            body=body,
            to=to,
            cc=cc,
            bcc=bcc,
            sender_name=sender_name,
            subject=subject,
            author_id=author_id,
            channel_id=channel_id,
            text=text,
            quote_body=quote_body,
            options=options,
            attachments=attachments,
            signature_id=signature_id,
            should_add_default_signature=should_add_default_signature,
        )

        outbound_reply_message.additional_properties = d
        return outbound_reply_message

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
