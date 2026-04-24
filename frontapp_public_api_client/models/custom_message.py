from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, File, FileTypes, Unset
from ..models.custom_message_body_format import CustomMessageBodyFormat

if TYPE_CHECKING:
    from ..models.custom_message_metadata import CustomMessageMetadata
    from ..models.custom_message_sender import CustomMessageSender


T = TypeVar("T", bound="CustomMessage")


@_attrs_define
class CustomMessage:
    sender: CustomMessageSender
    body: str
    subject: str | Unset = UNSET
    body_format: CustomMessageBodyFormat | Unset = CustomMessageBodyFormat.MARKDOWN
    metadata: CustomMessageMetadata | Unset = UNSET
    attachments: list[File] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sender = self.sender.to_dict()

        body = self.body

        subject = self.subject

        body_format: str | Unset = UNSET
        if not isinstance(self.body_format, Unset):
            body_format = self.body_format.value

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        attachments: list[FileTypes] | Unset = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_tuple()

                attachments.append(attachments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sender": sender,
                "body": body,
            }
        )
        if subject is not UNSET:
            field_dict["subject"] = subject
        if body_format is not UNSET:
            field_dict["body_format"] = body_format
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_message_metadata import CustomMessageMetadata
        from ..models.custom_message_sender import CustomMessageSender

        d = dict(src_dict)
        sender = CustomMessageSender.from_dict(d.pop("sender"))

        body = d.pop("body")

        subject = d.pop("subject", UNSET)

        _body_format = d.pop("body_format", UNSET)
        body_format: CustomMessageBodyFormat | Unset
        if isinstance(_body_format, Unset):
            body_format = UNSET
        else:
            body_format = CustomMessageBodyFormat(_body_format)

        _metadata = d.pop("metadata", UNSET)
        metadata: CustomMessageMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CustomMessageMetadata.from_dict(_metadata)

        _attachments = d.pop("attachments", UNSET)
        attachments: list[File] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = File(payload=BytesIO(attachments_item_data))

                attachments.append(attachments_item)

        custom_message = cls(
            sender=sender,
            body=body,
            subject=subject,
            body_format=body_format,
            metadata=metadata,
            attachments=attachments,
        )

        custom_message.additional_properties = d
        return custom_message

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
