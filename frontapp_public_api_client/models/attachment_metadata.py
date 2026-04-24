from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="AttachmentMetadata")


@_attrs_define
class AttachmentMetadata:
    """Attachment metadata"""

    is_inline: bool | Unset = UNSET
    cid: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_inline = self.is_inline

        cid = self.cid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_inline is not UNSET:
            field_dict["is_inline"] = is_inline
        if cid is not UNSET:
            field_dict["cid"] = cid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_inline = d.pop("is_inline", UNSET)

        cid = d.pop("cid", UNSET)

        attachment_metadata = cls(
            is_inline=is_inline,
            cid=cid,
        )

        attachment_metadata.additional_properties = d
        return attachment_metadata

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
