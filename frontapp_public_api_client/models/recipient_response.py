from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.recipient_response_role import RecipientResponseRole

if TYPE_CHECKING:
    from ..models.recipient_response_links import RecipientResponseLinks


T = TypeVar("T", bound="RecipientResponse")


@_attrs_define
class RecipientResponse:
    field_links: RecipientResponseLinks
    name: None | str
    handle: str
    role: RecipientResponseRole
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        name: None | str
        name = self.name

        handle = self.handle

        role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "name": name,
                "handle": handle,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recipient_response_links import RecipientResponseLinks

        d = dict(src_dict)
        field_links = RecipientResponseLinks.from_dict(d.pop("_links"))

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        handle = d.pop("handle")

        role = RecipientResponseRole(d.pop("role"))

        recipient_response = cls(
            field_links=field_links,
            name=name,
            handle=handle,
            role=role,
        )

        recipient_response.additional_properties = d
        return recipient_response

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
