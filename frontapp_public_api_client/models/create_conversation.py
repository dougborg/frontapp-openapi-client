from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset
from ..models.create_conversation_type import CreateConversationType

if TYPE_CHECKING:
    from ..models.create_conversation_comment import CreateConversationComment
    from ..models.custom_field_parameter import CustomFieldParameter


T = TypeVar("T", bound="CreateConversation")


@_attrs_define
class CreateConversation:
    type_: CreateConversationType
    subject: str
    comment: CreateConversationComment
    inbox_id: str | Unset = UNSET
    teammate_ids: list[str] | Unset = UNSET
    custom_fields: CustomFieldParameter | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        subject = self.subject

        comment = self.comment.to_dict()

        inbox_id = self.inbox_id

        teammate_ids: list[str] | Unset = UNSET
        if not isinstance(self.teammate_ids, Unset):
            teammate_ids = self.teammate_ids

        custom_fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = self.custom_fields.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "subject": subject,
                "comment": comment,
            }
        )
        if inbox_id is not UNSET:
            field_dict["inbox_id"] = inbox_id
        if teammate_ids is not UNSET:
            field_dict["teammate_ids"] = teammate_ids
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_conversation_comment import CreateConversationComment
        from ..models.custom_field_parameter import CustomFieldParameter

        d = dict(src_dict)
        type_ = CreateConversationType(d.pop("type"))

        subject = d.pop("subject")

        comment = CreateConversationComment.from_dict(d.pop("comment"))

        inbox_id = d.pop("inbox_id", UNSET)

        teammate_ids = cast(list[str], d.pop("teammate_ids", UNSET))

        _custom_fields = d.pop("custom_fields", UNSET)
        custom_fields: CustomFieldParameter | Unset
        if isinstance(_custom_fields, Unset):
            custom_fields = UNSET
        else:
            custom_fields = CustomFieldParameter.from_dict(_custom_fields)

        create_conversation = cls(
            type_=type_,
            subject=subject,
            comment=comment,
            inbox_id=inbox_id,
            teammate_ids=teammate_ids,
            custom_fields=custom_fields,
        )

        create_conversation.additional_properties = d
        return create_conversation

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
