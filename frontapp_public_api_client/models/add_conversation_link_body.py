from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="AddConversationLinkBody")


@_attrs_define
class AddConversationLinkBody:
    link_ids: list[str] | Unset = UNSET
    link_external_urls: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        link_ids: list[str] | Unset = UNSET
        if not isinstance(self.link_ids, Unset):
            link_ids = self.link_ids

        link_external_urls: list[str] | Unset = UNSET
        if not isinstance(self.link_external_urls, Unset):
            link_external_urls = self.link_external_urls

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if link_ids is not UNSET:
            field_dict["link_ids"] = link_ids
        if link_external_urls is not UNSET:
            field_dict["link_external_urls"] = link_external_urls

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        link_ids = cast(list[str], d.pop("link_ids", UNSET))

        link_external_urls = cast(list[str], d.pop("link_external_urls", UNSET))

        add_conversation_link_body = cls(
            link_ids=link_ids,
            link_external_urls=link_external_urls,
        )

        add_conversation_link_body.additional_properties = d
        return add_conversation_link_body

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
