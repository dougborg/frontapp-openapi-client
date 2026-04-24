from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..client_types import UNSET, Unset

T = TypeVar("T", bound="MessageTemplateFolderResponseLinksRelated")


@_attrs_define
class MessageTemplateFolderResponseLinksRelated:
    owner: None | str | Unset = UNSET
    parent_folder: None | str | Unset = UNSET
    child_folders: None | str | Unset = UNSET
    child_answers: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        owner: None | str | Unset
        if isinstance(self.owner, Unset):
            owner = UNSET
        else:
            owner = self.owner

        parent_folder: None | str | Unset
        if isinstance(self.parent_folder, Unset):
            parent_folder = UNSET
        else:
            parent_folder = self.parent_folder

        child_folders: None | str | Unset
        if isinstance(self.child_folders, Unset):
            child_folders = UNSET
        else:
            child_folders = self.child_folders

        child_answers: None | str | Unset
        if isinstance(self.child_answers, Unset):
            child_answers = UNSET
        else:
            child_answers = self.child_answers

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if owner is not UNSET:
            field_dict["owner"] = owner
        if parent_folder is not UNSET:
            field_dict["parent_folder"] = parent_folder
        if child_folders is not UNSET:
            field_dict["child_folders"] = child_folders
        if child_answers is not UNSET:
            field_dict["child_answers"] = child_answers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_owner(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        owner = _parse_owner(d.pop("owner", UNSET))

        def _parse_parent_folder(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_folder = _parse_parent_folder(d.pop("parent_folder", UNSET))

        def _parse_child_folders(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        child_folders = _parse_child_folders(d.pop("child_folders", UNSET))

        def _parse_child_answers(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        child_answers = _parse_child_answers(d.pop("child_answers", UNSET))

        message_template_folder_response_links_related = cls(
            owner=owner,
            parent_folder=parent_folder,
            child_folders=child_folders,
            child_answers=child_answers,
        )

        message_template_folder_response_links_related.additional_properties = d
        return message_template_folder_response_links_related

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
