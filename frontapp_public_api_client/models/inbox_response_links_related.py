from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="InboxResponseLinksRelated")


@_attrs_define
class InboxResponseLinksRelated:
    teammates: str | Unset = UNSET
    conversations: str | Unset = UNSET
    channels: str | Unset = UNSET
    owner: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        teammates = self.teammates

        conversations = self.conversations

        channels = self.channels

        owner = self.owner

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if teammates is not UNSET:
            field_dict["teammates"] = teammates
        if conversations is not UNSET:
            field_dict["conversations"] = conversations
        if channels is not UNSET:
            field_dict["channels"] = channels
        if owner is not UNSET:
            field_dict["owner"] = owner

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        teammates = d.pop("teammates", UNSET)

        conversations = d.pop("conversations", UNSET)

        channels = d.pop("channels", UNSET)

        owner = d.pop("owner", UNSET)

        inbox_response_links_related = cls(
            teammates=teammates,
            conversations=conversations,
            channels=channels,
            owner=owner,
        )

        inbox_response_links_related.additional_properties = d
        return inbox_response_links_related

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
