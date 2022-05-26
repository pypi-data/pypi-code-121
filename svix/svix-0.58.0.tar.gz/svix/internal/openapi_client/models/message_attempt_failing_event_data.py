from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.message_attempt_failed_data import MessageAttemptFailedData
from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageAttemptFailingEventData")


@attr.s(auto_attribs=True)
class MessageAttemptFailingEventData:
    """
    Attributes:
        app_id (str):  Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        endpoint_id (str):  Example: ep_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        last_attempt (MessageAttemptFailedData):
        msg_id (str):  Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        app_uid (Union[Unset, str]): Optional unique identifier for the application Example: unique-app-identifier.
    """

    app_id: str
    endpoint_id: str
    last_attempt: MessageAttemptFailedData
    msg_id: str
    app_uid: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        app_id = self.app_id
        endpoint_id = self.endpoint_id
        last_attempt = self.last_attempt.to_dict()

        msg_id = self.msg_id
        app_uid = self.app_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "appId": app_id,
                "endpointId": endpoint_id,
                "lastAttempt": last_attempt,
                "msgId": msg_id,
            }
        )
        if app_uid is not UNSET:
            field_dict["appUid"] = app_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        app_id = dict_copy.pop("appId")

        endpoint_id = dict_copy.pop("endpointId")

        last_attempt = MessageAttemptFailedData.from_dict(dict_copy.pop("lastAttempt"))

        msg_id = dict_copy.pop("msgId")

        app_uid = dict_copy.pop("appUid", UNSET)

        message_attempt_failing_event_data = cls(
            app_id=app_id,
            endpoint_id=endpoint_id,
            last_attempt=last_attempt,
            msg_id=msg_id,
            app_uid=app_uid,
        )

        message_attempt_failing_event_data.additional_properties = dict_copy
        return message_attempt_failing_event_data

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
