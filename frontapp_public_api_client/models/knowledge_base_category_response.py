from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.knowledge_base_category_response_locale import (
    KnowledgeBaseCategoryResponseLocale,
)

if TYPE_CHECKING:
    from ..models.knowledge_base_category_response_links import (
        KnowledgeBaseCategoryResponseLinks,
    )


T = TypeVar("T", bound="KnowledgeBaseCategoryResponse")


@_attrs_define
class KnowledgeBaseCategoryResponse:
    field_links: KnowledgeBaseCategoryResponseLinks
    id: str
    name: None | str
    description: None | str
    is_hidden: bool
    locale: KnowledgeBaseCategoryResponseLocale
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name: None | str
        name = self.name

        description: None | str
        description = self.description

        is_hidden = self.is_hidden

        locale = self.locale.value

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
                "is_hidden": is_hidden,
                "locale": locale,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.knowledge_base_category_response_links import (
            KnowledgeBaseCategoryResponseLinks,
        )

        d = dict(src_dict)
        field_links = KnowledgeBaseCategoryResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        is_hidden = d.pop("is_hidden")

        locale = KnowledgeBaseCategoryResponseLocale(d.pop("locale"))

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        knowledge_base_category_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            description=description,
            is_hidden=is_hidden,
            locale=locale,
            created_at=created_at,
            updated_at=updated_at,
        )

        knowledge_base_category_response.additional_properties = d
        return knowledge_base_category_response

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
