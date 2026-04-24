from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="ConversationResponseLinksRelated")


@_attrs_define
class ConversationResponseLinksRelated:
    events: str | Unset = UNSET
    followers: str | Unset = UNSET
    messages: str | Unset = UNSET
    comments: str | Unset = UNSET
    inboxes: str | Unset = UNSET
    last_message: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        events = self.events

        followers = self.followers

        messages = self.messages

        comments = self.comments

        inboxes = self.inboxes

        last_message = self.last_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if events is not UNSET:
            field_dict["events"] = events
        if followers is not UNSET:
            field_dict["followers"] = followers
        if messages is not UNSET:
            field_dict["messages"] = messages
        if comments is not UNSET:
            field_dict["comments"] = comments
        if inboxes is not UNSET:
            field_dict["inboxes"] = inboxes
        if last_message is not UNSET:
            field_dict["last_message"] = last_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        events = d.pop("events", UNSET)

        followers = d.pop("followers", UNSET)

        messages = d.pop("messages", UNSET)

        comments = d.pop("comments", UNSET)

        inboxes = d.pop("inboxes", UNSET)

        last_message = d.pop("last_message", UNSET)

        conversation_response_links_related = cls(
            events=events,
            followers=followers,
            messages=messages,
            comments=comments,
            inboxes=inboxes,
            last_message=last_message,
        )

        conversation_response_links_related.additional_properties = d
        return conversation_response_links_related

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
