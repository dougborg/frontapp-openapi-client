from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.update_shift_color import UpdateShiftColor

if TYPE_CHECKING:
    from ..models.shift_intervals import ShiftIntervals


T = TypeVar("T", bound="UpdateShift")


@_attrs_define
class UpdateShift:
    name: str | Unset = UNSET
    color: UpdateShiftColor | Unset = UNSET
    timezone: str | Unset = UNSET
    times: ShiftIntervals | Unset = UNSET
    teammate_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        color: str | Unset = UNSET
        if not isinstance(self.color, Unset):
            color = self.color.value

        timezone = self.timezone

        times: dict[str, Any] | Unset = UNSET
        if not isinstance(self.times, Unset):
            times = self.times.to_dict()

        teammate_ids: list[str] | Unset = UNSET
        if not isinstance(self.teammate_ids, Unset):
            teammate_ids = self.teammate_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if color is not UNSET:
            field_dict["color"] = color
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if times is not UNSET:
            field_dict["times"] = times
        if teammate_ids is not UNSET:
            field_dict["teammate_ids"] = teammate_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.shift_intervals import ShiftIntervals

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _color = d.pop("color", UNSET)
        color: UpdateShiftColor | Unset
        if isinstance(_color, Unset):
            color = UNSET
        else:
            color = UpdateShiftColor(_color)

        timezone = d.pop("timezone", UNSET)

        _times = d.pop("times", UNSET)
        times: ShiftIntervals | Unset
        if isinstance(_times, Unset):
            times = UNSET
        else:
            times = ShiftIntervals.from_dict(_times)

        teammate_ids = cast(list[str], d.pop("teammate_ids", UNSET))

        update_shift = cls(
            name=name,
            color=color,
            timezone=timezone,
            times=times,
            teammate_ids=teammate_ids,
        )

        update_shift.additional_properties = d
        return update_shift

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
