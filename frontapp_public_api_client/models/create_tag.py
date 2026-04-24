from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.create_tag_highlight import CreateTagHighlight

T = TypeVar("T", bound="CreateTag")


@_attrs_define
class CreateTag:
    """A tag is a label that can be used to classify conversations."""

    name: str
    description: str | Unset = UNSET
    highlight: CreateTagHighlight | Unset = UNSET
    is_visible_in_conversation_lists: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        highlight: str | Unset = UNSET
        if not isinstance(self.highlight, Unset):
            highlight = self.highlight.value

        is_visible_in_conversation_lists = self.is_visible_in_conversation_lists

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if highlight is not UNSET:
            field_dict["highlight"] = highlight
        if is_visible_in_conversation_lists is not UNSET:
            field_dict["is_visible_in_conversation_lists"] = (
                is_visible_in_conversation_lists
            )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        _highlight = d.pop("highlight", UNSET)
        highlight: CreateTagHighlight | Unset
        if isinstance(_highlight, Unset):
            highlight = UNSET
        else:
            highlight = CreateTagHighlight(_highlight)

        is_visible_in_conversation_lists = d.pop(
            "is_visible_in_conversation_lists", UNSET
        )

        create_tag = cls(
            name=name,
            description=description,
            highlight=highlight,
            is_visible_in_conversation_lists=is_visible_in_conversation_lists,
        )

        create_tag.additional_properties = d
        return create_tag

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
