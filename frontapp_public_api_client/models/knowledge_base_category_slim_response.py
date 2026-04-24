from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.knowledge_base_category_slim_response_links import (
        KnowledgeBaseCategorySlimResponseLinks,
    )


T = TypeVar("T", bound="KnowledgeBaseCategorySlimResponse")


@_attrs_define
class KnowledgeBaseCategorySlimResponse:
    field_links: KnowledgeBaseCategorySlimResponseLinks
    id: str
    slug: str
    is_hidden: bool
    locales: list[str]
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        slug = self.slug

        is_hidden = self.is_hidden

        locales = self.locales

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "slug": slug,
                "is_hidden": is_hidden,
                "locales": locales,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.knowledge_base_category_slim_response_links import (
            KnowledgeBaseCategorySlimResponseLinks,
        )

        d = dict(src_dict)
        field_links = KnowledgeBaseCategorySlimResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        slug = d.pop("slug")

        is_hidden = d.pop("is_hidden")

        locales = cast(list[str], d.pop("locales"))

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        knowledge_base_category_slim_response = cls(
            field_links=field_links,
            id=id,
            slug=slug,
            is_hidden=is_hidden,
            locales=locales,
            created_at=created_at,
            updated_at=updated_at,
        )

        knowledge_base_category_slim_response.additional_properties = d
        return knowledge_base_category_slim_response

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
