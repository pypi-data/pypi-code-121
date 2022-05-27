from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.message_attempt_failing_event_data import MessageAttemptFailingEventData
from ..models.message_attempt_failing_event_type import MessageAttemptFailingEventType
from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageAttemptFailingEvent")


@attr.s(auto_attribs=True)
class MessageAttemptFailingEvent:
    """Sent after a message has been failing for a few times.
    It's sent on the fourth failure. It complements `message.attempt.exhausted` which is sent after the last failure.

        Example:
            {'data': {'appId': 'app_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'appUid': 'unique-app-identifier', 'endpointId':
                'ep_1srOrx2ZWZBpBUvZwXKQmoEYga2', 'lastAttempt': {'id': 'atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2',
                'responseStatusCode': 500, 'timestamp': '1970-01-01T00:00:00'}, 'msgId': 'msg_1srOrx2ZWZBpBUvZwXKQmoEYga2'},
                'type': 'message.attempt.failing'}

        Attributes:
            data (MessageAttemptFailingEventData):
            type (Union[Unset, MessageAttemptFailingEventType]):  Default:
                MessageAttemptFailingEventType.MESSAGE_ATTEMPT_FAILING.
    """

    data: MessageAttemptFailingEventData
    type: Union[Unset, MessageAttemptFailingEventType] = MessageAttemptFailingEventType.MESSAGE_ATTEMPT_FAILING
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
        data = MessageAttemptFailingEventData.from_dict(dict_copy.pop("data"))

        _type = dict_copy.pop("type", UNSET)
        type: Union[Unset, MessageAttemptFailingEventType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = MessageAttemptFailingEventType(_type)

        message_attempt_failing_event = cls(
            data=data,
            type=type,
        )

        message_attempt_failing_event.additional_properties = dict_copy
        return message_attempt_failing_event

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
