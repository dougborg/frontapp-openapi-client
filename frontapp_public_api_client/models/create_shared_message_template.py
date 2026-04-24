from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="CreateSharedMessageTemplate")


@_attrs_define
class CreateSharedMessageTemplate:
    """A message template that is used for pre-written responses"""

    name: str
    body: str
    subject: str | Unset = UNSET
    folder_id: str | Unset = UNSET
    inbox_ids: list[str] | Unset = UNSET
    attachments: list[File] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        body = self.body

        subject = self.subject

        folder_id = self.folder_id

        inbox_ids: list[str] | Unset = UNSET
        if not isinstance(self.inbox_ids, Unset):
            inbox_ids = self.inbox_ids

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
                "name": name,
                "body": body,
            }
        )
        if subject is not UNSET:
            field_dict["subject"] = subject
        if folder_id is not UNSET:
            field_dict["folder_id"] = folder_id
        if inbox_ids is not UNSET:
            field_dict["inbox_ids"] = inbox_ids
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        body = d.pop("body")

        subject = d.pop("subject", UNSET)

        folder_id = d.pop("folder_id", UNSET)

        inbox_ids = cast(list[str], d.pop("inbox_ids", UNSET))

        _attachments = d.pop("attachments", UNSET)
        attachments: list[File] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = File(payload=BytesIO(attachments_item_data))

                attachments.append(attachments_item)

        create_shared_message_template = cls(
            name=name,
            body=body,
            subject=subject,
            folder_id=folder_id,
            inbox_ids=inbox_ids,
            attachments=attachments,
        )

        create_shared_message_template.additional_properties = d
        return create_shared_message_template

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
