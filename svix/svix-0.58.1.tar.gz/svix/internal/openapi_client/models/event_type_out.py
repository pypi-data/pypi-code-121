import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.event_type_out_schemas import EventTypeOutSchemas
from ..types import UNSET, Unset

T = TypeVar("T", bound="EventTypeOut")


@attr.s(auto_attribs=True)
class EventTypeOut:
    """
    Attributes:
        created_at (datetime.datetime):
        description (str):  Example: A user has signed up.
        name (str):  Example: user.signup.
        updated_at (datetime.datetime):
        archived (Union[Unset, bool]):
        schemas (Union[Unset, EventTypeOutSchemas]): The schema for the event type for a specific version as a JSON
            schema. Example: {'1': {'description': 'An invoice was paid by a user', 'properties': {'invoiceId':
            {'description': 'The invoice id', 'type': 'string'}, 'userId': {'description': 'The user id', 'type':
            'string'}}, 'required': ['invoiceId', 'userId'], 'title': 'Invoice Paid Event', 'type': 'object'}}.
    """

    created_at: datetime.datetime
    description: str
    name: str
    updated_at: datetime.datetime
    archived: Union[Unset, bool] = False
    schemas: Union[Unset, EventTypeOutSchemas] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()

        description = self.description
        name = self.name
        updated_at = self.updated_at.isoformat()

        archived = self.archived
        schemas = self.schemas

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "description": description,
                "name": name,
                "updatedAt": updated_at,
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
        created_at = isoparse(dict_copy.pop("createdAt"))

        description = dict_copy.pop("description")

        name = dict_copy.pop("name")

        updated_at = isoparse(dict_copy.pop("updatedAt"))

        archived = dict_copy.pop("archived", UNSET)

        schemas = dict_copy.pop("schemas")

        event_type_out = cls(
            created_at=created_at,
            description=description,
            name=name,
            updated_at=updated_at,
            archived=archived,
            schemas=schemas,
        )

        event_type_out.additional_properties = dict_copy
        return event_type_out

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
