from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="ConversationResponseMetadata")


@_attrs_define
class ConversationResponseMetadata:
    """Optional metadata about the conversation"""

    external_conversation_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        external_conversation_ids: list[str] | Unset = UNSET
        if not isinstance(self.external_conversation_ids, Unset):
            external_conversation_ids = self.external_conversation_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if external_conversation_ids is not UNSET:
            field_dict["external_conversation_ids"] = external_conversation_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        external_conversation_ids = cast(
            list[str], d.pop("external_conversation_ids", UNSET)
        )

        conversation_response_metadata = cls(
            external_conversation_ids=external_conversation_ids,
        )

        conversation_response_metadata.additional_properties = d
        return conversation_response_metadata

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
