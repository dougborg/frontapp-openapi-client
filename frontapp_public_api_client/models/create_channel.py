from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.create_channel_type import CreateChannelType

if TYPE_CHECKING:
    from ..models.create_channel_settings import CreateChannelSettings


T = TypeVar("T", bound="CreateChannel")


@_attrs_define
class CreateChannel:
    type_: CreateChannelType
    name: str | Unset = UNSET
    settings: CreateChannelSettings | Unset = UNSET
    send_as: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        name = self.name

        settings: dict[str, Any] | Unset = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        send_as = self.send_as

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if settings is not UNSET:
            field_dict["settings"] = settings
        if send_as is not UNSET:
            field_dict["send_as"] = send_as

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_channel_settings import CreateChannelSettings

        d = dict(src_dict)
        type_ = CreateChannelType(d.pop("type"))

        name = d.pop("name", UNSET)

        _settings = d.pop("settings", UNSET)
        settings: CreateChannelSettings | Unset
        if isinstance(_settings, Unset):
            settings = UNSET
        else:
            settings = CreateChannelSettings.from_dict(_settings)

        send_as = d.pop("send_as", UNSET)

        create_channel = cls(
            type_=type_,
            name=name,
            settings=settings,
            send_as=send_as,
        )

        create_channel.additional_properties = d
        return create_channel

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
