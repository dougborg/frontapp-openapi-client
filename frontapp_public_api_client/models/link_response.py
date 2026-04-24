from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.custom_field_parameter import CustomFieldParameter
    from ..models.link_response_links import LinkResponseLinks


T = TypeVar("T", bound="LinkResponse")


@_attrs_define
class LinkResponse:
    """A link used to connect a Front conversation to an external resource."""

    field_links: LinkResponseLinks
    id: str
    name: str
    type_: str
    external_url: str
    custom_fields: CustomFieldParameter
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        type_ = self.type_

        external_url = self.external_url

        custom_fields = self.custom_fields.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "type": type_,
                "external_url": external_url,
                "custom_fields": custom_fields,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_field_parameter import CustomFieldParameter
        from ..models.link_response_links import LinkResponseLinks

        d = dict(src_dict)
        field_links = LinkResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        type_ = d.pop("type")

        external_url = d.pop("external_url")

        custom_fields = CustomFieldParameter.from_dict(d.pop("custom_fields"))

        link_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            type_=type_,
            external_url=external_url,
            custom_fields=custom_fields,
        )

        link_response.additional_properties = d
        return link_response

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
