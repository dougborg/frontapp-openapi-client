from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tag_response_links import TagResponseLinks


T = TypeVar("T", bound="TagResponse")


@_attrs_define
class TagResponse:
    """A tag is a label that can be used to classify conversations."""

    field_links: TagResponseLinks
    id: str
    name: str
    description: None | str
    highlight: None | str
    is_private: bool
    is_visible_in_conversation_lists: bool
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        description: None | str
        description = self.description

        highlight: None | str
        highlight = self.highlight

        is_private = self.is_private

        is_visible_in_conversation_lists = self.is_visible_in_conversation_lists

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "description": description,
                "highlight": highlight,
                "is_private": is_private,
                "is_visible_in_conversation_lists": is_visible_in_conversation_lists,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tag_response_links import TagResponseLinks

        d = dict(src_dict)
        field_links = TagResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        def _parse_highlight(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        highlight = _parse_highlight(d.pop("highlight"))

        is_private = d.pop("is_private")

        is_visible_in_conversation_lists = d.pop("is_visible_in_conversation_lists")

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        tag_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            description=description,
            highlight=highlight,
            is_private=is_private,
            is_visible_in_conversation_lists=is_visible_in_conversation_lists,
            created_at=created_at,
            updated_at=updated_at,
        )

        tag_response.additional_properties = d
        return tag_response

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
