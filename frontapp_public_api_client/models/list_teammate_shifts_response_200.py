from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.list_teammate_shifts_response_200_links import (
        ListTeammateShiftsResponse200Links,
    )
    from ..models.shift_response import ShiftResponse


T = TypeVar("T", bound="ListTeammateShiftsResponse200")


@_attrs_define
class ListTeammateShiftsResponse200:
    field_links: ListTeammateShiftsResponse200Links | Unset = UNSET
    field_results: list[ShiftResponse] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_links, Unset):
            field_links = self.field_links.to_dict()

        field_results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.field_results, Unset):
            field_results = []
            for field_results_item_data in self.field_results:
                field_results_item = field_results_item_data.to_dict()
                field_results.append(field_results_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_links is not UNSET:
            field_dict["_links"] = field_links
        if field_results is not UNSET:
            field_dict["_results"] = field_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_teammate_shifts_response_200_links import (
            ListTeammateShiftsResponse200Links,
        )
        from ..models.shift_response import ShiftResponse

        d = dict(src_dict)
        _field_links = d.pop("_links", UNSET)
        field_links: ListTeammateShiftsResponse200Links | Unset
        if isinstance(_field_links, Unset):
            field_links = UNSET
        else:
            field_links = ListTeammateShiftsResponse200Links.from_dict(_field_links)

        _field_results = d.pop("_results", UNSET)
        field_results: list[ShiftResponse] | Unset = UNSET
        if _field_results is not UNSET:
            field_results = []
            for field_results_item_data in _field_results:
                field_results_item = ShiftResponse.from_dict(field_results_item_data)

                field_results.append(field_results_item)

        list_teammate_shifts_response_200 = cls(
            field_links=field_links,
            field_results=field_results,
        )

        list_teammate_shifts_response_200.additional_properties = d
        return list_teammate_shifts_response_200

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
