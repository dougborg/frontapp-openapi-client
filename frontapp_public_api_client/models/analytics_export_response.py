from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.analytics_export_response_status import AnalyticsExportResponseStatus

if TYPE_CHECKING:
    from ..models.account_ids import AccountIds
    from ..models.analytics_export_response_links import AnalyticsExportResponseLinks
    from ..models.channel_ids import ChannelIds
    from ..models.inbox_ids import InboxIds
    from ..models.tag_ids import TagIds
    from ..models.team_ids import TeamIds
    from ..models.teammate_ids import TeammateIds


T = TypeVar("T", bound="AnalyticsExportResponse")


@_attrs_define
class AnalyticsExportResponse:
    field_links: AnalyticsExportResponseLinks
    id: str
    status: AnalyticsExportResponseStatus
    progress: int
    filters: AccountIds | ChannelIds | InboxIds | TagIds | TeamIds | TeammateIds
    url: str | Unset = UNSET
    filename: str | Unset = UNSET
    size: float | None | Unset = UNSET
    created_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.channel_ids import ChannelIds
        from ..models.inbox_ids import InboxIds
        from ..models.tag_ids import TagIds
        from ..models.team_ids import TeamIds
        from ..models.teammate_ids import TeammateIds

        field_links = self.field_links.to_dict()

        id = self.id

        status = self.status.value

        progress = self.progress

        filters: dict[str, Any]
        if isinstance(
            self.filters, (TagIds, TeammateIds, ChannelIds, InboxIds, TeamIds)
        ):
            filters = self.filters.to_dict()
        else:
            filters = self.filters.to_dict()

        url = self.url

        filename = self.filename

        size: float | None | Unset
        if isinstance(self.size, Unset):
            size = UNSET
        else:
            size = self.size

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "status": status,
                "progress": progress,
                "filters": filters,
            }
        )
        if url is not UNSET:
            field_dict["url"] = url
        if filename is not UNSET:
            field_dict["filename"] = filename
        if size is not UNSET:
            field_dict["size"] = size
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.account_ids import AccountIds
        from ..models.analytics_export_response_links import (
            AnalyticsExportResponseLinks,
        )
        from ..models.channel_ids import ChannelIds
        from ..models.inbox_ids import InboxIds
        from ..models.tag_ids import TagIds
        from ..models.team_ids import TeamIds
        from ..models.teammate_ids import TeammateIds

        d = dict(src_dict)
        field_links = AnalyticsExportResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        status = AnalyticsExportResponseStatus(d.pop("status"))

        progress = d.pop("progress")

        def _parse_filters(
            data: object,
        ) -> AccountIds | ChannelIds | InboxIds | TagIds | TeamIds | TeammateIds:
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

        filters = _parse_filters(d.pop("filters"))

        url = d.pop("url", UNSET)

        filename = d.pop("filename", UNSET)

        def _parse_size(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        size = _parse_size(d.pop("size", UNSET))

        created_at = d.pop("created_at", UNSET)

        analytics_export_response = cls(
            field_links=field_links,
            id=id,
            status=status,
            progress=progress,
            filters=filters,
            url=url,
            filename=filename,
            size=size,
            created_at=created_at,
        )

        analytics_export_response.additional_properties = d
        return analytics_export_response

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
