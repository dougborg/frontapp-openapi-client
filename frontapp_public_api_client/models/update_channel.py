from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_channel_settings import UpdateChannelSettings


T = TypeVar("T", bound="UpdateChannel")


@_attrs_define
class UpdateChannel:
    name: str | Unset = UNSET
    inbox_id: str | Unset = UNSET
    settings: UpdateChannelSettings | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        inbox_id = self.inbox_id

        settings: dict[str, Any] | Unset = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if inbox_id is not UNSET:
            field_dict["inbox_id"] = inbox_id
        if settings is not UNSET:
            field_dict["settings"] = settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_channel_settings import UpdateChannelSettings

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        inbox_id = d.pop("inbox_id", UNSET)

        _settings = d.pop("settings", UNSET)
        settings: UpdateChannelSettings | Unset
        if isinstance(_settings, Unset):
            settings = UNSET
        else:
            settings = UpdateChannelSettings.from_dict(_settings)

        update_channel = cls(
            name=name,
            inbox_id=inbox_id,
            settings=settings,
        )

        update_channel.additional_properties = d
        return update_channel

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
