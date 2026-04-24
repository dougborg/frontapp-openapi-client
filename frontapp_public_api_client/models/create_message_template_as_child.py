from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="CreateMessageTemplateAsChild")


@_attrs_define
class CreateMessageTemplateAsChild:
    """A message template that is used for pre-written responses"""

    name: str
    body: str
    subject: str | Unset = UNSET
    inbox_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        body = self.body

        subject = self.subject

        inbox_ids: list[str] | Unset = UNSET
        if not isinstance(self.inbox_ids, Unset):
            inbox_ids = self.inbox_ids

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
        if inbox_ids is not UNSET:
            field_dict["inbox_ids"] = inbox_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        body = d.pop("body")

        subject = d.pop("subject", UNSET)

        inbox_ids = cast(list[str], d.pop("inbox_ids", UNSET))

        create_message_template_as_child = cls(
            name=name,
            body=body,
            subject=subject,
            inbox_ids=inbox_ids,
        )

        create_message_template_as_child.additional_properties = d
        return create_message_template_as_child

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
