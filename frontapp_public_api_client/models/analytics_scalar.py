from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.analytics_metric_id import AnalyticsMetricId
from ..models.analytics_scalar_type import AnalyticsScalarType

if TYPE_CHECKING:
    from ..models.analytics_scalar_value_type_2 import AnalyticsScalarValueType2


T = TypeVar("T", bound="AnalyticsScalar")


@_attrs_define
class AnalyticsScalar:
    id: AnalyticsMetricId
    type_: AnalyticsScalarType
    value: AnalyticsScalarValueType2 | int | None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.analytics_scalar_value_type_2 import AnalyticsScalarValueType2

        id = self.id.value

        type_ = self.type_.value

        value: dict[str, Any] | int | None | str
        if isinstance(self.value, AnalyticsScalarValueType2):
            value = self.value.to_dict()
        else:
            value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.analytics_scalar_value_type_2 import AnalyticsScalarValueType2

        d = dict(src_dict)
        id = AnalyticsMetricId(d.pop("id"))

        type_ = AnalyticsScalarType(d.pop("type"))

        def _parse_value(data: object) -> AnalyticsScalarValueType2 | int | None | str:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_analytics_scalar_value_type_2 = (
                    AnalyticsScalarValueType2.from_dict(cast(Mapping[str, Any], data))
                )

                return componentsschemas_analytics_scalar_value_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AnalyticsScalarValueType2 | int | None | str, data)

        value = _parse_value(d.pop("value"))

        analytics_scalar = cls(
            id=id,
            type_=type_,
            value=value,
        )

        analytics_scalar.additional_properties = d
        return analytics_scalar

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
