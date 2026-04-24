from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contact_handle import ContactHandle
    from ..models.contact_list_responses import ContactListResponses
    from ..models.contact_response_links import ContactResponseLinks
    from ..models.custom_field_parameter import CustomFieldParameter


T = TypeVar("T", bound="ContactResponse")


@_attrs_define
class ContactResponse:
    field_links: ContactResponseLinks | Unset = UNSET
    id: str | Unset = UNSET
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    avatar_url: str | Unset = UNSET
    links: list[str] | Unset = UNSET
    groups: list[ContactListResponses] | Unset = UNSET
    lists: list[ContactListResponses] | Unset = UNSET
    handles: list[ContactHandle] | Unset = UNSET
    custom_fields: CustomFieldParameter | Unset = UNSET
    is_private: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_links, Unset):
            field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        description = self.description

        avatar_url = self.avatar_url

        links: list[str] | Unset = UNSET
        if not isinstance(self.links, Unset):
            links = self.links

        groups: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()
                groups.append(groups_item)

        lists: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.lists, Unset):
            lists = []
            for lists_item_data in self.lists:
                lists_item = lists_item_data.to_dict()
                lists.append(lists_item)

        handles: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.handles, Unset):
            handles = []
            for handles_item_data in self.handles:
                handles_item = handles_item_data.to_dict()
                handles.append(handles_item)

        custom_fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = self.custom_fields.to_dict()

        is_private = self.is_private

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_links is not UNSET:
            field_dict["_links"] = field_links
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if avatar_url is not UNSET:
            field_dict["avatar_url"] = avatar_url
        if links is not UNSET:
            field_dict["links"] = links
        if groups is not UNSET:
            field_dict["groups"] = groups
        if lists is not UNSET:
            field_dict["lists"] = lists
        if handles is not UNSET:
            field_dict["handles"] = handles
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields
        if is_private is not UNSET:
            field_dict["is_private"] = is_private

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contact_handle import ContactHandle
        from ..models.contact_list_responses import ContactListResponses
        from ..models.contact_response_links import ContactResponseLinks
        from ..models.custom_field_parameter import CustomFieldParameter

        d = dict(src_dict)
        _field_links = d.pop("_links", UNSET)
        field_links: ContactResponseLinks | Unset
        if isinstance(_field_links, Unset):
            field_links = UNSET
        else:
            field_links = ContactResponseLinks.from_dict(_field_links)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        avatar_url = d.pop("avatar_url", UNSET)

        links = cast(list[str], d.pop("links", UNSET))

        _groups = d.pop("groups", UNSET)
        groups: list[ContactListResponses] | Unset = UNSET
        if _groups is not UNSET:
            groups = []
            for groups_item_data in _groups:
                groups_item = ContactListResponses.from_dict(groups_item_data)

                groups.append(groups_item)

        _lists = d.pop("lists", UNSET)
        lists: list[ContactListResponses] | Unset = UNSET
        if _lists is not UNSET:
            lists = []
            for lists_item_data in _lists:
                lists_item = ContactListResponses.from_dict(lists_item_data)

                lists.append(lists_item)

        _handles = d.pop("handles", UNSET)
        handles: list[ContactHandle] | Unset = UNSET
        if _handles is not UNSET:
            handles = []
            for handles_item_data in _handles:
                handles_item = ContactHandle.from_dict(handles_item_data)

                handles.append(handles_item)

        _custom_fields = d.pop("custom_fields", UNSET)
        custom_fields: CustomFieldParameter | Unset
        if isinstance(_custom_fields, Unset):
            custom_fields = UNSET
        else:
            custom_fields = CustomFieldParameter.from_dict(_custom_fields)

        is_private = d.pop("is_private", UNSET)

        contact_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            description=description,
            avatar_url=avatar_url,
            links=links,
            groups=groups,
            lists=lists,
            handles=handles,
            custom_fields=custom_fields,
            is_private=is_private,
        )

        contact_response.additional_properties = d
        return contact_response

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
