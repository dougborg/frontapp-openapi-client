from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment import Attachment
    from ..models.comment_response_links import CommentResponseLinks
    from ..models.teammate_response import TeammateResponse


T = TypeVar("T", bound="CommentResponse")


@_attrs_define
class CommentResponse:
    field_links: CommentResponseLinks
    id: str
    author: TeammateResponse
    body: str
    attachments: list[Attachment]
    is_pinned: bool
    posted_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        author = self.author.to_dict()

        body = self.body

        attachments = []
        for attachments_item_data in self.attachments:
            attachments_item = attachments_item_data.to_dict()
            attachments.append(attachments_item)

        is_pinned = self.is_pinned

        posted_at = self.posted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "author": author,
                "body": body,
                "attachments": attachments,
                "is_pinned": is_pinned,
            }
        )
        if posted_at is not UNSET:
            field_dict["posted_at"] = posted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attachment import Attachment
        from ..models.comment_response_links import CommentResponseLinks
        from ..models.teammate_response import TeammateResponse

        d = dict(src_dict)
        field_links = CommentResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        author = TeammateResponse.from_dict(d.pop("author"))

        body = d.pop("body")

        attachments = []
        _attachments = d.pop("attachments")
        for attachments_item_data in _attachments:
            attachments_item = Attachment.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        is_pinned = d.pop("is_pinned")

        posted_at = d.pop("posted_at", UNSET)

        comment_response = cls(
            field_links=field_links,
            id=id,
            author=author,
            body=body,
            attachments=attachments,
            is_pinned=is_pinned,
            posted_at=posted_at,
        )

        comment_response.additional_properties = d
        return comment_response

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
