from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message_response_metadata_headers import (
        MessageResponseMetadataHeaders,
    )


T = TypeVar("T", bound="MessageResponseMetadata")


@_attrs_define
class MessageResponseMetadata:
    """Optional metadata about the message"""

    intercom_url: str | Unset = UNSET
    duration: int | Unset = UNSET
    have_been_answered: bool | Unset = UNSET
    external_id: str | Unset = UNSET
    twitter_url: str | Unset = UNSET
    is_retweet: bool | Unset = UNSET
    have_been_retweeted: bool | Unset = UNSET
    have_been_favorited: bool | Unset = UNSET
    thread_ref: str | Unset = UNSET
    headers: MessageResponseMetadataHeaders | Unset = UNSET
    chat_visitor_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        intercom_url = self.intercom_url

        duration = self.duration

        have_been_answered = self.have_been_answered

        external_id = self.external_id

        twitter_url = self.twitter_url

        is_retweet = self.is_retweet

        have_been_retweeted = self.have_been_retweeted

        have_been_favorited = self.have_been_favorited

        thread_ref = self.thread_ref

        headers: dict[str, Any] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        chat_visitor_url = self.chat_visitor_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if intercom_url is not UNSET:
            field_dict["intercom_url"] = intercom_url
        if duration is not UNSET:
            field_dict["duration"] = duration
        if have_been_answered is not UNSET:
            field_dict["have_been_answered"] = have_been_answered
        if external_id is not UNSET:
            field_dict["external_id"] = external_id
        if twitter_url is not UNSET:
            field_dict["twitter_url"] = twitter_url
        if is_retweet is not UNSET:
            field_dict["is_retweet"] = is_retweet
        if have_been_retweeted is not UNSET:
            field_dict["have_been_retweeted"] = have_been_retweeted
        if have_been_favorited is not UNSET:
            field_dict["have_been_favorited"] = have_been_favorited
        if thread_ref is not UNSET:
            field_dict["thread_ref"] = thread_ref
        if headers is not UNSET:
            field_dict["headers"] = headers
        if chat_visitor_url is not UNSET:
            field_dict["chat_visitor_url"] = chat_visitor_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message_response_metadata_headers import (
            MessageResponseMetadataHeaders,
        )

        d = dict(src_dict)
        intercom_url = d.pop("intercom_url", UNSET)

        duration = d.pop("duration", UNSET)

        have_been_answered = d.pop("have_been_answered", UNSET)

        external_id = d.pop("external_id", UNSET)

        twitter_url = d.pop("twitter_url", UNSET)

        is_retweet = d.pop("is_retweet", UNSET)

        have_been_retweeted = d.pop("have_been_retweeted", UNSET)

        have_been_favorited = d.pop("have_been_favorited", UNSET)

        thread_ref = d.pop("thread_ref", UNSET)

        _headers = d.pop("headers", UNSET)
        headers: MessageResponseMetadataHeaders | Unset
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = MessageResponseMetadataHeaders.from_dict(_headers)

        chat_visitor_url = d.pop("chat_visitor_url", UNSET)

        message_response_metadata = cls(
            intercom_url=intercom_url,
            duration=duration,
            have_been_answered=have_been_answered,
            external_id=external_id,
            twitter_url=twitter_url,
            is_retweet=is_retweet,
            have_been_retweeted=have_been_retweeted,
            have_been_favorited=have_been_favorited,
            thread_ref=thread_ref,
            headers=headers,
            chat_visitor_url=chat_visitor_url,
        )

        message_response_metadata.additional_properties = d
        return message_response_metadata

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
