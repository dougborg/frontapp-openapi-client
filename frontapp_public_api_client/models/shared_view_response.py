from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.shared_view_response_links import SharedViewResponseLinks


T = TypeVar("T", bound="SharedViewResponse")


@_attrs_define
class SharedViewResponse:
    field_links: SharedViewResponseLinks
    id: str
    name: str
    highlight: None | str
    inbox_ids: list[str]
    tag_ids: list[str]
    not_tag_ids: list[str]
    no_tags: bool
    assignee_ids: list[str]
    not_assignee_ids: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        highlight: None | str
        highlight = self.highlight

        inbox_ids = self.inbox_ids

        tag_ids = self.tag_ids

        not_tag_ids = self.not_tag_ids

        no_tags = self.no_tags

        assignee_ids = self.assignee_ids

        not_assignee_ids = self.not_assignee_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "highlight": highlight,
                "inbox_ids": inbox_ids,
                "tag_ids": tag_ids,
                "not_tag_ids": not_tag_ids,
                "no_tags": no_tags,
                "assignee_ids": assignee_ids,
                "not_assignee_ids": not_assignee_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.shared_view_response_links import SharedViewResponseLinks

        d = dict(src_dict)
        field_links = SharedViewResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        def _parse_highlight(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        highlight = _parse_highlight(d.pop("highlight"))

        inbox_ids = cast(list[str], d.pop("inbox_ids"))

        tag_ids = cast(list[str], d.pop("tag_ids"))

        not_tag_ids = cast(list[str], d.pop("not_tag_ids"))

        no_tags = d.pop("no_tags")

        assignee_ids = cast(list[str], d.pop("assignee_ids"))

        not_assignee_ids = cast(list[str], d.pop("not_assignee_ids"))

        shared_view_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            highlight=highlight,
            inbox_ids=inbox_ids,
            tag_ids=tag_ids,
            not_tag_ids=not_tag_ids,
            no_tags=no_tags,
            assignee_ids=assignee_ids,
            not_assignee_ids=not_assignee_ids,
        )

        shared_view_response.additional_properties = d
        return shared_view_response

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
