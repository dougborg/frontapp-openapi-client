from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.teammate_group_response_links import TeammateGroupResponseLinks
    from ..models.teammate_group_response_permissions import (
        TeammateGroupResponsePermissions,
    )


T = TypeVar("T", bound="TeammateGroupResponse")


@_attrs_define
class TeammateGroupResponse:
    """A teammate group is a group of teammates in Front."""

    field_links: TeammateGroupResponseLinks
    id: str
    name: str
    description: None | str
    is_managed_by_scim: bool
    permissions: TeammateGroupResponsePermissions
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        description: None | str
        description = self.description

        is_managed_by_scim = self.is_managed_by_scim

        permissions = self.permissions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "description": description,
                "is_managed_by_scim": is_managed_by_scim,
                "permissions": permissions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.teammate_group_response_links import TeammateGroupResponseLinks
        from ..models.teammate_group_response_permissions import (
            TeammateGroupResponsePermissions,
        )

        d = dict(src_dict)
        field_links = TeammateGroupResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        is_managed_by_scim = d.pop("is_managed_by_scim")

        permissions = TeammateGroupResponsePermissions.from_dict(d.pop("permissions"))

        teammate_group_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            description=description,
            is_managed_by_scim=is_managed_by_scim,
            permissions=permissions,
        )

        teammate_group_response.additional_properties = d
        return teammate_group_response

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
