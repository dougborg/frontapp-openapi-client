from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.account_response_links import AccountResponseLinks
    from ..models.custom_field_parameter import CustomFieldParameter


T = TypeVar("T", bound="AccountResponse")


@_attrs_define
class AccountResponse:
    field_links: AccountResponseLinks
    id: str
    name: str
    logo_url: None | str
    description: None | str
    domains: list[str]
    external_id: None | str
    custom_fields: CustomFieldParameter
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        logo_url: None | str
        logo_url = self.logo_url

        description: None | str
        description = self.description

        domains = self.domains

        external_id: None | str
        external_id = self.external_id

        custom_fields = self.custom_fields.to_dict()

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "logo_url": logo_url,
                "description": description,
                "domains": domains,
                "external_id": external_id,
                "custom_fields": custom_fields,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.account_response_links import AccountResponseLinks
        from ..models.custom_field_parameter import CustomFieldParameter

        d = dict(src_dict)
        field_links = AccountResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        def _parse_logo_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        logo_url = _parse_logo_url(d.pop("logo_url"))

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        domains = cast(list[str], d.pop("domains"))

        def _parse_external_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        external_id = _parse_external_id(d.pop("external_id"))

        custom_fields = CustomFieldParameter.from_dict(d.pop("custom_fields"))

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        account_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            logo_url=logo_url,
            description=description,
            domains=domains,
            external_id=external_id,
            custom_fields=custom_fields,
            created_at=created_at,
            updated_at=updated_at,
        )

        account_response.additional_properties = d
        return account_response

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
