from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="UpdateView")


@_attrs_define
class UpdateView:
    name: str | Unset = UNSET
    inbox_ids: list[str] | Unset = UNSET
    tag_ids: list[str] | Unset = UNSET
    not_tag_ids: list[str] | Unset = UNSET
    no_tags: bool | Unset = UNSET
    assignee_ids: list[str] | Unset = UNSET
    not_assignee_ids: list[str] | Unset = UNSET
    highlight: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        inbox_ids: list[str] | Unset = UNSET
        if not isinstance(self.inbox_ids, Unset):
            inbox_ids = self.inbox_ids

        tag_ids: list[str] | Unset = UNSET
        if not isinstance(self.tag_ids, Unset):
            tag_ids = self.tag_ids

        not_tag_ids: list[str] | Unset = UNSET
        if not isinstance(self.not_tag_ids, Unset):
            not_tag_ids = self.not_tag_ids

        no_tags = self.no_tags

        assignee_ids: list[str] | Unset = UNSET
        if not isinstance(self.assignee_ids, Unset):
            assignee_ids = self.assignee_ids

        not_assignee_ids: list[str] | Unset = UNSET
        if not isinstance(self.not_assignee_ids, Unset):
            not_assignee_ids = self.not_assignee_ids

        highlight = self.highlight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if inbox_ids is not UNSET:
            field_dict["inbox_ids"] = inbox_ids
        if tag_ids is not UNSET:
            field_dict["tag_ids"] = tag_ids
        if not_tag_ids is not UNSET:
            field_dict["not_tag_ids"] = not_tag_ids
        if no_tags is not UNSET:
            field_dict["no_tags"] = no_tags
        if assignee_ids is not UNSET:
            field_dict["assignee_ids"] = assignee_ids
        if not_assignee_ids is not UNSET:
            field_dict["not_assignee_ids"] = not_assignee_ids
        if highlight is not UNSET:
            field_dict["highlight"] = highlight

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        inbox_ids = cast(list[str], d.pop("inbox_ids", UNSET))

        tag_ids = cast(list[str], d.pop("tag_ids", UNSET))

        not_tag_ids = cast(list[str], d.pop("not_tag_ids", UNSET))

        no_tags = d.pop("no_tags", UNSET)

        assignee_ids = cast(list[str], d.pop("assignee_ids", UNSET))

        not_assignee_ids = cast(list[str], d.pop("not_assignee_ids", UNSET))

        highlight = d.pop("highlight", UNSET)

        update_view = cls(
            name=name,
            inbox_ids=inbox_ids,
            tag_ids=tag_ids,
            not_tag_ids=not_tag_ids,
            no_tags=no_tags,
            assignee_ids=assignee_ids,
            not_assignee_ids=not_assignee_ids,
            highlight=highlight,
        )

        update_view.additional_properties = d
        return update_view

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
