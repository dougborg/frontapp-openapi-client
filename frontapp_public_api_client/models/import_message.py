from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, File, FileTypes, Unset
from ..models.import_message_body_format import ImportMessageBodyFormat
from ..models.import_message_type import ImportMessageType

if TYPE_CHECKING:
    from ..models.import_message_metadata import ImportMessageMetadata
    from ..models.import_message_sender import ImportMessageSender


T = TypeVar("T", bound="ImportMessage")


@_attrs_define
class ImportMessage:
    sender: ImportMessageSender
    to: list[str]
    body: str
    external_id: str
    created_at: int
    metadata: ImportMessageMetadata
    cc: list[str] | Unset = UNSET
    bcc: list[str] | Unset = UNSET
    subject: str | Unset = UNSET
    body_format: ImportMessageBodyFormat | Unset = ImportMessageBodyFormat.MARKDOWN
    type_: ImportMessageType | Unset = ImportMessageType.EMAIL
    assignee_id: str | Unset = UNSET
    tags: list[str] | Unset = UNSET
    conversation_id: str | Unset = UNSET
    attachments: list[File] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sender = self.sender.to_dict()

        to = self.to

        body = self.body

        external_id = self.external_id

        created_at = self.created_at

        metadata = self.metadata.to_dict()

        cc: list[str] | Unset = UNSET
        if not isinstance(self.cc, Unset):
            cc = self.cc

        bcc: list[str] | Unset = UNSET
        if not isinstance(self.bcc, Unset):
            bcc = self.bcc

        subject = self.subject

        body_format: str | Unset = UNSET
        if not isinstance(self.body_format, Unset):
            body_format = self.body_format.value

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        assignee_id = self.assignee_id

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        conversation_id = self.conversation_id

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
                "to": to,
                "body": body,
                "external_id": external_id,
                "created_at": created_at,
                "metadata": metadata,
            }
        )
        if cc is not UNSET:
            field_dict["cc"] = cc
        if bcc is not UNSET:
            field_dict["bcc"] = bcc
        if subject is not UNSET:
            field_dict["subject"] = subject
        if body_format is not UNSET:
            field_dict["body_format"] = body_format
        if type_ is not UNSET:
            field_dict["type"] = type_
        if assignee_id is not UNSET:
            field_dict["assignee_id"] = assignee_id
        if tags is not UNSET:
            field_dict["tags"] = tags
        if conversation_id is not UNSET:
            field_dict["conversation_id"] = conversation_id
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.import_message_metadata import ImportMessageMetadata
        from ..models.import_message_sender import ImportMessageSender

        d = dict(src_dict)
        sender = ImportMessageSender.from_dict(d.pop("sender"))

        to = cast(list[str], d.pop("to"))

        body = d.pop("body")

        external_id = d.pop("external_id")

        created_at = d.pop("created_at")

        metadata = ImportMessageMetadata.from_dict(d.pop("metadata"))

        cc = cast(list[str], d.pop("cc", UNSET))

        bcc = cast(list[str], d.pop("bcc", UNSET))

        subject = d.pop("subject", UNSET)

        _body_format = d.pop("body_format", UNSET)
        body_format: ImportMessageBodyFormat | Unset
        if isinstance(_body_format, Unset):
            body_format = UNSET
        else:
            body_format = ImportMessageBodyFormat(_body_format)

        _type_ = d.pop("type", UNSET)
        type_: ImportMessageType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = ImportMessageType(_type_)

        assignee_id = d.pop("assignee_id", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))

        conversation_id = d.pop("conversation_id", UNSET)

        _attachments = d.pop("attachments", UNSET)
        attachments: list[File] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = File(payload=BytesIO(attachments_item_data))

                attachments.append(attachments_item)

        import_message = cls(
            sender=sender,
            to=to,
            body=body,
            external_id=external_id,
            created_at=created_at,
            metadata=metadata,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body_format=body_format,
            type_=type_,
            assignee_id=assignee_id,
            tags=tags,
            conversation_id=conversation_id,
            attachments=attachments,
        )

        import_message.additional_properties = d
        return import_message

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
