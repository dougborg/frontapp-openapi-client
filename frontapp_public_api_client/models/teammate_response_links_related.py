from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="TeammateResponseLinksRelated")


@_attrs_define
class TeammateResponseLinksRelated:
    inboxes: str | Unset = UNSET
    conversations: str | Unset = UNSET
    bot_source: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inboxes = self.inboxes

        conversations = self.conversations

        bot_source = self.bot_source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if inboxes is not UNSET:
            field_dict["inboxes"] = inboxes
        if conversations is not UNSET:
            field_dict["conversations"] = conversations
        if bot_source is not UNSET:
            field_dict["botSource"] = bot_source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        inboxes = d.pop("inboxes", UNSET)

        conversations = d.pop("conversations", UNSET)

        bot_source = d.pop("botSource", UNSET)

        teammate_response_links_related = cls(
            inboxes=inboxes,
            conversations=conversations,
            bot_source=bot_source,
        )

        teammate_response_links_related.additional_properties = d
        return teammate_response_links_related

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
