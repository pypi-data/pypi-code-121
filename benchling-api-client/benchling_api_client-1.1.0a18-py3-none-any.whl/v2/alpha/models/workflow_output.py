from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.creation_origin import CreationOrigin
from ..models.fields import Fields
from ..models.workflow_output_summary import WorkflowOutputSummary
from ..models.workflow_task_group_summary import WorkflowTaskGroupSummary
from ..models.workflow_task_summary import WorkflowTaskSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowOutput")


@attr.s(auto_attribs=True, repr=False)
class WorkflowOutput:
    """  """

    _next_outputs: Union[Unset, List[WorkflowOutputSummary]] = UNSET
    _next_tasks: Union[Unset, List[WorkflowTaskSummary]] = UNSET
    _source_outputs: Union[Unset, List[WorkflowOutputSummary]] = UNSET
    _source_tasks: Union[Unset, List[WorkflowTaskSummary]] = UNSET
    _creation_origin: Union[Unset, CreationOrigin] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _task: Union[Unset, WorkflowTaskSummary] = UNSET
    _web_url: Union[Unset, str] = UNSET
    _workflow_task_group: Union[Unset, WorkflowTaskGroupSummary] = UNSET
    _display_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_outputs={}".format(repr(self._next_outputs)))
        fields.append("next_tasks={}".format(repr(self._next_tasks)))
        fields.append("source_outputs={}".format(repr(self._source_outputs)))
        fields.append("source_tasks={}".format(repr(self._source_tasks)))
        fields.append("creation_origin={}".format(repr(self._creation_origin)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("task={}".format(repr(self._task)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("workflow_task_group={}".format(repr(self._workflow_task_group)))
        fields.append("display_id={}".format(repr(self._display_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowOutput({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_outputs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._next_outputs, Unset):
            next_outputs = []
            for next_outputs_item_data in self._next_outputs:
                next_outputs_item = next_outputs_item_data.to_dict()

                next_outputs.append(next_outputs_item)

        next_tasks: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._next_tasks, Unset):
            next_tasks = []
            for next_tasks_item_data in self._next_tasks:
                next_tasks_item = next_tasks_item_data.to_dict()

                next_tasks.append(next_tasks_item)

        source_outputs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._source_outputs, Unset):
            source_outputs = []
            for source_outputs_item_data in self._source_outputs:
                source_outputs_item = source_outputs_item_data.to_dict()

                source_outputs.append(source_outputs_item)

        source_tasks: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._source_tasks, Unset):
            source_tasks = []
            for source_tasks_item_data in self._source_tasks:
                source_tasks_item = source_tasks_item_data.to_dict()

                source_tasks.append(source_tasks_item)

        creation_origin: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creation_origin, Unset):
            creation_origin = self._creation_origin.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._task, Unset):
            task = self._task.to_dict()

        web_url = self._web_url
        workflow_task_group: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._workflow_task_group, Unset):
            workflow_task_group = self._workflow_task_group.to_dict()

        display_id = self._display_id
        id = self._id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_outputs is not UNSET:
            field_dict["nextOutputs"] = next_outputs
        if next_tasks is not UNSET:
            field_dict["nextTasks"] = next_tasks
        if source_outputs is not UNSET:
            field_dict["sourceOutputs"] = source_outputs
        if source_tasks is not UNSET:
            field_dict["sourceTasks"] = source_tasks
        if creation_origin is not UNSET:
            field_dict["creationOrigin"] = creation_origin
        if fields is not UNSET:
            field_dict["fields"] = fields
        if task is not UNSET:
            field_dict["task"] = task
        if web_url is not UNSET:
            field_dict["webURL"] = web_url
        if workflow_task_group is not UNSET:
            field_dict["workflowTaskGroup"] = workflow_task_group
        if display_id is not UNSET:
            field_dict["displayId"] = display_id
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_outputs() -> Union[Unset, List[WorkflowOutputSummary]]:
            next_outputs = []
            _next_outputs = d.pop("nextOutputs")
            for next_outputs_item_data in _next_outputs or []:
                next_outputs_item = WorkflowOutputSummary.from_dict(next_outputs_item_data)

                next_outputs.append(next_outputs_item)

            return next_outputs

        next_outputs = (
            get_next_outputs()
            if "nextOutputs" in d
            else cast(Union[Unset, List[WorkflowOutputSummary]], UNSET)
        )

        def get_next_tasks() -> Union[Unset, List[WorkflowTaskSummary]]:
            next_tasks = []
            _next_tasks = d.pop("nextTasks")
            for next_tasks_item_data in _next_tasks or []:
                next_tasks_item = WorkflowTaskSummary.from_dict(next_tasks_item_data)

                next_tasks.append(next_tasks_item)

            return next_tasks

        next_tasks = (
            get_next_tasks() if "nextTasks" in d else cast(Union[Unset, List[WorkflowTaskSummary]], UNSET)
        )

        def get_source_outputs() -> Union[Unset, List[WorkflowOutputSummary]]:
            source_outputs = []
            _source_outputs = d.pop("sourceOutputs")
            for source_outputs_item_data in _source_outputs or []:
                source_outputs_item = WorkflowOutputSummary.from_dict(source_outputs_item_data)

                source_outputs.append(source_outputs_item)

            return source_outputs

        source_outputs = (
            get_source_outputs()
            if "sourceOutputs" in d
            else cast(Union[Unset, List[WorkflowOutputSummary]], UNSET)
        )

        def get_source_tasks() -> Union[Unset, List[WorkflowTaskSummary]]:
            source_tasks = []
            _source_tasks = d.pop("sourceTasks")
            for source_tasks_item_data in _source_tasks or []:
                source_tasks_item = WorkflowTaskSummary.from_dict(source_tasks_item_data)

                source_tasks.append(source_tasks_item)

            return source_tasks

        source_tasks = (
            get_source_tasks() if "sourceTasks" in d else cast(Union[Unset, List[WorkflowTaskSummary]], UNSET)
        )

        def get_creation_origin() -> Union[Unset, CreationOrigin]:
            creation_origin: Union[Unset, CreationOrigin] = UNSET
            _creation_origin = d.pop("creationOrigin")
            if not isinstance(_creation_origin, Unset):
                creation_origin = CreationOrigin.from_dict(_creation_origin)

            return creation_origin

        creation_origin = (
            get_creation_origin() if "creationOrigin" in d else cast(Union[Unset, CreationOrigin], UNSET)
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_task() -> Union[Unset, WorkflowTaskSummary]:
            task: Union[Unset, WorkflowTaskSummary] = UNSET
            _task = d.pop("task")
            if not isinstance(_task, Unset):
                task = WorkflowTaskSummary.from_dict(_task)

            return task

        task = get_task() if "task" in d else cast(Union[Unset, WorkflowTaskSummary], UNSET)

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_task_group() -> Union[Unset, WorkflowTaskGroupSummary]:
            workflow_task_group: Union[Unset, WorkflowTaskGroupSummary] = UNSET
            _workflow_task_group = d.pop("workflowTaskGroup")
            if not isinstance(_workflow_task_group, Unset):
                workflow_task_group = WorkflowTaskGroupSummary.from_dict(_workflow_task_group)

            return workflow_task_group

        workflow_task_group = (
            get_workflow_task_group()
            if "workflowTaskGroup" in d
            else cast(Union[Unset, WorkflowTaskGroupSummary], UNSET)
        )

        def get_display_id() -> Union[Unset, str]:
            display_id = d.pop("displayId")
            return display_id

        display_id = get_display_id() if "displayId" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        workflow_output = cls(
            next_outputs=next_outputs,
            next_tasks=next_tasks,
            source_outputs=source_outputs,
            source_tasks=source_tasks,
            creation_origin=creation_origin,
            fields=fields,
            task=task,
            web_url=web_url,
            workflow_task_group=workflow_task_group,
            display_id=display_id,
            id=id,
        )

        workflow_output.additional_properties = d
        return workflow_output

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
    def next_outputs(self) -> List[WorkflowOutputSummary]:
        if isinstance(self._next_outputs, Unset):
            raise NotPresentError(self, "next_outputs")
        return self._next_outputs

    @next_outputs.setter
    def next_outputs(self, value: List[WorkflowOutputSummary]) -> None:
        self._next_outputs = value

    @next_outputs.deleter
    def next_outputs(self) -> None:
        self._next_outputs = UNSET

    @property
    def next_tasks(self) -> List[WorkflowTaskSummary]:
        if isinstance(self._next_tasks, Unset):
            raise NotPresentError(self, "next_tasks")
        return self._next_tasks

    @next_tasks.setter
    def next_tasks(self, value: List[WorkflowTaskSummary]) -> None:
        self._next_tasks = value

    @next_tasks.deleter
    def next_tasks(self) -> None:
        self._next_tasks = UNSET

    @property
    def source_outputs(self) -> List[WorkflowOutputSummary]:
        if isinstance(self._source_outputs, Unset):
            raise NotPresentError(self, "source_outputs")
        return self._source_outputs

    @source_outputs.setter
    def source_outputs(self, value: List[WorkflowOutputSummary]) -> None:
        self._source_outputs = value

    @source_outputs.deleter
    def source_outputs(self) -> None:
        self._source_outputs = UNSET

    @property
    def source_tasks(self) -> List[WorkflowTaskSummary]:
        if isinstance(self._source_tasks, Unset):
            raise NotPresentError(self, "source_tasks")
        return self._source_tasks

    @source_tasks.setter
    def source_tasks(self, value: List[WorkflowTaskSummary]) -> None:
        self._source_tasks = value

    @source_tasks.deleter
    def source_tasks(self) -> None:
        self._source_tasks = UNSET

    @property
    def creation_origin(self) -> CreationOrigin:
        if isinstance(self._creation_origin, Unset):
            raise NotPresentError(self, "creation_origin")
        return self._creation_origin

    @creation_origin.setter
    def creation_origin(self, value: CreationOrigin) -> None:
        self._creation_origin = value

    @creation_origin.deleter
    def creation_origin(self) -> None:
        self._creation_origin = UNSET

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

    @property
    def task(self) -> WorkflowTaskSummary:
        if isinstance(self._task, Unset):
            raise NotPresentError(self, "task")
        return self._task

    @task.setter
    def task(self, value: WorkflowTaskSummary) -> None:
        self._task = value

    @task.deleter
    def task(self) -> None:
        self._task = UNSET

    @property
    def web_url(self) -> str:
        """ URL of the workflow output """
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET

    @property
    def workflow_task_group(self) -> WorkflowTaskGroupSummary:
        if isinstance(self._workflow_task_group, Unset):
            raise NotPresentError(self, "workflow_task_group")
        return self._workflow_task_group

    @workflow_task_group.setter
    def workflow_task_group(self, value: WorkflowTaskGroupSummary) -> None:
        self._workflow_task_group = value

    @workflow_task_group.deleter
    def workflow_task_group(self) -> None:
        self._workflow_task_group = UNSET

    @property
    def display_id(self) -> str:
        """ User-friendly ID of the workflow task group """
        if isinstance(self._display_id, Unset):
            raise NotPresentError(self, "display_id")
        return self._display_id

    @display_id.setter
    def display_id(self, value: str) -> None:
        self._display_id = value

    @display_id.deleter
    def display_id(self) -> None:
        self._display_id = UNSET

    @property
    def id(self) -> str:
        """ The ID of the workflow output """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET
