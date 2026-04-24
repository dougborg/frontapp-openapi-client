from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="UpdateConversationReminders")


@_attrs_define
class UpdateConversationReminders:
    teammate_id: str
    scheduled_at: float
    status_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        teammate_id = self.teammate_id

        scheduled_at = self.scheduled_at

        status_id = self.status_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "teammate_id": teammate_id,
                "scheduled_at": scheduled_at,
            }
        )
        if status_id is not UNSET:
            field_dict["status_id"] = status_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        teammate_id = d.pop("teammate_id")

        scheduled_at = d.pop("scheduled_at")

        status_id = d.pop("status_id", UNSET)

        update_conversation_reminders = cls(
            teammate_id=teammate_id,
            scheduled_at=scheduled_at,
            status_id=status_id,
        )

        update_conversation_reminders.additional_properties = d
        return update_conversation_reminders

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
