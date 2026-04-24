from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, File, FileTypes, Unset

if TYPE_CHECKING:
    from ..models.contact_handle import ContactHandle
    from ..models.custom_field_parameter import CustomFieldParameter


T = TypeVar("T", bound="CreateContact")


@_attrs_define
class CreateContact:
    handles: list[ContactHandle]
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    avatar: File | Unset = UNSET
    links: list[str] | Unset = UNSET
    group_names: list[str] | Unset = UNSET
    list_names: list[str] | Unset = UNSET
    custom_fields: CustomFieldParameter | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        handles = []
        for handles_item_data in self.handles:
            handles_item = handles_item_data.to_dict()
            handles.append(handles_item)

        name = self.name

        description = self.description

        avatar: FileTypes | Unset = UNSET
        if not isinstance(self.avatar, Unset):
            avatar = self.avatar.to_tuple()

        links: list[str] | Unset = UNSET
        if not isinstance(self.links, Unset):
            links = self.links

        group_names: list[str] | Unset = UNSET
        if not isinstance(self.group_names, Unset):
            group_names = self.group_names

        list_names: list[str] | Unset = UNSET
        if not isinstance(self.list_names, Unset):
            list_names = self.list_names

        custom_fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = self.custom_fields.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "handles": handles,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if avatar is not UNSET:
            field_dict["avatar"] = avatar
        if links is not UNSET:
            field_dict["links"] = links
        if group_names is not UNSET:
            field_dict["group_names"] = group_names
        if list_names is not UNSET:
            field_dict["list_names"] = list_names
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contact_handle import ContactHandle
        from ..models.custom_field_parameter import CustomFieldParameter

        d = dict(src_dict)
        handles = []
        _handles = d.pop("handles")
        for handles_item_data in _handles:
            handles_item = ContactHandle.from_dict(handles_item_data)

            handles.append(handles_item)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        _avatar = d.pop("avatar", UNSET)
        avatar: File | Unset
        if isinstance(_avatar, Unset):
            avatar = UNSET
        else:
            avatar = File(payload=BytesIO(_avatar))

        links = cast(list[str], d.pop("links", UNSET))

        group_names = cast(list[str], d.pop("group_names", UNSET))

        list_names = cast(list[str], d.pop("list_names", UNSET))

        _custom_fields = d.pop("custom_fields", UNSET)
        custom_fields: CustomFieldParameter | Unset
        if isinstance(_custom_fields, Unset):
            custom_fields = UNSET
        else:
            custom_fields = CustomFieldParameter.from_dict(_custom_fields)

        create_contact = cls(
            handles=handles,
            name=name,
            description=description,
            avatar=avatar,
            links=links,
            group_names=group_names,
            list_names=list_names,
            custom_fields=custom_fields,
        )

        create_contact.additional_properties = d
        return create_contact

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
