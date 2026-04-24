from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_teammate_group_permissions import (
        CreateTeammateGroupPermissions,
    )


T = TypeVar("T", bound="CreateTeammateGroup")


@_attrs_define
class CreateTeammateGroup:
    name: str
    description: str | Unset = UNSET
    permissions: CreateTeammateGroupPermissions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        permissions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_teammate_group_permissions import (
            CreateTeammateGroupPermissions,
        )

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        _permissions = d.pop("permissions", UNSET)
        permissions: CreateTeammateGroupPermissions | Unset
        if isinstance(_permissions, Unset):
            permissions = UNSET
        else:
            permissions = CreateTeammateGroupPermissions.from_dict(_permissions)

        create_teammate_group = cls(
            name=name,
            description=description,
            permissions=permissions,
        )

        create_teammate_group.additional_properties = d
        return create_teammate_group

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
