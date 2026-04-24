from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.role_response_links_related import RoleResponseLinksRelated


T = TypeVar("T", bound="RoleResponseLinks")


@_attrs_define
class RoleResponseLinks:
    related: RoleResponseLinksRelated | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        related: dict[str, Any] | Unset = UNSET
        if not isinstance(self.related, Unset):
            related = self.related.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if related is not UNSET:
            field_dict["related"] = related

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.role_response_links_related import RoleResponseLinksRelated

        d = dict(src_dict)
        _related = d.pop("related", UNSET)
        related: RoleResponseLinksRelated | Unset
        if isinstance(_related, Unset):
            related = UNSET
        else:
            related = RoleResponseLinksRelated.from_dict(_related)

        role_response_links = cls(
            related=related,
        )

        role_response_links.additional_properties = d
        return role_response_links

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
