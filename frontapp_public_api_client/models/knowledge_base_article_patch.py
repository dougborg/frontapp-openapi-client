from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.knowledge_base_article_patch_status import KnowledgeBaseArticlePatchStatus

T = TypeVar("T", bound="KnowledgeBaseArticlePatch")


@_attrs_define
class KnowledgeBaseArticlePatch:
    author_id: str | Unset = UNSET
    subject: str | Unset = UNSET
    content: str | Unset = UNSET
    status: KnowledgeBaseArticlePatchStatus | Unset = (
        KnowledgeBaseArticlePatchStatus.DRAFT
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        author_id = self.author_id

        subject = self.subject

        content = self.content

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if author_id is not UNSET:
            field_dict["author_id"] = author_id
        if subject is not UNSET:
            field_dict["subject"] = subject
        if content is not UNSET:
            field_dict["content"] = content
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        author_id = d.pop("author_id", UNSET)

        subject = d.pop("subject", UNSET)

        content = d.pop("content", UNSET)

        _status = d.pop("status", UNSET)
        status: KnowledgeBaseArticlePatchStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = KnowledgeBaseArticlePatchStatus(_status)

        knowledge_base_article_patch = cls(
            author_id=author_id,
            subject=subject,
            content=content,
            status=status,
        )

        knowledge_base_article_patch.additional_properties = d
        return knowledge_base_article_patch

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
