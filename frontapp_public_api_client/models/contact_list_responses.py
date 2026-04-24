from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contact_list_responses_links import ContactListResponsesLinks


T = TypeVar("T", bound="ContactListResponses")


@_attrs_define
class ContactListResponses:
    field_links: ContactListResponsesLinks | Unset = UNSET
    id: str | Unset = UNSET
    name: str | Unset = UNSET
    is_private: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_links, Unset):
            field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        is_private = self.is_private

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_links is not UNSET:
            field_dict["_links"] = field_links
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if is_private is not UNSET:
            field_dict["is_private"] = is_private

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contact_list_responses_links import ContactListResponsesLinks

        d = dict(src_dict)
        _field_links = d.pop("_links", UNSET)
        field_links: ContactListResponsesLinks | Unset
        if isinstance(_field_links, Unset):
            field_links = UNSET
        else:
            field_links = ContactListResponsesLinks.from_dict(_field_links)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        is_private = d.pop("is_private", UNSET)

        contact_list_responses = cls(
            field_links=field_links,
            id=id,
            name=name,
            is_private=is_private,
        )

        contact_list_responses.additional_properties = d
        return contact_list_responses

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
