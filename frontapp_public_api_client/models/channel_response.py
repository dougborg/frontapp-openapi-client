from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.channel_response_type import ChannelResponseType

if TYPE_CHECKING:
    from ..models.channel_response_links import ChannelResponseLinks
    from ..models.channel_response_settings import ChannelResponseSettings


T = TypeVar("T", bound="ChannelResponse")


@_attrs_define
class ChannelResponse:
    field_links: ChannelResponseLinks
    id: str
    type_: ChannelResponseType
    settings: ChannelResponseSettings
    is_private: bool = False
    is_valid: bool = False
    name: str | Unset = UNSET
    address: str | Unset = UNSET
    send_as: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        type_ = self.type_.value

        settings = self.settings.to_dict()

        is_private = self.is_private

        is_valid = self.is_valid

        name = self.name

        address = self.address

        send_as = self.send_as

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "type": type_,
                "settings": settings,
                "is_private": is_private,
                "is_valid": is_valid,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if address is not UNSET:
            field_dict["address"] = address
        if send_as is not UNSET:
            field_dict["send_as"] = send_as

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.channel_response_links import ChannelResponseLinks
        from ..models.channel_response_settings import ChannelResponseSettings

        d = dict(src_dict)
        field_links = ChannelResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        type_ = ChannelResponseType(d.pop("type"))

        settings = ChannelResponseSettings.from_dict(d.pop("settings"))

        is_private = d.pop("is_private")

        is_valid = d.pop("is_valid")

        name = d.pop("name", UNSET)

        address = d.pop("address", UNSET)

        send_as = d.pop("send_as", UNSET)

        channel_response = cls(
            field_links=field_links,
            id=id,
            type_=type_,
            settings=settings,
            is_private=is_private,
            is_valid=is_valid,
            name=name,
            address=address,
            send_as=send_as,
        )

        channel_response.additional_properties = d
        return channel_response

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
