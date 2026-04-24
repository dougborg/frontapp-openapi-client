from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.signature_response_links import SignatureResponseLinks


T = TypeVar("T", bound="SignatureResponse")


@_attrs_define
class SignatureResponse:
    field_links: SignatureResponseLinks
    id: str
    name: None | str
    body: str
    sender_info: None | str
    is_visible_for_all_teammate_channels: bool
    is_default: bool
    is_private: bool
    channel_ids: list[str] | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name: None | str
        name = self.name

        body = self.body

        sender_info: None | str
        sender_info = self.sender_info

        is_visible_for_all_teammate_channels = self.is_visible_for_all_teammate_channels

        is_default = self.is_default

        is_private = self.is_private

        channel_ids: list[str] | None
        if isinstance(self.channel_ids, list):
            channel_ids = self.channel_ids

        else:
            channel_ids = self.channel_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "body": body,
                "sender_info": sender_info,
                "is_visible_for_all_teammate_channels": is_visible_for_all_teammate_channels,
                "is_default": is_default,
                "is_private": is_private,
                "channel_ids": channel_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.signature_response_links import SignatureResponseLinks

        d = dict(src_dict)
        field_links = SignatureResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        body = d.pop("body")

        def _parse_sender_info(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        sender_info = _parse_sender_info(d.pop("sender_info"))

        is_visible_for_all_teammate_channels = d.pop(
            "is_visible_for_all_teammate_channels"
        )

        is_default = d.pop("is_default")

        is_private = d.pop("is_private")

        def _parse_channel_ids(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                channel_ids_type_0 = cast(list[str], data)

                return channel_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None, data)

        channel_ids = _parse_channel_ids(d.pop("channel_ids"))

        signature_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            body=body,
            sender_info=sender_info,
            is_visible_for_all_teammate_channels=is_visible_for_all_teammate_channels,
            is_default=is_default,
            is_private=is_private,
            channel_ids=channel_ids,
        )

        signature_response.additional_properties = d
        return signature_response

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
