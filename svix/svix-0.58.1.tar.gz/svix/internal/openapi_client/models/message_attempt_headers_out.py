from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.message_attempt_headers_out_sentheaders import MessageAttemptHeadersOutSentheaders

T = TypeVar("T", bound="MessageAttemptHeadersOut")


@attr.s(auto_attribs=True)
class MessageAttemptHeadersOut:
    """
    Attributes:
        sent_headers (MessageAttemptHeadersOutSentheaders):
    """

    sent_headers: MessageAttemptHeadersOutSentheaders
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        sent_headers = self.sent_headers

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sentHeaders": sent_headers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        sent_headers = dict_copy.pop("sentHeaders")

        message_attempt_headers_out = cls(
            sent_headers=sent_headers,
        )

        message_attempt_headers_out.additional_properties = dict_copy
        return message_attempt_headers_out

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
