from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.teammate_response_type import TeammateResponseType

if TYPE_CHECKING:
    from ..models.custom_field_parameter import CustomFieldParameter
    from ..models.teammate_response_links import TeammateResponseLinks


T = TypeVar("T", bound="TeammateResponse")


@_attrs_define
class TeammateResponse:
    """A teammate is a user in Front."""

    field_links: TeammateResponseLinks
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    is_admin: bool
    is_available: bool
    is_blocked: bool
    type_: TeammateResponseType
    custom_fields: CustomFieldParameter
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        email = self.email

        username = self.username

        first_name = self.first_name

        last_name = self.last_name

        is_admin = self.is_admin

        is_available = self.is_available

        is_blocked = self.is_blocked

        type_ = self.type_.value

        custom_fields = self.custom_fields.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "email": email,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "is_admin": is_admin,
                "is_available": is_available,
                "is_blocked": is_blocked,
                "type": type_,
                "custom_fields": custom_fields,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_field_parameter import CustomFieldParameter
        from ..models.teammate_response_links import TeammateResponseLinks

        d = dict(src_dict)
        field_links = TeammateResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        email = d.pop("email")

        username = d.pop("username")

        first_name = d.pop("first_name")

        last_name = d.pop("last_name")

        is_admin = d.pop("is_admin")

        is_available = d.pop("is_available")

        is_blocked = d.pop("is_blocked")

        type_ = TeammateResponseType(d.pop("type"))

        custom_fields = CustomFieldParameter.from_dict(d.pop("custom_fields"))

        teammate_response = cls(
            field_links=field_links,
            id=id,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
            is_available=is_available,
            is_blocked=is_blocked,
            type_=type_,
            custom_fields=custom_fields,
        )

        teammate_response.additional_properties = d
        return teammate_response

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
