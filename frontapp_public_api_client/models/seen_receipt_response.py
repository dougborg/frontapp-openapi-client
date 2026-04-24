from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.contact_handle import ContactHandle
    from ..models.seen_receipt_response_links import SeenReceiptResponseLinks


T = TypeVar("T", bound="SeenReceiptResponse")


@_attrs_define
class SeenReceiptResponse:
    field_links: SeenReceiptResponseLinks
    first_seen_at: str
    seen_by: ContactHandle
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        first_seen_at = self.first_seen_at

        seen_by = self.seen_by.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "first_seen_at": first_seen_at,
                "seen_by": seen_by,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contact_handle import ContactHandle
        from ..models.seen_receipt_response_links import SeenReceiptResponseLinks

        d = dict(src_dict)
        field_links = SeenReceiptResponseLinks.from_dict(d.pop("_links"))

        first_seen_at = d.pop("first_seen_at")

        seen_by = ContactHandle.from_dict(d.pop("seen_by"))

        seen_receipt_response = cls(
            field_links=field_links,
            first_seen_at=first_seen_at,
            seen_by=seen_by,
        )

        seen_receipt_response.additional_properties = d
        return seen_receipt_response

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
