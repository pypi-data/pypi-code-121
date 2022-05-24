from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_flowchart_edge_config import WorkflowFlowchartEdgeConfig
from ..models.workflow_flowchart_node_config import WorkflowFlowchartNodeConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowFlowchart")


@attr.s(auto_attribs=True, repr=False)
class WorkflowFlowchart:
    """  """

    _edge_configs: Union[Unset, List[WorkflowFlowchartEdgeConfig]] = UNSET
    _id: Union[Unset, str] = UNSET
    _node_configs: Union[Unset, List[WorkflowFlowchartNodeConfig]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("edge_configs={}".format(repr(self._edge_configs)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("node_configs={}".format(repr(self._node_configs)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowFlowchart({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        edge_configs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._edge_configs, Unset):
            edge_configs = []
            for edge_configs_item_data in self._edge_configs:
                edge_configs_item = edge_configs_item_data.to_dict()

                edge_configs.append(edge_configs_item)

        id = self._id
        node_configs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._node_configs, Unset):
            node_configs = []
            for node_configs_item_data in self._node_configs:
                node_configs_item = node_configs_item_data.to_dict()

                node_configs.append(node_configs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if edge_configs is not UNSET:
            field_dict["edgeConfigs"] = edge_configs
        if id is not UNSET:
            field_dict["id"] = id
        if node_configs is not UNSET:
            field_dict["nodeConfigs"] = node_configs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_edge_configs() -> Union[Unset, List[WorkflowFlowchartEdgeConfig]]:
            edge_configs = []
            _edge_configs = d.pop("edgeConfigs")
            for edge_configs_item_data in _edge_configs or []:
                edge_configs_item = WorkflowFlowchartEdgeConfig.from_dict(edge_configs_item_data)

                edge_configs.append(edge_configs_item)

            return edge_configs

        edge_configs = (
            get_edge_configs()
            if "edgeConfigs" in d
            else cast(Union[Unset, List[WorkflowFlowchartEdgeConfig]], UNSET)
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_node_configs() -> Union[Unset, List[WorkflowFlowchartNodeConfig]]:
            node_configs = []
            _node_configs = d.pop("nodeConfigs")
            for node_configs_item_data in _node_configs or []:
                node_configs_item = WorkflowFlowchartNodeConfig.from_dict(node_configs_item_data)

                node_configs.append(node_configs_item)

            return node_configs

        node_configs = (
            get_node_configs()
            if "nodeConfigs" in d
            else cast(Union[Unset, List[WorkflowFlowchartNodeConfig]], UNSET)
        )

        workflow_flowchart = cls(
            edge_configs=edge_configs,
            id=id,
            node_configs=node_configs,
        )

        workflow_flowchart.additional_properties = d
        return workflow_flowchart

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def edge_configs(self) -> List[WorkflowFlowchartEdgeConfig]:
        """ Edge configs in this flowchart """
        if isinstance(self._edge_configs, Unset):
            raise NotPresentError(self, "edge_configs")
        return self._edge_configs

    @edge_configs.setter
    def edge_configs(self, value: List[WorkflowFlowchartEdgeConfig]) -> None:
        self._edge_configs = value

    @edge_configs.deleter
    def edge_configs(self) -> None:
        self._edge_configs = UNSET

    @property
    def id(self) -> str:
        """ The ID of the flowchart """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def node_configs(self) -> List[WorkflowFlowchartNodeConfig]:
        """ Node configs in this flowchart """
        if isinstance(self._node_configs, Unset):
            raise NotPresentError(self, "node_configs")
        return self._node_configs

    @node_configs.setter
    def node_configs(self, value: List[WorkflowFlowchartNodeConfig]) -> None:
        self._node_configs = value

    @node_configs.deleter
    def node_configs(self) -> None:
        self._node_configs = UNSET
