from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApplicationIn")


@attr.s(auto_attribs=True)
class ApplicationIn:
    """
    Attributes:
        name (str):  Example: My first application.
        rate_limit (Union[Unset, int]):  Example: 1000.
        uid (Union[Unset, str]): Optional unique identifier for the application Example: unique-app-identifier.
    """

    name: str
    rate_limit: Union[Unset, int] = UNSET
    uid: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        rate_limit = self.rate_limit
        uid = self.uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if rate_limit is not UNSET:
            field_dict["rateLimit"] = rate_limit
        if uid is not UNSET:
            field_dict["uid"] = uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        name = dict_copy.pop("name")

        rate_limit = dict_copy.pop("rateLimit", UNSET)

        uid = dict_copy.pop("uid", UNSET)

        application_in = cls(
            name=name,
            rate_limit=rate_limit,
            uid=uid,
        )

        application_in.additional_properties = dict_copy
        return application_in

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
