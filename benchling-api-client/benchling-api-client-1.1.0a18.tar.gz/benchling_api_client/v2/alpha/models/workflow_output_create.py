from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowOutputCreate")


@attr.s(auto_attribs=True, repr=False)
class WorkflowOutputCreate:
    """  """

    _source_output_ids: Union[Unset, List[str]] = UNSET
    _source_task_ids: Union[Unset, List[str]] = UNSET
    _workflow_task_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("source_output_ids={}".format(repr(self._source_output_ids)))
        fields.append("source_task_ids={}".format(repr(self._source_task_ids)))
        fields.append("workflow_task_id={}".format(repr(self._workflow_task_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowOutputCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        source_output_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._source_output_ids, Unset):
            source_output_ids = self._source_output_ids

        source_task_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._source_task_ids, Unset):
            source_task_ids = self._source_task_ids

        workflow_task_id = self._workflow_task_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if source_output_ids is not UNSET:
            field_dict["sourceOutputIds"] = source_output_ids
        if source_task_ids is not UNSET:
            field_dict["sourceTaskIds"] = source_task_ids
        if workflow_task_id is not UNSET:
            field_dict["workflowTaskId"] = workflow_task_id
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_source_output_ids() -> Union[Unset, List[str]]:
            source_output_ids = cast(List[str], d.pop("sourceOutputIds"))

            return source_output_ids

        source_output_ids = (
            get_source_output_ids() if "sourceOutputIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        def get_source_task_ids() -> Union[Unset, List[str]]:
            source_task_ids = cast(List[str], d.pop("sourceTaskIds"))

            return source_task_ids

        source_task_ids = (
            get_source_task_ids() if "sourceTaskIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        def get_workflow_task_id() -> Union[Unset, str]:
            workflow_task_id = d.pop("workflowTaskId")
            return workflow_task_id

        workflow_task_id = get_workflow_task_id() if "workflowTaskId" in d else cast(Union[Unset, str], UNSET)

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        workflow_output_create = cls(
            source_output_ids=source_output_ids,
            source_task_ids=source_task_ids,
            workflow_task_id=workflow_task_id,
            fields=fields,
        )

        workflow_output_create.additional_properties = d
        return workflow_output_create

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
    def source_output_ids(self) -> List[str]:
        """ The preceding workflow output IDs in the flowchart """
        if isinstance(self._source_output_ids, Unset):
            raise NotPresentError(self, "source_output_ids")
        return self._source_output_ids

    @source_output_ids.setter
    def source_output_ids(self, value: List[str]) -> None:
        self._source_output_ids = value

    @source_output_ids.deleter
    def source_output_ids(self) -> None:
        self._source_output_ids = UNSET

    @property
    def source_task_ids(self) -> List[str]:
        """ The preceding workflow task IDs in the flowchart """
        if isinstance(self._source_task_ids, Unset):
            raise NotPresentError(self, "source_task_ids")
        return self._source_task_ids

    @source_task_ids.setter
    def source_task_ids(self, value: List[str]) -> None:
        self._source_task_ids = value

    @source_task_ids.deleter
    def source_task_ids(self) -> None:
        self._source_task_ids = UNSET

    @property
    def workflow_task_id(self) -> str:
        """ The ID of the workflow task this output belogns to """
        if isinstance(self._workflow_task_id, Unset):
            raise NotPresentError(self, "workflow_task_id")
        return self._workflow_task_id

    @workflow_task_id.setter
    def workflow_task_id(self, value: str) -> None:
        self._workflow_task_id = value

    @workflow_task_id.deleter
    def workflow_task_id(self) -> None:
        self._workflow_task_id = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET
