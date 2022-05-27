from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="RemoteSite")


@attr.s(auto_attribs=True)
class RemoteSite:
    """A remote site information"""

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    account_id: Union[Unset, str] = UNSET
    server: Union[Unset, str] = UNSET
    port: Union[Unset, int] = UNSET
    kind: Union[Unset, str] = UNSET
    default_image_id: Union[Unset, str] = UNSET
    default_flavor_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        account_id = self.account_id
        server = self.server
        port = self.port
        kind = self.kind
        default_image_id = self.default_image_id
        default_flavor_id = self.default_flavor_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if account_id is not UNSET:
            field_dict["account_id"] = account_id
        if server is not UNSET:
            field_dict["server"] = server
        if port is not UNSET:
            field_dict["port"] = port
        if kind is not UNSET:
            field_dict["kind"] = kind
        if default_image_id is not UNSET:
            field_dict["default_image_id"] = default_image_id
        if default_flavor_id is not UNSET:
            field_dict["default_flavor_id"] = default_flavor_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        account_id = d.pop("account_id", UNSET)

        server = d.pop("server", UNSET)

        port = d.pop("port", UNSET)

        kind = d.pop("kind", UNSET)

        default_image_id = d.pop("default_image_id", UNSET)

        default_flavor_id = d.pop("default_flavor_id", UNSET)

        remote_site = cls(
            id=id,
            name=name,
            account_id=account_id,
            server=server,
            port=port,
            kind=kind,
            default_image_id=default_image_id,
            default_flavor_id=default_flavor_id,
        )

        remote_site.additional_properties = d
        return remote_site

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
