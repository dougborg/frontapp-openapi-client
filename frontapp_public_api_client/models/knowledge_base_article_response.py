from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment import Attachment
    from ..models.knowledge_base_article_response_links import (
        KnowledgeBaseArticleResponseLinks,
    )


T = TypeVar("T", bound="KnowledgeBaseArticleResponse")


@_attrs_define
class KnowledgeBaseArticleResponse:
    field_links: KnowledgeBaseArticleResponseLinks
    id: str
    slug: str
    name: str
    status: str
    keywords: list[str]
    content: str
    locale: str
    attachments: list[Attachment]
    last_edited_at: float | Unset = UNSET
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        slug = self.slug

        name = self.name

        status = self.status

        keywords = self.keywords

        content = self.content

        locale = self.locale

        attachments = []
        for attachments_item_data in self.attachments:
            attachments_item = attachments_item_data.to_dict()
            attachments.append(attachments_item)

        last_edited_at = self.last_edited_at

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "slug": slug,
                "name": name,
                "status": status,
                "keywords": keywords,
                "content": content,
                "locale": locale,
                "attachments": attachments,
            }
        )
        if last_edited_at is not UNSET:
            field_dict["last_edited_at"] = last_edited_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attachment import Attachment
        from ..models.knowledge_base_article_response_links import (
            KnowledgeBaseArticleResponseLinks,
        )

        d = dict(src_dict)
        field_links = KnowledgeBaseArticleResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        slug = d.pop("slug")

        name = d.pop("name")

        status = d.pop("status")

        keywords = cast(list[str], d.pop("keywords"))

        content = d.pop("content")

        locale = d.pop("locale")

        attachments = []
        _attachments = d.pop("attachments")
        for attachments_item_data in _attachments:
            attachments_item = Attachment.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        last_edited_at = d.pop("last_edited_at", UNSET)

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        knowledge_base_article_response = cls(
            field_links=field_links,
            id=id,
            slug=slug,
            name=name,
            status=status,
            keywords=keywords,
            content=content,
            locale=locale,
            attachments=attachments,
            last_edited_at=last_edited_at,
            created_at=created_at,
            updated_at=updated_at,
        )

        knowledge_base_article_response.additional_properties = d
        return knowledge_base_article_response

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
