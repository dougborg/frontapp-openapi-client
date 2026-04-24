from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="CreateLink")


@_attrs_define
class CreateLink:
    """A link is used to connect a Front conversation to an external resource."""

    name: str | Unset = UNSET
    external_url: str | Unset = UNSET
    pattern: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        external_url = self.external_url

        pattern = self.pattern

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if external_url is not UNSET:
            field_dict["external_url"] = external_url
        if pattern is not UNSET:
            field_dict["pattern"] = pattern

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        external_url = d.pop("external_url", UNSET)

        pattern = d.pop("pattern", UNSET)

        create_link = cls(
            name=name,
            external_url=external_url,
            pattern=pattern,
        )

        create_link.additional_properties = d
        return create_link

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
