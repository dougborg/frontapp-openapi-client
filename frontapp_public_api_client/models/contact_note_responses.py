from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contact_note_responses_links import ContactNoteResponsesLinks
    from ..models.teammate_response import TeammateResponse


T = TypeVar("T", bound="ContactNoteResponses")


@_attrs_define
class ContactNoteResponses:
    field_links: ContactNoteResponsesLinks
    author: TeammateResponse
    body: str
    created_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        author = self.author.to_dict()

        body = self.body

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "author": author,
                "body": body,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contact_note_responses_links import ContactNoteResponsesLinks
        from ..models.teammate_response import TeammateResponse

        d = dict(src_dict)
        field_links = ContactNoteResponsesLinks.from_dict(d.pop("_links"))

        author = TeammateResponse.from_dict(d.pop("author"))

        body = d.pop("body")

        created_at = d.pop("created_at", UNSET)

        contact_note_responses = cls(
            field_links=field_links,
            author=author,
            body=body,
            created_at=created_at,
        )

        contact_note_responses.additional_properties = d
        return contact_note_responses

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
