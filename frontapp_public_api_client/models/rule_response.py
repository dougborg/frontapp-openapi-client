from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.rule_response_links import RuleResponseLinks


T = TypeVar("T", bound="RuleResponse")


@_attrs_define
class RuleResponse:
    field_links: RuleResponseLinks
    id: str
    name: str
    actions: list[str]
    is_private: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_links = self.field_links.to_dict()

        id = self.id

        name = self.name

        actions = self.actions

        is_private = self.is_private

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_links": field_links,
                "id": id,
                "name": name,
                "actions": actions,
                "is_private": is_private,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rule_response_links import RuleResponseLinks

        d = dict(src_dict)
        field_links = RuleResponseLinks.from_dict(d.pop("_links"))

        id = d.pop("id")

        name = d.pop("name")

        actions = cast(list[str], d.pop("actions"))

        is_private = d.pop("is_private")

        rule_response = cls(
            field_links=field_links,
            id=id,
            name=name,
            actions=actions,
            is_private=is_private,
        )

        rule_response.additional_properties = d
        return rule_response

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
