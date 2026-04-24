from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_template_folder_response_links import (
        MessageTemplateFolderResponseLinks,
    )


T = TypeVar("T", bound="MessageTemplateFolderResponse")


@_attrs_define
class MessageTemplateFolderResponse:
    field_links: MessageTemplateFolderResponseLinks
    id: str
    name: str
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_template_folder_response_links import (
            MessageTemplateFolderResponseLinks,
        )

        d = dict(src_dict)
        field_links = MessageTemplateFolderResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        message_template_folder_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            created_at=created_at,
            updated_at=updated_at,
        )

        message_template_folder_response.additional_properties = d
        return message_template_folder_response

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
