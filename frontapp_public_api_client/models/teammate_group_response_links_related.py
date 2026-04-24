from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="TeammateGroupResponseLinksRelated")


@_attrs_define
class TeammateGroupResponseLinksRelated:
    teammates: str | Unset = UNSET
    teams: str | Unset = UNSET
    inboxes: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        teammates = self.teammates

        teams = self.teams

        inboxes = self.inboxes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if teammates is not UNSET:
            field_dict["teammates"] = teammates
        if teams is not UNSET:
            field_dict["teams"] = teams
        if inboxes is not UNSET:
            field_dict["inboxes"] = inboxes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        teammates = d.pop("teammates", UNSET)

        teams = d.pop("teams", UNSET)

        inboxes = d.pop("inboxes", UNSET)

        teammate_group_response_links_related = cls(
            teammates=teammates,
            teams=teams,
            inboxes=inboxes,
        )

        teammate_group_response_links_related.additional_properties = d
        return teammate_group_response_links_related

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
