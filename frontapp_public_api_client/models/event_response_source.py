from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_response_source_meta import EventResponseSourceMeta
    from ..models.inbox_response import InboxResponse
    from ..models.rule_response import RuleResponse
    from ..models.teammate_response import TeammateResponse


T = TypeVar("T", bound="EventResponseSource")


@_attrs_define
class EventResponseSource:
    """Event source"""

    field_meta: EventResponseSourceMeta | Unset = UNSET
    data: list[InboxResponse] | RuleResponse | TeammateResponse | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_response import RuleResponse
        from ..models.teammate_response import TeammateResponse

        field_meta: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_meta, Unset):
            field_meta = self.field_meta.to_dict()

        data: dict[str, Any] | list[dict[str, Any]] | Unset
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, (RuleResponse, TeammateResponse)):
            data = self.data.to_dict()
        else:
            data = []
            for data_type_2_item_data in self.data:
                data_type_2_item = data_type_2_item_data.to_dict()
                data.append(data_type_2_item)

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
        from ..models.event_response_source_meta import EventResponseSourceMeta
        from ..models.inbox_response import InboxResponse
        from ..models.rule_response import RuleResponse
        from ..models.teammate_response import TeammateResponse

        d = dict(src_dict)
        _field_meta = d.pop("_meta", UNSET)
        field_meta: EventResponseSourceMeta | Unset
        if isinstance(_field_meta, Unset):
            field_meta = UNSET
        else:
            field_meta = EventResponseSourceMeta.from_dict(_field_meta)

        def _parse_data(
            data: object,
        ) -> list[InboxResponse] | RuleResponse | TeammateResponse | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = RuleResponse.from_dict(cast(Mapping[str, Any], data))

                return data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_1 = TeammateResponse.from_dict(cast(Mapping[str, Any], data))

                return data_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, list):
                raise TypeError()
            data_type_2 = []
            _data_type_2 = data
            for data_type_2_item_data in _data_type_2:
                data_type_2_item = InboxResponse.from_dict(data_type_2_item_data)

                data_type_2.append(data_type_2_item)

            return data_type_2

        data = _parse_data(d.pop("data", UNSET))

        event_response_source = cls(
            field_meta=field_meta,
            data=data,
        )

        event_response_source.additional_properties = d
        return event_response_source

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
