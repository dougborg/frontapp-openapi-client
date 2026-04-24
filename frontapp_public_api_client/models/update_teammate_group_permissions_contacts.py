from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="UpdateTeammateGroupPermissionsContacts")


@_attrs_define
class UpdateTeammateGroupPermissionsContacts:
    """Permissions for accessing contact lists. This only applies if shared contacts permissions are enabled."""

    access: str
    contact_group_ids: list[str] | Unset = UNSET
    contact_list_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access = self.access

        contact_group_ids: list[str] | Unset = UNSET
        if not isinstance(self.contact_group_ids, Unset):
            contact_group_ids = self.contact_group_ids

        contact_list_ids: list[str] | Unset = UNSET
        if not isinstance(self.contact_list_ids, Unset):
            contact_list_ids = self.contact_list_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access": access,
            }
        )
        if contact_group_ids is not UNSET:
            field_dict["contact_group_ids"] = contact_group_ids
        if contact_list_ids is not UNSET:
            field_dict["contact_list_ids"] = contact_list_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access = d.pop("access")

        contact_group_ids = cast(list[str], d.pop("contact_group_ids", UNSET))

        contact_list_ids = cast(list[str], d.pop("contact_list_ids", UNSET))

        update_teammate_group_permissions_contacts = cls(
            access=access,
            contact_group_ids=contact_group_ids,
            contact_list_ids=contact_list_ids,
        )

        update_teammate_group_permissions_contacts.additional_properties = d
        return update_teammate_group_permissions_contacts

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
