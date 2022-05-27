import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.endpoint_message_out_payload import EndpointMessageOutPayload
from ..models.message_status import MessageStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="EndpointMessageOut")


@attr.s(auto_attribs=True)
class EndpointMessageOut:
    """
    Attributes:
        event_type (str):  Example: user.signup.
        id (str):  Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        payload (EndpointMessageOutPayload):  Example: {'email': 'test@example.com', 'username': 'test_user'}.
        status (MessageStatus): The sending status of the message:
            - Success = 0
            - Pending = 1
            - Fail = 2
            - Sending = 3
        timestamp (datetime.datetime):
        channels (Union[Unset, List[str]]): List of free-form identifiers that endpoints can filter by Example:
            ['project_123', 'group_2'].
        event_id (Union[Unset, str]): Optional unique identifier for the message Example: evt_pNZKtWg8Azow.
        next_attempt (Union[Unset, datetime.datetime]):
    """

    event_type: str
    id: str
    payload: EndpointMessageOutPayload
    status: MessageStatus
    timestamp: datetime.datetime
    channels: Union[Unset, List[str]] = UNSET
    event_id: Union[Unset, str] = UNSET
    next_attempt: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        event_type = self.event_type
        id = self.id
        payload = self.payload
        status = self.status.value

        timestamp = self.timestamp.isoformat()

        channels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.channels, Unset):
            channels = self.channels

        event_id = self.event_id
        next_attempt: Union[Unset, str] = UNSET
        if not isinstance(self.next_attempt, Unset):
            next_attempt = self.next_attempt.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "eventType": event_type,
                "id": id,
                "payload": payload,
                "status": status,
                "timestamp": timestamp,
            }
        )
        if channels is not UNSET:
            field_dict["channels"] = channels
        if event_id is not UNSET:
            field_dict["eventId"] = event_id
        if next_attempt is not UNSET:
            field_dict["nextAttempt"] = next_attempt

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        event_type = dict_copy.pop("eventType")

        id = dict_copy.pop("id")

        payload = dict_copy.pop("payload")

        status = MessageStatus(dict_copy.pop("status"))

        timestamp = isoparse(dict_copy.pop("timestamp"))

        channels = cast(List[str], dict_copy.pop("channels", UNSET))

        event_id = dict_copy.pop("eventId", UNSET)

        _next_attempt = dict_copy.pop("nextAttempt", UNSET)
        next_attempt: Union[Unset, datetime.datetime]
        if isinstance(_next_attempt, Unset):
            next_attempt = UNSET
        else:
            next_attempt = isoparse(_next_attempt)

        endpoint_message_out = cls(
            event_type=event_type,
            id=id,
            payload=payload,
            status=status,
            timestamp=timestamp,
            channels=channels,
            event_id=event_id,
            next_attempt=next_attempt,
        )

        endpoint_message_out.additional_properties = dict_copy
        return endpoint_message_out

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
