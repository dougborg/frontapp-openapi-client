from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.analytics_metric_id import AnalyticsMetricId

if TYPE_CHECKING:
    from ..models.account_ids import AccountIds
    from ..models.channel_ids import ChannelIds
    from ..models.inbox_ids import InboxIds
    from ..models.tag_ids import TagIds
    from ..models.team_ids import TeamIds
    from ..models.teammate_ids import TeammateIds


T = TypeVar("T", bound="AnalyticsReportRequest")


@_attrs_define
class AnalyticsReportRequest:
    start: float
    end: float
    metrics: list[AnalyticsMetricId]
    timezone: str | Unset = UNSET
    filters: (
        AccountIds | ChannelIds | InboxIds | TagIds | TeamIds | TeammateIds | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.channel_ids import ChannelIds
        from ..models.inbox_ids import InboxIds
        from ..models.tag_ids import TagIds
        from ..models.team_ids import TeamIds
        from ..models.teammate_ids import TeammateIds

        start = self.start

        end = self.end

        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.value
            metrics.append(metrics_item)

        timezone = self.timezone

        filters: dict[str, Any] | Unset
        if isinstance(self.filters, Unset):
            filters = UNSET
        elif isinstance(
            self.filters, (TagIds, TeammateIds, ChannelIds, InboxIds, TeamIds)
        ):
            filters = self.filters.to_dict()
        else:
            filters = self.filters.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "start": start,
                "end": end,
                "metrics": metrics,
            }
        )
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.account_ids import AccountIds
        from ..models.channel_ids import ChannelIds
        from ..models.inbox_ids import InboxIds
        from ..models.tag_ids import TagIds
        from ..models.team_ids import TeamIds
        from ..models.teammate_ids import TeammateIds

        d = dict(src_dict)
        start = d.pop("start")

        end = d.pop("end")

        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = AnalyticsMetricId(metrics_item_data)

            metrics.append(metrics_item)

        timezone = d.pop("timezone", UNSET)

        def _parse_filters(
            data: object,
        ) -> (
            AccountIds | ChannelIds | InboxIds | TagIds | TeamIds | TeammateIds | Unset
        ):
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_analytics_filters_type_0 = TagIds.from_dict(
                    cast(Mapping[str, Any], data)
                )

                return componentsschemas_analytics_filters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_analytics_filters_type_1 = TeammateIds.from_dict(
                    cast(Mapping[str, Any], data)
                )

                return componentsschemas_analytics_filters_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_analytics_filters_type_2 = ChannelIds.from_dict(
                    cast(Mapping[str, Any], data)
                )

                return componentsschemas_analytics_filters_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_analytics_filters_type_3 = InboxIds.from_dict(
                    cast(Mapping[str, Any], data)
                )

                return componentsschemas_analytics_filters_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_analytics_filters_type_4 = TeamIds.from_dict(
                    cast(Mapping[str, Any], data)
                )

                return componentsschemas_analytics_filters_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_analytics_filters_type_5 = AccountIds.from_dict(
                cast(Mapping[str, Any], data)
            )

            return componentsschemas_analytics_filters_type_5

        filters = _parse_filters(d.pop("filters", UNSET))

        analytics_report_request = cls(
            start=start,
            end=end,
            metrics=metrics,
            timezone=timezone,
            filters=filters,
        )

        analytics_report_request.additional_properties = d
        return analytics_report_request

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
