from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="CreateComment")


@_attrs_define
class CreateComment:
    body: str
    author_id: str | Unset = UNSET
    is_pinned: bool | Unset = UNSET
    attachments: list[File] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        body = self.body

        author_id = self.author_id

        is_pinned = self.is_pinned

        attachments: list[FileTypes] | Unset = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_tuple()

                attachments.append(attachments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "body": body,
            }
        )
        if author_id is not UNSET:
            field_dict["author_id"] = author_id
        if is_pinned is not UNSET:
            field_dict["is_pinned"] = is_pinned
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        body = d.pop("body")

        author_id = d.pop("author_id", UNSET)

        is_pinned = d.pop("is_pinned", UNSET)

        _attachments = d.pop("attachments", UNSET)
        attachments: list[File] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = File(payload=BytesIO(attachments_item_data))

                attachments.append(attachments_item)

        create_comment = cls(
            body=body,
            author_id=author_id,
            is_pinned=is_pinned,
            attachments=attachments,
        )

        create_comment.additional_properties = d
        return create_comment

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
