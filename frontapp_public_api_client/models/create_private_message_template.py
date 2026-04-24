from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="CreatePrivateMessageTemplate")


@_attrs_define
class CreatePrivateMessageTemplate:
    """A message template that is used for pre-written responses"""

    name: str
    body: str
    subject: str | Unset = UNSET
    folder_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        body = self.body

        subject = self.subject

        folder_id = self.folder_id

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        body = d.pop("body")

        subject = d.pop("subject", UNSET)

        folder_id = d.pop("folder_id", UNSET)

        create_private_message_template = cls(
            name=name,
            body=body,
            subject=subject,
            folder_id=folder_id,
        )

        create_private_message_template.additional_properties = d
        return create_private_message_template

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
