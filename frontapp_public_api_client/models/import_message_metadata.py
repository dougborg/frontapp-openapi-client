from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="ImportMessageMetadata")


@_attrs_define
class ImportMessageMetadata:
    is_inbound: bool
    thread_ref: str | Unset = UNSET
    is_archived: bool | Unset = True
    should_skip_rules: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_inbound = self.is_inbound

        thread_ref = self.thread_ref

        is_archived = self.is_archived

        should_skip_rules = self.should_skip_rules

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "is_inbound": is_inbound,
            }
        )
        if thread_ref is not UNSET:
            field_dict["thread_ref"] = thread_ref
        if is_archived is not UNSET:
            field_dict["is_archived"] = is_archived
        if should_skip_rules is not UNSET:
            field_dict["should_skip_rules"] = should_skip_rules

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_inbound = d.pop("is_inbound")

        thread_ref = d.pop("thread_ref", UNSET)

        is_archived = d.pop("is_archived", UNSET)

        should_skip_rules = d.pop("should_skip_rules", UNSET)

        import_message_metadata = cls(
            is_inbound=is_inbound,
            thread_ref=thread_ref,
            is_archived=is_archived,
            should_skip_rules=should_skip_rules,
        )

        import_message_metadata.additional_properties = d
        return import_message_metadata

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
