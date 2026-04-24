from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.update_conversation_status import UpdateConversationStatus

if TYPE_CHECKING:
    from ..models.custom_field_parameter import CustomFieldParameter


T = TypeVar("T", bound="UpdateConversation")


@_attrs_define
class UpdateConversation:
    assignee_id: str | Unset = UNSET
    inbox_id: str | Unset = UNSET
    status: UpdateConversationStatus | Unset = UNSET
    status_id: str | Unset = UNSET
    tag_ids: list[str] | Unset = UNSET
    custom_fields: CustomFieldParameter | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assignee_id = self.assignee_id

        inbox_id = self.inbox_id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        status_id = self.status_id

        tag_ids: list[str] | Unset = UNSET
        if not isinstance(self.tag_ids, Unset):
            tag_ids = self.tag_ids

        custom_fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = self.custom_fields.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assignee_id is not UNSET:
            field_dict["assignee_id"] = assignee_id
        if inbox_id is not UNSET:
            field_dict["inbox_id"] = inbox_id
        if status is not UNSET:
            field_dict["status"] = status
        if status_id is not UNSET:
            field_dict["status_id"] = status_id
        if tag_ids is not UNSET:
            field_dict["tag_ids"] = tag_ids
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_field_parameter import CustomFieldParameter

        d = dict(src_dict)
        assignee_id = d.pop("assignee_id", UNSET)

        inbox_id = d.pop("inbox_id", UNSET)

        _status = d.pop("status", UNSET)
        status: UpdateConversationStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = UpdateConversationStatus(_status)

        status_id = d.pop("status_id", UNSET)

        tag_ids = cast(list[str], d.pop("tag_ids", UNSET))

        _custom_fields = d.pop("custom_fields", UNSET)
        custom_fields: CustomFieldParameter | Unset
        if isinstance(_custom_fields, Unset):
            custom_fields = UNSET
        else:
            custom_fields = CustomFieldParameter.from_dict(_custom_fields)

        update_conversation = cls(
            assignee_id=assignee_id,
            inbox_id=inbox_id,
            status=status,
            status_id=status_id,
            tag_ids=tag_ids,
            custom_fields=custom_fields,
        )

        update_conversation.additional_properties = d
        return update_conversation

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
