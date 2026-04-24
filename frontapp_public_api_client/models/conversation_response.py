from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.conversation_response_status import ConversationResponseStatus
from ..models.conversation_response_status_category import (
    ConversationResponseStatusCategory,
)

if TYPE_CHECKING:
    from ..models.conversation_response_links import ConversationResponseLinks
    from ..models.conversation_response_metadata import ConversationResponseMetadata
    from ..models.custom_field_parameter import CustomFieldParameter
    from ..models.link_response import LinkResponse
    from ..models.recipient_response import RecipientResponse
    from ..models.reminder import Reminder
    from ..models.tag_response import TagResponse
    from ..models.teammate_response import TeammateResponse


T = TypeVar("T", bound="ConversationResponse")


@_attrs_define
class ConversationResponse:
    field_links: ConversationResponseLinks
    id: str
    subject: str
    status: ConversationResponseStatus
    ticket_ids: list[str]
    assignee: TeammateResponse
    recipient: RecipientResponse
    tags: list[TagResponse]
    links: list[LinkResponse]
    custom_fields: CustomFieldParameter
    is_private: bool
    scheduled_reminders: list[Reminder]
    metadata: ConversationResponseMetadata
    status_id: str | Unset = UNSET
    status_category: ConversationResponseStatusCategory | Unset = UNSET
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    waiting_since: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        subject = self.subject

        status = self.status.value

        ticket_ids = self.ticket_ids

        assignee = self.assignee.to_dict()

        recipient = self.recipient.to_dict()

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        links = []
        for links_item_data in self.links:
            links_item = links_item_data.to_dict()
            links.append(links_item)

        custom_fields = self.custom_fields.to_dict()

        is_private = self.is_private

        scheduled_reminders = []
        for scheduled_reminders_item_data in self.scheduled_reminders:
            scheduled_reminders_item = scheduled_reminders_item_data.to_dict()
            scheduled_reminders.append(scheduled_reminders_item)

        metadata = self.metadata.to_dict()

        status_id = self.status_id

        status_category: str | Unset = UNSET
        if not isinstance(self.status_category, Unset):
            status_category = self.status_category.value

        created_at = self.created_at

        updated_at = self.updated_at

        waiting_since = self.waiting_since

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "subject": subject,
                "status": status,
                "ticket_ids": ticket_ids,
                "assignee": assignee,
                "recipient": recipient,
                "tags": tags,
                "links": links,
                "custom_fields": custom_fields,
                "is_private": is_private,
                "scheduled_reminders": scheduled_reminders,
                "metadata": metadata,
            }
        )
        if status_id is not UNSET:
            field_dict["status_id"] = status_id
        if status_category is not UNSET:
            field_dict["status_category"] = status_category
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if waiting_since is not UNSET:
            field_dict["waiting_since"] = waiting_since

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.conversation_response_links import ConversationResponseLinks
        from ..models.conversation_response_metadata import ConversationResponseMetadata
        from ..models.custom_field_parameter import CustomFieldParameter
        from ..models.link_response import LinkResponse
        from ..models.recipient_response import RecipientResponse
        from ..models.reminder import Reminder
        from ..models.tag_response import TagResponse
        from ..models.teammate_response import TeammateResponse

        d = dict(src_dict)
        field_links = ConversationResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        subject = d.pop("subject")

        status = ConversationResponseStatus(d.pop("status"))

        ticket_ids = cast(list[str], d.pop("ticket_ids"))

        assignee = TeammateResponse.from_dict(d.pop("assignee"))

        recipient = RecipientResponse.from_dict(d.pop("recipient"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = TagResponse.from_dict(tags_item_data)

            tags.append(tags_item)

        links = []
        _links = d.pop("links")
        for links_item_data in _links:
            links_item = LinkResponse.from_dict(links_item_data)

            links.append(links_item)

        custom_fields = CustomFieldParameter.from_dict(d.pop("custom_fields"))

        is_private = d.pop("is_private")

        scheduled_reminders = []
        _scheduled_reminders = d.pop("scheduled_reminders")
        for scheduled_reminders_item_data in _scheduled_reminders:
            scheduled_reminders_item = Reminder.from_dict(scheduled_reminders_item_data)

            scheduled_reminders.append(scheduled_reminders_item)

        metadata = ConversationResponseMetadata.from_dict(d.pop("metadata"))

        status_id = d.pop("status_id", UNSET)

        _status_category = d.pop("status_category", UNSET)
        status_category: ConversationResponseStatusCategory | Unset
        if isinstance(_status_category, Unset):
            status_category = UNSET
        else:
            status_category = ConversationResponseStatusCategory(_status_category)

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        waiting_since = d.pop("waiting_since", UNSET)

        conversation_response = cls(
            field_links=field_links,
            id=id,
            subject=subject,
            status=status,
            ticket_ids=ticket_ids,
            assignee=assignee,
            recipient=recipient,
            tags=tags,
            links=links,
            custom_fields=custom_fields,
            is_private=is_private,
            scheduled_reminders=scheduled_reminders,
            metadata=metadata,
            status_id=status_id,
            status_category=status_category,
            created_at=created_at,
            updated_at=updated_at,
            waiting_since=waiting_since,
        )

        conversation_response.additional_properties = d
        return conversation_response

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
