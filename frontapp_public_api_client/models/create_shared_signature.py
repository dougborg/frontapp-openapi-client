from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="CreateSharedSignature")


@_attrs_define
class CreateSharedSignature:
    """A signature that can be used to sign messages."""

    name: str
    body: str
    sender_info: str | Unset = UNSET
    is_visible_for_all_teammate_channels: bool | Unset = UNSET
    is_default: bool | Unset = False
    channel_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        body = self.body

        sender_info = self.sender_info

        is_visible_for_all_teammate_channels = self.is_visible_for_all_teammate_channels

        is_default = self.is_default

        channel_ids: list[str] | Unset = UNSET
        if not isinstance(self.channel_ids, Unset):
            channel_ids = self.channel_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "body": body,
            }
        )
        if sender_info is not UNSET:
            field_dict["sender_info"] = sender_info
        if is_visible_for_all_teammate_channels is not UNSET:
            field_dict["is_visible_for_all_teammate_channels"] = (
                is_visible_for_all_teammate_channels
            )
        if is_default is not UNSET:
            field_dict["is_default"] = is_default
        if channel_ids is not UNSET:
            field_dict["channel_ids"] = channel_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        body = d.pop("body")

        sender_info = d.pop("sender_info", UNSET)

        is_visible_for_all_teammate_channels = d.pop(
            "is_visible_for_all_teammate_channels", UNSET
        )

        is_default = d.pop("is_default", UNSET)

        channel_ids = cast(list[str], d.pop("channel_ids", UNSET))

        create_shared_signature = cls(
            name=name,
            body=body,
            sender_info=sender_info,
            is_visible_for_all_teammate_channels=is_visible_for_all_teammate_channels,
            is_default=is_default,
            channel_ids=channel_ids,
        )

        create_shared_signature.additional_properties = d
        return create_shared_signature

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
