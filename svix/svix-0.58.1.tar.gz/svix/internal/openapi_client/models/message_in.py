from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.message_in_payload import MessageInPayload
from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageIn")


@attr.s(auto_attribs=True)
class MessageIn:
    """
    Attributes:
        event_type (str):  Example: user.signup.
        payload (MessageInPayload):  Example: {'email': 'test@example.com', 'username': 'test_user'}.
        channels (Union[Unset, List[str]]): List of free-form identifiers that endpoints can filter by Example:
            ['project_123', 'group_2'].
        event_id (Union[Unset, str]): Optional unique identifier for the message Example: evt_pNZKtWg8Azow.
        payload_retention_period (Union[Unset, int]): The retention period for the payload (in days). Default: 90.
            Example: 90.
    """

    event_type: str
    payload: MessageInPayload
    channels: Union[Unset, List[str]] = UNSET
    event_id: Union[Unset, str] = UNSET
    payload_retention_period: Union[Unset, int] = 90
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        event_type = self.event_type
        payload = self.payload
        channels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.channels, Unset):
            channels = self.channels

        event_id = self.event_id
        payload_retention_period = self.payload_retention_period

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "eventType": event_type,
                "payload": payload,
            }
        )
        if channels is not UNSET:
            field_dict["channels"] = channels
        if event_id is not UNSET:
            field_dict["eventId"] = event_id
        if payload_retention_period is not UNSET:
            field_dict["payloadRetentionPeriod"] = payload_retention_period

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        event_type = dict_copy.pop("eventType")

        payload = dict_copy.pop("payload")

        channels = cast(List[str], dict_copy.pop("channels", UNSET))

        event_id = dict_copy.pop("eventId", UNSET)

        payload_retention_period = dict_copy.pop("payloadRetentionPeriod", UNSET)

        message_in = cls(
            event_type=event_type,
            payload=payload,
            channels=channels,
            event_id=event_id,
            payload_retention_period=payload_retention_period,
        )

        message_in.additional_properties = dict_copy
        return message_in

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
