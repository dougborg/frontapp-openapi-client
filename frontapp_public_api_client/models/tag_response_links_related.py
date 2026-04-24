from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="TagResponseLinksRelated")


@_attrs_define
class TagResponseLinksRelated:
    conversations: str | Unset = UNSET
    owner: None | str | Unset = UNSET
    parent_tag: None | str | Unset = UNSET
    children: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conversations = self.conversations

        owner: None | str | Unset
        if isinstance(self.owner, Unset):
            owner = UNSET
        else:
            owner = self.owner

        parent_tag: None | str | Unset
        if isinstance(self.parent_tag, Unset):
            parent_tag = UNSET
        else:
            parent_tag = self.parent_tag

        children: None | str | Unset
        if isinstance(self.children, Unset):
            children = UNSET
        else:
            children = self.children

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if conversations is not UNSET:
            field_dict["conversations"] = conversations
        if owner is not UNSET:
            field_dict["owner"] = owner
        if parent_tag is not UNSET:
            field_dict["parent_tag"] = parent_tag
        if children is not UNSET:
            field_dict["children"] = children

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        conversations = d.pop("conversations", UNSET)

        def _parse_owner(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        owner = _parse_owner(d.pop("owner", UNSET))

        def _parse_parent_tag(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_tag = _parse_parent_tag(d.pop("parent_tag", UNSET))

        def _parse_children(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        children = _parse_children(d.pop("children", UNSET))

        tag_response_links_related = cls(
            conversations=conversations,
            owner=owner,
            parent_tag=parent_tag,
            children=children,
        )

        tag_response_links_related.additional_properties = d
        return tag_response_links_related

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
