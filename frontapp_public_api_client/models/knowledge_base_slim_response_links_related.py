from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="KnowledgeBaseSlimResponseLinksRelated")


@_attrs_define
class KnowledgeBaseSlimResponseLinksRelated:
    articles: str | Unset = UNSET
    categories: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        articles = self.articles

        categories = self.categories

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if articles is not UNSET:
            field_dict["articles"] = articles
        if categories is not UNSET:
            field_dict["categories"] = categories

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        articles = d.pop("articles", UNSET)

        categories = d.pop("categories", UNSET)

        knowledge_base_slim_response_links_related = cls(
            articles=articles,
            categories=categories,
        )

        knowledge_base_slim_response_links_related.additional_properties = d
        return knowledge_base_slim_response_links_related

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
