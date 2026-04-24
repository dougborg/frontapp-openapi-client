from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="MessageResponseLinksRelated")


@_attrs_define
class MessageResponseLinksRelated:
    conversation: str | Unset = UNSET
    message_replied_to: str | Unset = UNSET
    message_seen: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conversation = self.conversation

        message_replied_to = self.message_replied_to

        message_seen = self.message_seen

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if conversation is not UNSET:
            field_dict["conversation"] = conversation
        if message_replied_to is not UNSET:
            field_dict["message_replied_to"] = message_replied_to
        if message_seen is not UNSET:
            field_dict["message_seen"] = message_seen

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        conversation = d.pop("conversation", UNSET)

        message_replied_to = d.pop("message_replied_to", UNSET)

        message_seen = d.pop("message_seen", UNSET)

        message_response_links_related = cls(
            conversation=conversation,
            message_replied_to=message_replied_to,
            message_seen=message_seen,
        )

        message_response_links_related.additional_properties = d
        return message_response_links_related

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
