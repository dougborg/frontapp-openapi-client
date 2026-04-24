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


T = TypeVar("T", bound="UpdateTeammate")


@_attrs_define
class UpdateTeammate:
    username: str | Unset = UNSET
    first_name: str | Unset = UNSET
    last_name: str | Unset = UNSET
    is_available: bool | Unset = UNSET
    custom_fields: CustomFieldParameter | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        first_name = self.first_name

        last_name = self.last_name

        is_available = self.is_available

        custom_fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = self.custom_fields.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if is_available is not UNSET:
            field_dict["is_available"] = is_available
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_field_parameter import CustomFieldParameter

        d = dict(src_dict)
        username = d.pop("username", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        is_available = d.pop("is_available", UNSET)

        _custom_fields = d.pop("custom_fields", UNSET)
        custom_fields: CustomFieldParameter | Unset
        if isinstance(_custom_fields, Unset):
            custom_fields = UNSET
        else:
            custom_fields = CustomFieldParameter.from_dict(_custom_fields)

        update_teammate = cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_available=is_available,
            custom_fields=custom_fields,
        )

        update_teammate.additional_properties = d
        return update_teammate

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
