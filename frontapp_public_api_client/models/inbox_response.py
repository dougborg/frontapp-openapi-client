from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_field_parameter import CustomFieldParameter
    from ..models.inbox_response_links import InboxResponseLinks


T = TypeVar("T", bound="InboxResponse")


@_attrs_define
class InboxResponse:
    field_links: InboxResponseLinks | Unset = UNSET
    id: str | Unset = UNSET
    name: str | Unset = UNSET
    is_private: bool | Unset = UNSET
    is_public: bool | Unset = UNSET
    custom_fields: CustomFieldParameter | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_links, Unset):
            field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        is_private = self.is_private

        is_public = self.is_public

        custom_fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = self.custom_fields.to_dict()

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
        if is_public is not UNSET:
            field_dict["is_public"] = is_public
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_field_parameter import CustomFieldParameter
        from ..models.inbox_response_links import InboxResponseLinks

        d = dict(src_dict)
        _field_links = d.pop("_links", UNSET)
        field_links: InboxResponseLinks | Unset
        if isinstance(_field_links, Unset):
            field_links = UNSET
        else:
            field_links = InboxResponseLinks.from_dict(_field_links)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        is_private = d.pop("is_private", UNSET)

        is_public = d.pop("is_public", UNSET)

        _custom_fields = d.pop("custom_fields", UNSET)
        custom_fields: CustomFieldParameter | Unset
        if isinstance(_custom_fields, Unset):
            custom_fields = UNSET
        else:
            custom_fields = CustomFieldParameter.from_dict(_custom_fields)

        inbox_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            is_private=is_private,
            is_public=is_public,
            custom_fields=custom_fields,
        )

        inbox_response.additional_properties = d
        return inbox_response

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
