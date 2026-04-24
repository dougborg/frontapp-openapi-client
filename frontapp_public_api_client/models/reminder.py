from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.reminder_links import ReminderLinks


T = TypeVar("T", bound="Reminder")


@_attrs_define
class Reminder:
    field_links: ReminderLinks
    created_at: float | Unset = UNSET
    scheduled_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        created_at = self.created_at

        scheduled_at = self.scheduled_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if scheduled_at is not UNSET:
            field_dict["scheduled_at"] = scheduled_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reminder_links import ReminderLinks

        d = dict(src_dict)
        field_links = ReminderLinks.from_dict(d.pop("_links"))

        created_at = d.pop("created_at", UNSET)

        scheduled_at = d.pop("scheduled_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        reminder = cls(
            field_links=field_links,
            created_at=created_at,
            scheduled_at=scheduled_at,
            updated_at=updated_at,
        )

        reminder.additional_properties = d
        return reminder

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
