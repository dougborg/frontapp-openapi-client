from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.analytics_activities_columns import AnalyticsActivitiesColumns

T = TypeVar("T", bound="AnalyticsActivitiesExportsColumns")


@_attrs_define
class AnalyticsActivitiesExportsColumns:
    columns: list[AnalyticsActivitiesColumns | str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        columns = []
        for columns_item_data in self.columns:
            columns_item: str
            if isinstance(columns_item_data, AnalyticsActivitiesColumns):
                columns_item = columns_item_data.value
            else:
                columns_item = columns_item_data
            columns.append(columns_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "columns": columns,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        columns = []
        _columns = d.pop("columns")
        for columns_item_data in _columns:

            def _parse_columns_item(data: object) -> AnalyticsActivitiesColumns | str:
                try:
                    if not isinstance(data, str):
                        raise TypeError()
                    columns_item_type_0 = AnalyticsActivitiesColumns(data)

                    return columns_item_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                return cast(AnalyticsActivitiesColumns | str, data)

            columns_item = _parse_columns_item(columns_item_data)

            columns.append(columns_item)

        analytics_activities_exports_columns = cls(
            columns=columns,
        )

        analytics_activities_exports_columns.additional_properties = d
        return analytics_activities_exports_columns

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
