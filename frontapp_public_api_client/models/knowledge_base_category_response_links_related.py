from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="KnowledgeBaseCategoryResponseLinksRelated")


@_attrs_define
class KnowledgeBaseCategoryResponseLinksRelated:
    knowledge_base: str | Unset = UNSET
    parent_category: None | str | Unset = UNSET
    articles: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        knowledge_base = self.knowledge_base

        parent_category: None | str | Unset
        if isinstance(self.parent_category, Unset):
            parent_category = UNSET
        else:
            parent_category = self.parent_category

        articles = self.articles

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if knowledge_base is not UNSET:
            field_dict["knowledge_base"] = knowledge_base
        if parent_category is not UNSET:
            field_dict["parent_category"] = parent_category
        if articles is not UNSET:
            field_dict["articles"] = articles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        knowledge_base = d.pop("knowledge_base", UNSET)

        def _parse_parent_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_category = _parse_parent_category(d.pop("parent_category", UNSET))

        articles = d.pop("articles", UNSET)

        knowledge_base_category_response_links_related = cls(
            knowledge_base=knowledge_base,
            parent_category=parent_category,
            articles=articles,
        )

        knowledge_base_category_response_links_related.additional_properties = d
        return knowledge_base_category_response_links_related

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
