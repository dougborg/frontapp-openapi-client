from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_teammate_group_permissions_contacts import (
        UpdateTeammateGroupPermissionsContacts,
    )


T = TypeVar("T", bound="UpdateTeammateGroupPermissions")


@_attrs_define
class UpdateTeammateGroupPermissions:
    """Permissions for the teammate group"""

    contacts: UpdateTeammateGroupPermissionsContacts | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contacts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.contacts, Unset):
            contacts = self.contacts.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contacts is not UNSET:
            field_dict["contacts"] = contacts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_teammate_group_permissions_contacts import (
            UpdateTeammateGroupPermissionsContacts,
        )

        d = dict(src_dict)
        _contacts = d.pop("contacts", UNSET)
        contacts: UpdateTeammateGroupPermissionsContacts | Unset
        if isinstance(_contacts, Unset):
            contacts = UNSET
        else:
            contacts = UpdateTeammateGroupPermissionsContacts.from_dict(_contacts)

        update_teammate_group_permissions = cls(
            contacts=contacts,
        )

        update_teammate_group_permissions.additional_properties = d
        return update_teammate_group_permissions

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
