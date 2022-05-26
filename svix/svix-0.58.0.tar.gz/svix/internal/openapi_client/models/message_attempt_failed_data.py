import datetime
from typing import Any, Dict, List, Type, TypeVar

import attr
from dateutil.parser import isoparse

T = TypeVar("T", bound="MessageAttemptFailedData")


@attr.s(auto_attribs=True)
class MessageAttemptFailedData:
    """
    Attributes:
        id (str):  Example: atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        response_status_code (int):  Example: 500.
        timestamp (datetime.datetime):
    """

    id: str
    response_status_code: int
    timestamp: datetime.datetime
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        response_status_code = self.response_status_code
        timestamp = self.timestamp.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "responseStatusCode": response_status_code,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        id = dict_copy.pop("id")

        response_status_code = dict_copy.pop("responseStatusCode")

        timestamp = isoparse(dict_copy.pop("timestamp"))

        message_attempt_failed_data = cls(
            id=id,
            response_status_code=response_status_code,
            timestamp=timestamp,
        )

        message_attempt_failed_data.additional_properties = dict_copy
        return message_attempt_failed_data

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
