from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="EndpointIn")


@attr.s(auto_attribs=True)
class EndpointIn:
    """
    Attributes:
        url (str):  Example: https://example.com/webhook/.
        version (int):  Example: 1.
        channels (Union[Unset, List[str]]): List of message channels this endpoint listens to (omit for all) Example:
            ['project_123', 'group_2'].
        description (Union[Unset, str]):  Default: ''. Example: An example endpoint name.
        disabled (Union[Unset, bool]):
        filter_types (Union[Unset, List[str]]):  Example: ['user.signup', 'user.deleted'].
        rate_limit (Union[Unset, int]):  Example: 1000.
        secret (Union[Unset, str]): The endpoint's verification secret. If `null` is passed, a secret is automatically
            generated. Example: whsec_C2FVsBQIhrscChlQIMV+b5sSYspob7oD.
        uid (Union[Unset, str]): Optional unique identifier for the endpoint Example: unique-endpoint-identifier.
    """

    url: str
    version: int
    channels: Union[Unset, List[str]] = UNSET
    description: Union[Unset, str] = ""
    disabled: Union[Unset, bool] = False
    filter_types: Union[Unset, List[str]] = UNSET
    rate_limit: Union[Unset, int] = UNSET
    secret: Union[Unset, str] = UNSET
    uid: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        url = self.url
        version = self.version
        channels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.channels, Unset):
            channels = self.channels

        description = self.description
        disabled = self.disabled
        filter_types: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_types, Unset):
            filter_types = self.filter_types

        rate_limit = self.rate_limit
        secret = self.secret
        uid = self.uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "version": version,
            }
        )
        if channels is not UNSET:
            field_dict["channels"] = channels
        if description is not UNSET:
            field_dict["description"] = description
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if filter_types is not UNSET:
            field_dict["filterTypes"] = filter_types
        if rate_limit is not UNSET:
            field_dict["rateLimit"] = rate_limit
        if secret is not UNSET:
            field_dict["secret"] = secret
        if uid is not UNSET:
            field_dict["uid"] = uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        dict_copy = src_dict.copy()
        url = dict_copy.pop("url")

        version = dict_copy.pop("version")

        channels = cast(List[str], dict_copy.pop("channels", UNSET))

        description = dict_copy.pop("description", UNSET)

        disabled = dict_copy.pop("disabled", UNSET)

        filter_types = cast(List[str], dict_copy.pop("filterTypes", UNSET))

        rate_limit = dict_copy.pop("rateLimit", UNSET)

        secret = dict_copy.pop("secret", UNSET)

        uid = dict_copy.pop("uid", UNSET)

        endpoint_in = cls(
            url=url,
            version=version,
            channels=channels,
            description=description,
            disabled=disabled,
            filter_types=filter_types,
            rate_limit=rate_limit,
            secret=secret,
            uid=uid,
        )

        endpoint_in.additional_properties = dict_copy
        return endpoint_in

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
