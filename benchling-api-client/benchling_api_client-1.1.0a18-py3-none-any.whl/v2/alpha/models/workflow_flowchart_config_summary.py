from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowFlowchartConfigSummary")


@attr.s(auto_attribs=True, repr=False)
class WorkflowFlowchartConfigSummary:
    """  """

    _flowchart_config_version_ids: Union[Unset, List[str]] = UNSET
    _id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("flowchart_config_version_ids={}".format(repr(self._flowchart_config_version_ids)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowFlowchartConfigSummary({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        flowchart_config_version_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._flowchart_config_version_ids, Unset):
            flowchart_config_version_ids = self._flowchart_config_version_ids

        id = self._id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if flowchart_config_version_ids is not UNSET:
            field_dict["flowchartConfigVersionIds"] = flowchart_config_version_ids
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_flowchart_config_version_ids() -> Union[Unset, List[str]]:
            flowchart_config_version_ids = cast(List[str], d.pop("flowchartConfigVersionIds"))

            return flowchart_config_version_ids

        flowchart_config_version_ids = (
            get_flowchart_config_version_ids()
            if "flowchartConfigVersionIds" in d
            else cast(Union[Unset, List[str]], UNSET)
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        workflow_flowchart_config_summary = cls(
            flowchart_config_version_ids=flowchart_config_version_ids,
            id=id,
        )

        workflow_flowchart_config_summary.additional_properties = d
        return workflow_flowchart_config_summary

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
    def flowchart_config_version_ids(self) -> List[str]:
        """ The ID of all the versions of this flowchart config sorted chronologically from most recent (current) version to the least recent one """
        if isinstance(self._flowchart_config_version_ids, Unset):
            raise NotPresentError(self, "flowchart_config_version_ids")
        return self._flowchart_config_version_ids

    @flowchart_config_version_ids.setter
    def flowchart_config_version_ids(self, value: List[str]) -> None:
        self._flowchart_config_version_ids = value

    @flowchart_config_version_ids.deleter
    def flowchart_config_version_ids(self) -> None:
        self._flowchart_config_version_ids = UNSET

    @property
    def id(self) -> str:
        """ The ID of the workflow flowchart config """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET
