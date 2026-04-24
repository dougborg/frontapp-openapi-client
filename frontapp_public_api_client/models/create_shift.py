from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.create_shift_color import CreateShiftColor

if TYPE_CHECKING:
    from ..models.shift_intervals import ShiftIntervals


T = TypeVar("T", bound="CreateShift")


@_attrs_define
class CreateShift:
    name: str
    color: CreateShiftColor
    timezone: str
    times: ShiftIntervals
    teammate_ids: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        color = self.color.value

        timezone = self.timezone

        times = self.times.to_dict()

        teammate_ids = self.teammate_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "color": color,
                "timezone": timezone,
                "times": times,
                "teammate_ids": teammate_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.shift_intervals import ShiftIntervals

        d = dict(src_dict)
        name = d.pop("name")

        color = CreateShiftColor(d.pop("color"))

        timezone = d.pop("timezone")

        times = ShiftIntervals.from_dict(d.pop("times"))

        teammate_ids = cast(list[str], d.pop("teammate_ids"))

        create_shift = cls(
            name=name,
            color=color,
            timezone=timezone,
            times=times,
            teammate_ids=teammate_ids,
        )

        create_shift.additional_properties = d
        return create_shift

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
