from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.shift_interval import ShiftInterval


T = TypeVar("T", bound="ShiftIntervals")


@_attrs_define
class ShiftIntervals:
    mon: ShiftInterval | Unset = UNSET
    tue: ShiftInterval | Unset = UNSET
    wed: ShiftInterval | Unset = UNSET
    thu: ShiftInterval | Unset = UNSET
    fri: ShiftInterval | Unset = UNSET
    sat: ShiftInterval | Unset = UNSET
    sun: ShiftInterval | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.mon, Unset):
            mon = self.mon.to_dict()

        tue: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tue, Unset):
            tue = self.tue.to_dict()

        wed: dict[str, Any] | Unset = UNSET
        if not isinstance(self.wed, Unset):
            wed = self.wed.to_dict()

        thu: dict[str, Any] | Unset = UNSET
        if not isinstance(self.thu, Unset):
            thu = self.thu.to_dict()

        fri: dict[str, Any] | Unset = UNSET
        if not isinstance(self.fri, Unset):
            fri = self.fri.to_dict()

        sat: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sat, Unset):
            sat = self.sat.to_dict()

        sun: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sun, Unset):
            sun = self.sun.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mon is not UNSET:
            field_dict["mon"] = mon
        if tue is not UNSET:
            field_dict["tue"] = tue
        if wed is not UNSET:
            field_dict["wed"] = wed
        if thu is not UNSET:
            field_dict["thu"] = thu
        if fri is not UNSET:
            field_dict["fri"] = fri
        if sat is not UNSET:
            field_dict["sat"] = sat
        if sun is not UNSET:
            field_dict["sun"] = sun

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.shift_interval import ShiftInterval

        d = dict(src_dict)
        _mon = d.pop("mon", UNSET)
        mon: ShiftInterval | Unset
        if isinstance(_mon, Unset):
            mon = UNSET
        else:
            mon = ShiftInterval.from_dict(_mon)

        _tue = d.pop("tue", UNSET)
        tue: ShiftInterval | Unset
        if isinstance(_tue, Unset):
            tue = UNSET
        else:
            tue = ShiftInterval.from_dict(_tue)

        _wed = d.pop("wed", UNSET)
        wed: ShiftInterval | Unset
        if isinstance(_wed, Unset):
            wed = UNSET
        else:
            wed = ShiftInterval.from_dict(_wed)

        _thu = d.pop("thu", UNSET)
        thu: ShiftInterval | Unset
        if isinstance(_thu, Unset):
            thu = UNSET
        else:
            thu = ShiftInterval.from_dict(_thu)

        _fri = d.pop("fri", UNSET)
        fri: ShiftInterval | Unset
        if isinstance(_fri, Unset):
            fri = UNSET
        else:
            fri = ShiftInterval.from_dict(_fri)

        _sat = d.pop("sat", UNSET)
        sat: ShiftInterval | Unset
        if isinstance(_sat, Unset):
            sat = UNSET
        else:
            sat = ShiftInterval.from_dict(_sat)

        _sun = d.pop("sun", UNSET)
        sun: ShiftInterval | Unset
        if isinstance(_sun, Unset):
            sun = UNSET
        else:
            sun = ShiftInterval.from_dict(_sun)

        shift_intervals = cls(
            mon=mon,
            tue=tue,
            wed=wed,
            thu=thu,
            fri=fri,
            sat=sat,
            sun=sun,
        )

        shift_intervals.additional_properties = d
        return shift_intervals

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
