from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.inbox_response import InboxResponse
    from ..models.team_response_links import TeamResponseLinks
    from ..models.teammate_response import TeammateResponse


T = TypeVar("T", bound="TeamResponse")


@_attrs_define
class TeamResponse:
    field_links: TeamResponseLinks
    id: str
    name: str
    inboxes: list[InboxResponse]
    members: list[TeammateResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        inboxes = []
        for inboxes_item_data in self.inboxes:
            inboxes_item = inboxes_item_data.to_dict()
            inboxes.append(inboxes_item)

        members = []
        for members_item_data in self.members:
            members_item = members_item_data.to_dict()
            members.append(members_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "inboxes": inboxes,
                "members": members,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.inbox_response import InboxResponse
        from ..models.team_response_links import TeamResponseLinks
        from ..models.teammate_response import TeammateResponse

        d = dict(src_dict)
        field_links = TeamResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        inboxes = []
        _inboxes = d.pop("inboxes")
        for inboxes_item_data in _inboxes:
            inboxes_item = InboxResponse.from_dict(inboxes_item_data)

            inboxes.append(inboxes_item)

        members = []
        _members = d.pop("members")
        for members_item_data in _members:
            members_item = TeammateResponse.from_dict(members_item_data)

            members.append(members_item)

        team_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            inboxes=inboxes,
            members=members,
        )

        team_response.additional_properties = d
        return team_response

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
