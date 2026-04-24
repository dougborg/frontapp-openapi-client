from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="CustomFieldParameter")


@_attrs_define
class CustomFieldParameter:
    """An object whose key is the `name` property defined for the custom field in the Front UI. The value of the key must
    use the same `type` specified for the custom field, as described in https://dev.frontapp.com/reference/custom-fields

        Example:
            {'city': 'London, UK', 'isVIP': True, 'renewal_date': 1525417200, 'sla_time': 90, 'owner': 'leela@planet-
                express.com', 'replyTo': 'inb_55c8c149', 'Job Title': 'firefighter'}

    """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        custom_field_parameter = cls()

        custom_field_parameter.additional_properties = d
        return custom_field_parameter

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
