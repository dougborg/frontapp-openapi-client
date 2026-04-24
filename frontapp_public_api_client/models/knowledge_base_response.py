from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.knowledge_base_response_locale import KnowledgeBaseResponseLocale
from ..models.knowledge_base_response_status import KnowledgeBaseResponseStatus
from ..models.knowledge_base_response_type import KnowledgeBaseResponseType

if TYPE_CHECKING:
    from ..models.knowledge_base_response_links import KnowledgeBaseResponseLinks


T = TypeVar("T", bound="KnowledgeBaseResponse")


@_attrs_define
class KnowledgeBaseResponse:
    field_links: KnowledgeBaseResponseLinks
    id: str
    name: str
    status: KnowledgeBaseResponseStatus
    type_: KnowledgeBaseResponseType
    locale: KnowledgeBaseResponseLocale
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        status = self.status.value

        type_ = self.type_.value

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
                "status": status,
                "type": type_,
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
        from ..models.knowledge_base_response_links import KnowledgeBaseResponseLinks

        d = dict(src_dict)
        field_links = KnowledgeBaseResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        status = KnowledgeBaseResponseStatus(d.pop("status"))

        type_ = KnowledgeBaseResponseType(d.pop("type"))

        locale = KnowledgeBaseResponseLocale(d.pop("locale"))

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        knowledge_base_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            status=status,
            type_=type_,
            locale=locale,
            created_at=created_at,
            updated_at=updated_at,
        )

        knowledge_base_response.additional_properties = d
        return knowledge_base_response

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
