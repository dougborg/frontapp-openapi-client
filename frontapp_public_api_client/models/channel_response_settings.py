from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.channel_response_settings_undo_send_time import (
    ChannelResponseSettingsUndoSendTime,
)

T = TypeVar("T", bound="ChannelResponseSettings")


@_attrs_define
class ChannelResponseSettings:
    """Channel settings"""

    undo_send_time: ChannelResponseSettingsUndoSendTime | Unset = UNSET
    all_teammates_can_reply: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        undo_send_time: int | Unset = UNSET
        if not isinstance(self.undo_send_time, Unset):
            undo_send_time = self.undo_send_time.value

        all_teammates_can_reply = self.all_teammates_can_reply

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if undo_send_time is not UNSET:
            field_dict["undo_send_time"] = undo_send_time
        if all_teammates_can_reply is not UNSET:
            field_dict["all_teammates_can_reply"] = all_teammates_can_reply

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _undo_send_time = d.pop("undo_send_time", UNSET)
        undo_send_time: ChannelResponseSettingsUndoSendTime | Unset
        if isinstance(_undo_send_time, Unset):
            undo_send_time = UNSET
        else:
            undo_send_time = ChannelResponseSettingsUndoSendTime(_undo_send_time)

        all_teammates_can_reply = d.pop("all_teammates_can_reply", UNSET)

        channel_response_settings = cls(
            undo_send_time=undo_send_time,
            all_teammates_can_reply=all_teammates_can_reply,
        )

        channel_response_settings.additional_properties = d
        return channel_response_settings

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
