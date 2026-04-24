from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.app_event_app_object import AppEventAppObject


T = TypeVar("T", bound="AppEvent")


@_attrs_define
class AppEvent:
    event_type: str
    app_object: AppEventAppObject
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_type = self.event_type

        app_object = self.app_object.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_type": event_type,
                "app_object": app_object,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.app_event_app_object import AppEventAppObject

        d = dict(src_dict)
        event_type = d.pop("event_type")

        app_object = AppEventAppObject.from_dict(d.pop("app_object"))

        app_event = cls(
            event_type=event_type,
            app_object=app_object,
        )

        app_event.additional_properties = d
        return app_event

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
