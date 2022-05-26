from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="EndpointStats")


@attr.s(auto_attribs=True)
class EndpointStats:
    """
    Attributes:
        fail (int):
        pending (int):
        sending (int):
        success (int):
    """

    fail: int
    pending: int
    sending: int
    success: int
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        fail = self.fail
        pending = self.pending
        sending = self.sending
        success = self.success

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fail": fail,
                "pending": pending,
                "sending": sending,
                "success": success,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        fail = dict_copy.pop("fail")

        pending = dict_copy.pop("pending")

        sending = dict_copy.pop("sending")

        success = dict_copy.pop("success")

        endpoint_stats = cls(
            fail=fail,
            pending=pending,
            sending=sending,
            success=success,
        )

        endpoint_stats.additional_properties = dict_copy
        return endpoint_stats

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
