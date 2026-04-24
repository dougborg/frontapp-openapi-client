from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.analytics_report_response_status import AnalyticsReportResponseStatus

if TYPE_CHECKING:
    from ..models.analytics_report_response_links import AnalyticsReportResponseLinks
    from ..models.analytics_scalar import AnalyticsScalar


T = TypeVar("T", bound="AnalyticsReportResponse")


@_attrs_define
class AnalyticsReportResponse:
    field_links: AnalyticsReportResponseLinks
    uid: str
    status: AnalyticsReportResponseStatus
    progress: int
    metrics: list[AnalyticsScalar]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        uid = self.uid

        status = self.status.value

        progress = self.progress

        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "uid": uid,
                "status": status,
                "progress": progress,
                "metrics": metrics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.analytics_report_response_links import (
            AnalyticsReportResponseLinks,
        )
        from ..models.analytics_scalar import AnalyticsScalar

        d = dict(src_dict)
        field_links = AnalyticsReportResponseLinks.from_dict(d.pop("_links"))

        uid = d.pop("uid")

        status = AnalyticsReportResponseStatus(d.pop("status"))

        progress = d.pop("progress")

        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = AnalyticsScalar.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        analytics_report_response = cls(
            field_links=field_links,
            uid=uid,
            status=status,
            progress=progress,
            metrics=metrics,
        )

        analytics_report_response.additional_properties = d
        return analytics_report_response

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
