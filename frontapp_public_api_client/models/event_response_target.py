from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.comment_response import CommentResponse
    from ..models.event_response_target_meta import EventResponseTargetMeta
    from ..models.inbox_response import InboxResponse
    from ..models.link_response import LinkResponse
    from ..models.message_response import MessageResponse
    from ..models.tag_response import TagResponse
    from ..models.teammate_response import TeammateResponse


T = TypeVar("T", bound="EventResponseTarget")


@_attrs_define
class EventResponseTarget:
    """Partial representation (type & id) of the event's target"""

    field_meta: EventResponseTargetMeta | Unset = UNSET
    data: (
        CommentResponse
        | InboxResponse
        | LinkResponse
        | MessageResponse
        | TagResponse
        | TeammateResponse
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.comment_response import CommentResponse
        from ..models.inbox_response import InboxResponse
        from ..models.message_response import MessageResponse
        from ..models.tag_response import TagResponse
        from ..models.teammate_response import TeammateResponse

        field_meta: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_meta, Unset):
            field_meta = self.field_meta.to_dict()

        data: dict[str, Any] | Unset
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(
            self.data,
            (
                TeammateResponse,
                InboxResponse,
                TagResponse,
                CommentResponse,
                MessageResponse,
            ),
        ):
            data = self.data.to_dict()
        else:
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_meta is not UNSET:
            field_dict["_meta"] = field_meta
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.comment_response import CommentResponse
        from ..models.event_response_target_meta import EventResponseTargetMeta
        from ..models.inbox_response import InboxResponse
        from ..models.link_response import LinkResponse
        from ..models.message_response import MessageResponse
        from ..models.tag_response import TagResponse
        from ..models.teammate_response import TeammateResponse

        d = dict(src_dict)
        _field_meta = d.pop("_meta", UNSET)
        field_meta: EventResponseTargetMeta | Unset
        if isinstance(_field_meta, Unset):
            field_meta = UNSET
        else:
            field_meta = EventResponseTargetMeta.from_dict(_field_meta)

        def _parse_data(
            data: object,
        ) -> (
            CommentResponse
            | InboxResponse
            | LinkResponse
            | MessageResponse
            | TagResponse
            | TeammateResponse
            | Unset
        ):
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = TeammateResponse.from_dict(cast(Mapping[str, Any], data))

                return data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_1 = InboxResponse.from_dict(cast(Mapping[str, Any], data))

                return data_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_2 = TagResponse.from_dict(cast(Mapping[str, Any], data))

                return data_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_3 = CommentResponse.from_dict(cast(Mapping[str, Any], data))

                return data_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_4 = MessageResponse.from_dict(cast(Mapping[str, Any], data))

                return data_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            data_type_5 = LinkResponse.from_dict(cast(Mapping[str, Any], data))

            return data_type_5

        data = _parse_data(d.pop("data", UNSET))

        event_response_target = cls(
            field_meta=field_meta,
            data=data,
        )

        event_response_target.additional_properties = d
        return event_response_target

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
