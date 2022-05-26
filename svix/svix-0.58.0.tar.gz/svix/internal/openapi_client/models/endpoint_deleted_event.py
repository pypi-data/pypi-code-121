from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.endpoint_deleted_event_data import EndpointDeletedEventData
from ..models.endpoint_deleted_event_type import EndpointDeletedEventType
from ..types import UNSET, Unset

T = TypeVar("T", bound="EndpointDeletedEvent")


@attr.s(auto_attribs=True)
class EndpointDeletedEvent:
    """Sent when an endpoint is deleted.

    Example:
        {'data': {'appId': 'app_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'appUid': 'unique-app-identifier', 'endpointId':
            'ep_1srOrx2ZWZBpBUvZwXKQmoEYga2'}, 'type': 'endpoint.deleted'}

    Attributes:
        data (EndpointDeletedEventData):
        type (Union[Unset, EndpointDeletedEventType]):  Default: EndpointDeletedEventType.ENDPOINT_DELETED.
    """

    data: EndpointDeletedEventData
    type: Union[Unset, EndpointDeletedEventType] = EndpointDeletedEventType.ENDPOINT_DELETED
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.data.to_dict()

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        data = EndpointDeletedEventData.from_dict(dict_copy.pop("data"))

        _type = dict_copy.pop("type", UNSET)
        type: Union[Unset, EndpointDeletedEventType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = EndpointDeletedEventType(_type)

        endpoint_deleted_event = cls(
            data=data,
            type=type,
        )

        endpoint_deleted_event.additional_properties = dict_copy
        return endpoint_deleted_event

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
