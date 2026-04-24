from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.event_response_type import EventResponseType

if TYPE_CHECKING:
    from ..models.conversation_response import ConversationResponse
    from ..models.event_response_links import EventResponseLinks
    from ..models.event_response_source import EventResponseSource
    from ..models.event_response_target import EventResponseTarget


T = TypeVar("T", bound="EventResponse")


@_attrs_define
class EventResponse:
    """An event is created every time something interesting is happening in Front."""

    field_links: EventResponseLinks | Unset = UNSET
    id: str | Unset = UNSET
    type_: EventResponseType | Unset = UNSET
    emitted_at: float | Unset = UNSET
    source: EventResponseSource | Unset = UNSET
    target: EventResponseTarget | Unset = UNSET
    conversation: ConversationResponse | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_links, Unset):
            field_links = self.field_links.to_dict()

        id = self.id

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        emitted_at = self.emitted_at

        source: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.to_dict()

        target: dict[str, Any] | Unset = UNSET
        if not isinstance(self.target, Unset):
            target = self.target.to_dict()

        conversation: dict[str, Any] | Unset = UNSET
        if not isinstance(self.conversation, Unset):
            conversation = self.conversation.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_links is not UNSET:
            field_dict["_links"] = field_links
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if emitted_at is not UNSET:
            field_dict["emitted_at"] = emitted_at
        if source is not UNSET:
            field_dict["source"] = source
        if target is not UNSET:
            field_dict["target"] = target
        if conversation is not UNSET:
            field_dict["conversation"] = conversation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.conversation_response import ConversationResponse
        from ..models.event_response_links import EventResponseLinks
        from ..models.event_response_source import EventResponseSource
        from ..models.event_response_target import EventResponseTarget

        d = dict(src_dict)
        _field_links = d.pop("_links", UNSET)
        field_links: EventResponseLinks | Unset
        if isinstance(_field_links, Unset):
            field_links = UNSET
        else:
            field_links = EventResponseLinks.from_dict(_field_links)

        id = d.pop("id", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: EventResponseType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = EventResponseType(_type_)

        emitted_at = d.pop("emitted_at", UNSET)

        _source = d.pop("source", UNSET)
        source: EventResponseSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = EventResponseSource.from_dict(_source)

        _target = d.pop("target", UNSET)
        target: EventResponseTarget | Unset
        if isinstance(_target, Unset):
            target = UNSET
        else:
            target = EventResponseTarget.from_dict(_target)

        _conversation = d.pop("conversation", UNSET)
        conversation: ConversationResponse | Unset
        if isinstance(_conversation, Unset):
            conversation = UNSET
        else:
            conversation = ConversationResponse.from_dict(_conversation)

        event_response = cls(
            field_links=field_links,
            id=id,
            type_=type_,
            emitted_at=emitted_at,
            source=source,
            target=target,
            conversation=conversation,
        )

        event_response.additional_properties = d
        return event_response

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
