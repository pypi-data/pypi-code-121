from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.event_type_in_schemas import EventTypeInSchemas
from ..types import UNSET, Unset

T = TypeVar("T", bound="EventTypeIn")


@attr.s(auto_attribs=True)
class EventTypeIn:
    """
    Attributes:
        description (str):  Example: A user has signed up.
        name (str):  Example: user.signup.
        archived (Union[Unset, bool]):
        schemas (Union[Unset, EventTypeInSchemas]): The schema for the event type for a specific version as a JSON
            schema. Example: {'1': {'description': 'An invoice was paid by a user', 'properties': {'invoiceId':
            {'description': 'The invoice id', 'type': 'string'}, 'userId': {'description': 'The user id', 'type':
            'string'}}, 'required': ['invoiceId', 'userId'], 'title': 'Invoice Paid Event', 'type': 'object'}}.
    """

    description: str
    name: str
    archived: Union[Unset, bool] = False
    schemas: Union[Unset, EventTypeInSchemas] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        description = self.description
        name = self.name
        archived = self.archived
        schemas = self.schemas

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "name": name,
            }
        )
        if archived is not UNSET:
            field_dict["archived"] = archived
        if schemas is not UNSET:
            field_dict["schemas"] = schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        description = dict_copy.pop("description")

        name = dict_copy.pop("name")

        archived = dict_copy.pop("archived", UNSET)

        schemas = dict_copy.pop("schemas")

        event_type_in = cls(
            description=description,
            name=name,
            archived=archived,
            schemas=schemas,
        )

        event_type_in.additional_properties = dict_copy
        return event_type_in

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
