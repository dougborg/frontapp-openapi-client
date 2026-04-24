from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.create_channel_settings_undo_send_time import (
    CreateChannelSettingsUndoSendTime,
)

T = TypeVar("T", bound="CreateChannelSettings")


@_attrs_define
class CreateChannelSettings:
    """Settings of the channel"""

    undo_send_time: CreateChannelSettingsUndoSendTime | Unset = UNSET
    all_teammates_can_reply: bool | Unset = UNSET
    webhook_url: str | Unset = UNSET
    sid: str | Unset = UNSET
    auth_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        undo_send_time: int | Unset = UNSET
        if not isinstance(self.undo_send_time, Unset):
            undo_send_time = self.undo_send_time.value

        all_teammates_can_reply = self.all_teammates_can_reply

        webhook_url = self.webhook_url

        sid = self.sid

        auth_token = self.auth_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if undo_send_time is not UNSET:
            field_dict["undo_send_time"] = undo_send_time
        if all_teammates_can_reply is not UNSET:
            field_dict["all_teammates_can_reply"] = all_teammates_can_reply
        if webhook_url is not UNSET:
            field_dict["webhook_url"] = webhook_url
        if sid is not UNSET:
            field_dict["sid"] = sid
        if auth_token is not UNSET:
            field_dict["auth_token"] = auth_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _undo_send_time = d.pop("undo_send_time", UNSET)
        undo_send_time: CreateChannelSettingsUndoSendTime | Unset
        if isinstance(_undo_send_time, Unset):
            undo_send_time = UNSET
        else:
            undo_send_time = CreateChannelSettingsUndoSendTime(_undo_send_time)

        all_teammates_can_reply = d.pop("all_teammates_can_reply", UNSET)

        webhook_url = d.pop("webhook_url", UNSET)

        sid = d.pop("sid", UNSET)

        auth_token = d.pop("auth_token", UNSET)

        create_channel_settings = cls(
            undo_send_time=undo_send_time,
            all_teammates_can_reply=all_teammates_can_reply,
            webhook_url=webhook_url,
            sid=sid,
            auth_token=auth_token,
        )

        create_channel_settings.additional_properties = d
        return create_channel_settings

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
