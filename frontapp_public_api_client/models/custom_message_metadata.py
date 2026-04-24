from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_message_metadata_headers import CustomMessageMetadataHeaders


T = TypeVar("T", bound="CustomMessageMetadata")


@_attrs_define
class CustomMessageMetadata:
    thread_ref: str | Unset = UNSET
    headers: CustomMessageMetadataHeaders | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        thread_ref = self.thread_ref

        headers: dict[str, Any] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if thread_ref is not UNSET:
            field_dict["thread_ref"] = thread_ref
        if headers is not UNSET:
            field_dict["headers"] = headers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_message_metadata_headers import (
            CustomMessageMetadataHeaders,
        )

        d = dict(src_dict)
        thread_ref = d.pop("thread_ref", UNSET)

        _headers = d.pop("headers", UNSET)
        headers: CustomMessageMetadataHeaders | Unset
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = CustomMessageMetadataHeaders.from_dict(_headers)

        custom_message_metadata = cls(
            thread_ref=thread_ref,
            headers=headers,
        )

        custom_message_metadata.additional_properties = d
        return custom_message_metadata

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
