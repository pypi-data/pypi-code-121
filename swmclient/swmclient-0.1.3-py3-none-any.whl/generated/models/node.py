from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.node_role import NodeRole
from ..models.node_state_alloc import NodeStateAlloc
from ..models.node_state_power import NodeStatePower
from ..models.resource import Resource
from ..types import UNSET, Unset

T = TypeVar("T", bound="Node")


@attr.s(auto_attribs=True)
class Node:
    """A node information"""

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    host: Union[Unset, str] = UNSET
    api_port: Union[Unset, int] = UNSET
    state_power: Union[Unset, NodeStatePower] = UNSET
    state_alloc: Union[Unset, NodeStateAlloc] = UNSET
    resources: Union[Unset, List[Resource]] = UNSET
    roles: Union[Unset, List[NodeRole]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        host = self.host
        api_port = self.api_port
        state_power: Union[Unset, str] = UNSET
        if not isinstance(self.state_power, Unset):
            state_power = self.state_power.value

        state_alloc: Union[Unset, str] = UNSET
        if not isinstance(self.state_alloc, Unset):
            state_alloc = self.state_alloc.value

        resources: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.resources, Unset):
            resources = []
            for resources_item_data in self.resources:
                resources_item = resources_item_data.to_dict()

                resources.append(resources_item)

        roles: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = []
            for roles_item_data in self.roles:
                roles_item = roles_item_data.to_dict()

                roles.append(roles_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if host is not UNSET:
            field_dict["host"] = host
        if api_port is not UNSET:
            field_dict["api_port"] = api_port
        if state_power is not UNSET:
            field_dict["state_power"] = state_power
        if state_alloc is not UNSET:
            field_dict["state_alloc"] = state_alloc
        if resources is not UNSET:
            field_dict["resources"] = resources
        if roles is not UNSET:
            field_dict["roles"] = roles

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        host = d.pop("host", UNSET)

        api_port = d.pop("api_port", UNSET)

        _state_power = d.pop("state_power", UNSET)
        state_power: Union[Unset, NodeStatePower]
        if isinstance(_state_power, Unset):
            state_power = UNSET
        else:
            state_power = NodeStatePower(_state_power)

        _state_alloc = d.pop("state_alloc", UNSET)
        state_alloc: Union[Unset, NodeStateAlloc]
        if isinstance(_state_alloc, Unset):
            state_alloc = UNSET
        else:
            state_alloc = NodeStateAlloc(_state_alloc)

        resources = []
        _resources = d.pop("resources", UNSET)
        for resources_item_data in _resources or []:
            resources_item = Resource.from_dict(resources_item_data)

            resources.append(resources_item)

        roles = []
        _roles = d.pop("roles", UNSET)
        for roles_item_data in _roles or []:
            roles_item = NodeRole.from_dict(roles_item_data)

            roles.append(roles_item)

        node = cls(
            id=id,
            name=name,
            host=host,
            api_port=api_port,
            state_power=state_power,
            state_alloc=state_alloc,
            resources=resources,
            roles=roles,
        )

        node.additional_properties = d
        return node

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
