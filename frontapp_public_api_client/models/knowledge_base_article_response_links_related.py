from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="KnowledgeBaseArticleResponseLinksRelated")


@_attrs_define
class KnowledgeBaseArticleResponseLinksRelated:
    knowledge_base: str | Unset = UNSET
    category: str | Unset = UNSET
    last_editor: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        knowledge_base = self.knowledge_base

        category = self.category

        last_editor = self.last_editor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if knowledge_base is not UNSET:
            field_dict["knowledge_base"] = knowledge_base
        if category is not UNSET:
            field_dict["category"] = category
        if last_editor is not UNSET:
            field_dict["last_editor"] = last_editor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        knowledge_base = d.pop("knowledge_base", UNSET)

        category = d.pop("category", UNSET)

        last_editor = d.pop("last_editor", UNSET)

        knowledge_base_article_response_links_related = cls(
            knowledge_base=knowledge_base,
            category=category,
            last_editor=last_editor,
        )

        knowledge_base_article_response_links_related.additional_properties = d
        return knowledge_base_article_response_links_related

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
