from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="TeammateGroupResponsePermissionsContacts")


@_attrs_define
class TeammateGroupResponsePermissionsContacts:
    """Permissions for teammate group access to contact lists"""

    access: str | Unset = UNSET
    contact_list_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access = self.access

        contact_list_ids: list[str] | Unset = UNSET
        if not isinstance(self.contact_list_ids, Unset):
            contact_list_ids = self.contact_list_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access is not UNSET:
            field_dict["access"] = access
        if contact_list_ids is not UNSET:
            field_dict["contact_list_ids"] = contact_list_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access = d.pop("access", UNSET)

        contact_list_ids = cast(list[str], d.pop("contact_list_ids", UNSET))

        teammate_group_response_permissions_contacts = cls(
            access=access,
            contact_list_ids=contact_list_ids,
        )

        teammate_group_response_permissions_contacts.additional_properties = d
        return teammate_group_response_permissions_contacts

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
