from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.custom_field_response_type import CustomFieldResponseType

if TYPE_CHECKING:
    from ..models.custom_field_response_links import CustomFieldResponseLinks
    from ..models.custom_field_response_values_item import CustomFieldResponseValuesItem


T = TypeVar("T", bound="CustomFieldResponse")


@_attrs_define
class CustomFieldResponse:
    field_links: CustomFieldResponseLinks
    id: str
    name: str
    description: str
    type_: CustomFieldResponseType
    values: list[CustomFieldResponseValuesItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        description = self.description

        type_ = self.type_.value

        values: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.values, Unset):
            values = []
            for values_item_data in self.values:
                values_item = values_item_data.to_dict()
                values.append(values_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "description": description,
                "type": type_,
            }
        )
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_field_response_links import CustomFieldResponseLinks
        from ..models.custom_field_response_values_item import (
            CustomFieldResponseValuesItem,
        )

        d = dict(src_dict)
        field_links = CustomFieldResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        type_ = CustomFieldResponseType(d.pop("type"))

        _values = d.pop("values", UNSET)
        values: list[CustomFieldResponseValuesItem] | Unset = UNSET
        if _values is not UNSET:
            values = []
            for values_item_data in _values:
                values_item = CustomFieldResponseValuesItem.from_dict(values_item_data)

                values.append(values_item)

        custom_field_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            description=description,
            type_=type_,
            values=values,
        )

        custom_field_response.additional_properties = d
        return custom_field_response

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
