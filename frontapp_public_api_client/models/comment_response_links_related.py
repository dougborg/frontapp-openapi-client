from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="CommentResponseLinksRelated")


@_attrs_define
class CommentResponseLinksRelated:
    conversation: str | Unset = UNSET
    mentions: str | Unset = UNSET
    comment_replied_to: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conversation = self.conversation

        mentions = self.mentions

        comment_replied_to: None | str | Unset
        if isinstance(self.comment_replied_to, Unset):
            comment_replied_to = UNSET
        else:
            comment_replied_to = self.comment_replied_to

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if conversation is not UNSET:
            field_dict["conversation"] = conversation
        if mentions is not UNSET:
            field_dict["mentions"] = mentions
        if comment_replied_to is not UNSET:
            field_dict["comment_replied_to"] = comment_replied_to

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        conversation = d.pop("conversation", UNSET)

        mentions = d.pop("mentions", UNSET)

        def _parse_comment_replied_to(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        comment_replied_to = _parse_comment_replied_to(
            d.pop("comment_replied_to", UNSET)
        )

        comment_response_links_related = cls(
            conversation=conversation,
            mentions=mentions,
            comment_replied_to=comment_replied_to,
        )

        comment_response_links_related.additional_properties = d
        return comment_response_links_related

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
