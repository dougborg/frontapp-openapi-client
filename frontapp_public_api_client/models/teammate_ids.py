from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="TeammateIds")


@_attrs_define
class TeammateIds:
    teammate_ids: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        teammate_ids = self.teammate_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "teammate_ids": teammate_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        teammate_ids = cast(list[str], d.pop("teammate_ids"))

        teammate_ids = cls(
            teammate_ids=teammate_ids,
        )

        teammate_ids.additional_properties = d
        return teammate_ids

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
