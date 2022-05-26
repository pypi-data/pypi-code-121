import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.message_out_payload import MessageOutPayload
from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageOut")


@attr.s(auto_attribs=True)
class MessageOut:
    """
    Attributes:
        event_type (str):  Example: user.signup.
        id (str):  Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        payload (MessageOutPayload):  Example: {'email': 'test@example.com', 'username': 'test_user'}.
        timestamp (datetime.datetime):
        channels (Union[Unset, List[str]]): List of free-form identifiers that endpoints can filter by Example:
            ['project_123', 'group_2'].
        event_id (Union[Unset, str]): Optional unique identifier for the message Example: evt_pNZKtWg8Azow.
    """

    event_type: str
    id: str
    payload: MessageOutPayload
    timestamp: datetime.datetime
    channels: Union[Unset, List[str]] = UNSET
    event_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        event_type = self.event_type
        id = self.id
        payload = self.payload
        timestamp = self.timestamp.isoformat()

        channels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.channels, Unset):
            channels = self.channels

        event_id = self.event_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "eventType": event_type,
                "id": id,
                "payload": payload,
                "timestamp": timestamp,
            }
        )
        if channels is not UNSET:
            field_dict["channels"] = channels
        if event_id is not UNSET:
            field_dict["eventId"] = event_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        event_type = dict_copy.pop("eventType")

        id = dict_copy.pop("id")

        payload = dict_copy.pop("payload")

        timestamp = isoparse(dict_copy.pop("timestamp"))

        channels = cast(List[str], dict_copy.pop("channels", UNSET))

        event_id = dict_copy.pop("eventId", UNSET)

        message_out = cls(
            event_type=event_type,
            id=id,
            payload=payload,
            timestamp=timestamp,
            channels=channels,
            event_id=event_id,
        )

        message_out.additional_properties = dict_copy
        return message_out

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
