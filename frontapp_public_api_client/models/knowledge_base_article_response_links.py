from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.knowledge_base_article_response_links_related import (
        KnowledgeBaseArticleResponseLinksRelated,
    )


T = TypeVar("T", bound="KnowledgeBaseArticleResponseLinks")


@_attrs_define
class KnowledgeBaseArticleResponseLinks:
    self_: str | Unset = UNSET
    related: KnowledgeBaseArticleResponseLinksRelated | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        self_ = self.self_

        related: dict[str, Any] | Unset = UNSET
        if not isinstance(self.related, Unset):
            related = self.related.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if self_ is not UNSET:
            field_dict["self"] = self_
        if related is not UNSET:
            field_dict["related"] = related

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.knowledge_base_article_response_links_related import (
            KnowledgeBaseArticleResponseLinksRelated,
        )

        d = dict(src_dict)
        self_ = d.pop("self", UNSET)

        _related = d.pop("related", UNSET)
        related: KnowledgeBaseArticleResponseLinksRelated | Unset
        if isinstance(_related, Unset):
            related = UNSET
        else:
            related = KnowledgeBaseArticleResponseLinksRelated.from_dict(_related)

        knowledge_base_article_response_links = cls(
            self_=self_,
            related=related,
        )

        knowledge_base_article_response_links.additional_properties = d
        return knowledge_base_article_response_links

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
