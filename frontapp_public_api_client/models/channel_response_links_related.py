from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="ChannelResponseLinksRelated")


@_attrs_define
class ChannelResponseLinksRelated:
    inbox: None | str | Unset = UNSET
    owner: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inbox: None | str | Unset
        if isinstance(self.inbox, Unset):
            inbox = UNSET
        else:
            inbox = self.inbox

        owner = self.owner

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if inbox is not UNSET:
            field_dict["inbox"] = inbox
        if owner is not UNSET:
            field_dict["owner"] = owner

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_inbox(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        inbox = _parse_inbox(d.pop("inbox", UNSET))

        owner = d.pop("owner", UNSET)

        channel_response_links_related = cls(
            inbox=inbox,
            owner=owner,
        )

        channel_response_links_related.additional_properties = d
        return channel_response_links_related

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
