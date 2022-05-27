from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AttemptStatisticsData")


@attr.s(auto_attribs=True)
class AttemptStatisticsData:
    """
    Attributes:
        failure_count (Union[Unset, List[int]]):
        success_count (Union[Unset, List[int]]):
    """

    failure_count: Union[Unset, List[int]] = UNSET
    success_count: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        failure_count: Union[Unset, List[int]] = UNSET
        if not isinstance(self.failure_count, Unset):
            failure_count = self.failure_count

        success_count: Union[Unset, List[int]] = UNSET
        if not isinstance(self.success_count, Unset):
            success_count = self.success_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if failure_count is not UNSET:
            field_dict["failureCount"] = failure_count
        if success_count is not UNSET:
            field_dict["successCount"] = success_count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        failure_count = cast(List[int], dict_copy.pop("failureCount", UNSET))

        success_count = cast(List[int], dict_copy.pop("successCount", UNSET))

        attempt_statistics_data = cls(
            failure_count=failure_count,
            success_count=success_count,
        )

        attempt_statistics_data.additional_properties = dict_copy
        return attempt_statistics_data

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
