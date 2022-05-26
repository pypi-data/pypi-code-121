import datetime
from typing import Any, Dict, List, Type, TypeVar

import attr
from dateutil.parser import isoparse

from ..models.message_attempt_trigger_type import MessageAttemptTriggerType
from ..models.message_status import MessageStatus

T = TypeVar("T", bound="MessageAttemptEndpointOut")


@attr.s(auto_attribs=True)
class MessageAttemptEndpointOut:
    """
    Attributes:
        endpoint_id (str):  Example: ep_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        id (str):  Example: atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        msg_id (str):  Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        response (str):  Example: {}.
        response_status_code (int):  Example: 200.
        status (MessageStatus): The sending status of the message:
            - Success = 0
            - Pending = 1
            - Fail = 2
            - Sending = 3
        timestamp (datetime.datetime):
        trigger_type (MessageAttemptTriggerType): The reason an attempt was made:
            - Scheduled = 0
            - Manual = 1
    """

    endpoint_id: str
    id: str
    msg_id: str
    response: str
    response_status_code: int
    status: MessageStatus
    timestamp: datetime.datetime
    trigger_type: MessageAttemptTriggerType
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        endpoint_id = self.endpoint_id
        id = self.id
        msg_id = self.msg_id
        response = self.response
        response_status_code = self.response_status_code
        status = self.status.value

        timestamp = self.timestamp.isoformat()

        trigger_type = self.trigger_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "endpointId": endpoint_id,
                "id": id,
                "msgId": msg_id,
                "response": response,
                "responseStatusCode": response_status_code,
                "status": status,
                "timestamp": timestamp,
                "triggerType": trigger_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        endpoint_id = dict_copy.pop("endpointId")

        id = dict_copy.pop("id")

        msg_id = dict_copy.pop("msgId")

        response = dict_copy.pop("response")

        response_status_code = dict_copy.pop("responseStatusCode")

        status = MessageStatus(dict_copy.pop("status"))

        timestamp = isoparse(dict_copy.pop("timestamp"))

        trigger_type = MessageAttemptTriggerType(dict_copy.pop("triggerType"))

        message_attempt_endpoint_out = cls(
            endpoint_id=endpoint_id,
            id=id,
            msg_id=msg_id,
            response=response,
            response_status_code=response_status_code,
            status=status,
            timestamp=timestamp,
            trigger_type=trigger_type,
        )

        message_attempt_endpoint_out.additional_properties = dict_copy
        return message_attempt_endpoint_out

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
