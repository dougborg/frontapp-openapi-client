from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="OutboundMessageOptions")


@_attrs_define
class OutboundMessageOptions:
    tag_ids: list[str] | Unset = UNSET
    archive: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tag_ids: list[str] | Unset = UNSET
        if not isinstance(self.tag_ids, Unset):
            tag_ids = self.tag_ids

        archive = self.archive

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tag_ids is not UNSET:
            field_dict["tag_ids"] = tag_ids
        if archive is not UNSET:
            field_dict["archive"] = archive

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tag_ids = cast(list[str], d.pop("tag_ids", UNSET))

        archive = d.pop("archive", UNSET)

        outbound_message_options = cls(
            tag_ids=tag_ids,
            archive=archive,
        )

        outbound_message_options.additional_properties = d
        return outbound_message_options

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
