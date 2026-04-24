from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.attachment import Attachment
    from ..models.message_template_response_links import MessageTemplateResponseLinks


T = TypeVar("T", bound="MessageTemplateResponse")


@_attrs_define
class MessageTemplateResponse:
    field_links: MessageTemplateResponseLinks
    id: str
    name: str
    subject: None | str
    body: str
    attachments: list[Attachment]
    is_available_for_all_inboxes: bool
    inbox_ids: list[str] | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        subject: None | str
        subject = self.subject

        body = self.body

        attachments = []
        for attachments_item_data in self.attachments:
            attachments_item = attachments_item_data.to_dict()
            attachments.append(attachments_item)

        is_available_for_all_inboxes = self.is_available_for_all_inboxes

        inbox_ids: list[str] | None
        if isinstance(self.inbox_ids, list):
            inbox_ids = self.inbox_ids

        else:
            inbox_ids = self.inbox_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "subject": subject,
                "body": body,
                "attachments": attachments,
                "is_available_for_all_inboxes": is_available_for_all_inboxes,
                "inbox_ids": inbox_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attachment import Attachment
        from ..models.message_template_response_links import (
            MessageTemplateResponseLinks,
        )

        d = dict(src_dict)
        field_links = MessageTemplateResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        def _parse_subject(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        subject = _parse_subject(d.pop("subject"))

        body = d.pop("body")

        attachments = []
        _attachments = d.pop("attachments")
        for attachments_item_data in _attachments:
            attachments_item = Attachment.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        is_available_for_all_inboxes = d.pop("is_available_for_all_inboxes")

        def _parse_inbox_ids(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                inbox_ids_type_0 = cast(list[str], data)

                return inbox_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None, data)

        inbox_ids = _parse_inbox_ids(d.pop("inbox_ids"))

        message_template_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            subject=subject,
            body=body,
            attachments=attachments,
            is_available_for_all_inboxes=is_available_for_all_inboxes,
            inbox_ids=inbox_ids,
        )

        message_template_response.additional_properties = d
        return message_template_response

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
