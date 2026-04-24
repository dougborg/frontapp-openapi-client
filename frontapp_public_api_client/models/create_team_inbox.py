from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_field_parameter import CustomFieldParameter


T = TypeVar("T", bound="CreateTeamInbox")


@_attrs_define
class CreateTeamInbox:
    name: str
    teammate_ids: list[str] | Unset = UNSET
    is_public: bool | Unset = UNSET
    custom_fields: CustomFieldParameter | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        teammate_ids: list[str] | Unset = UNSET
        if not isinstance(self.teammate_ids, Unset):
            teammate_ids = self.teammate_ids

        is_public = self.is_public

        custom_fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = self.custom_fields.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if teammate_ids is not UNSET:
            field_dict["teammate_ids"] = teammate_ids
        if is_public is not UNSET:
            field_dict["is_public"] = is_public
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_field_parameter import CustomFieldParameter

        d = dict(src_dict)
        name = d.pop("name")

        teammate_ids = cast(list[str], d.pop("teammate_ids", UNSET))

        is_public = d.pop("is_public", UNSET)

        _custom_fields = d.pop("custom_fields", UNSET)
        custom_fields: CustomFieldParameter | Unset
        if isinstance(_custom_fields, Unset):
            custom_fields = UNSET
        else:
            custom_fields = CustomFieldParameter.from_dict(_custom_fields)

        create_team_inbox = cls(
            name=name,
            teammate_ids=teammate_ids,
            is_public=is_public,
            custom_fields=custom_fields,
        )

        create_team_inbox.additional_properties = d
        return create_team_inbox

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
