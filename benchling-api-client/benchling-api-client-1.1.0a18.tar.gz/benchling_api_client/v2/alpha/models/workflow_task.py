import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.creation_origin import CreationOrigin
from ..models.fields import Fields
from ..models.user_summary import UserSummary
from ..models.workflow_output_summary import WorkflowOutputSummary
from ..models.workflow_task_execution_origin import WorkflowTaskExecutionOrigin
from ..models.workflow_task_execution_type import WorkflowTaskExecutionType
from ..models.workflow_task_group_summary import WorkflowTaskGroupSummary
from ..models.workflow_task_status import WorkflowTaskStatus
from ..models.workflow_task_summary import WorkflowTaskSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTask")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTask:
    """  """

    _execution_type: Union[Unset, WorkflowTaskExecutionType] = UNSET
    _next_outputs: Union[Unset, List[WorkflowOutputSummary]] = UNSET
    _next_tasks: Union[Unset, List[WorkflowTaskSummary]] = UNSET
    _root_task: Union[Unset, WorkflowTaskSummary] = UNSET
    _source_outputs: Union[Unset, List[WorkflowOutputSummary]] = UNSET
    _source_tasks: Union[Unset, List[WorkflowTaskSummary]] = UNSET
    _assignee: Union[Unset, None, UserSummary] = UNSET
    _cloned_from: Union[Unset, None, WorkflowTaskSummary] = UNSET
    _creation_origin: Union[Unset, CreationOrigin] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    _execution_origin: Union[Unset, None, WorkflowTaskExecutionOrigin] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _outputs: Union[Unset, List[WorkflowOutputSummary]] = UNSET
    _scheduled_on: Union[Unset, None, datetime.date] = UNSET
    _status: Union[Unset, WorkflowTaskStatus] = UNSET
    _web_url: Union[Unset, str] = UNSET
    _workflow_task_group: Union[Unset, WorkflowTaskGroupSummary] = UNSET
    _display_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("execution_type={}".format(repr(self._execution_type)))
        fields.append("next_outputs={}".format(repr(self._next_outputs)))
        fields.append("next_tasks={}".format(repr(self._next_tasks)))
        fields.append("root_task={}".format(repr(self._root_task)))
        fields.append("source_outputs={}".format(repr(self._source_outputs)))
        fields.append("source_tasks={}".format(repr(self._source_tasks)))
        fields.append("assignee={}".format(repr(self._assignee)))
        fields.append("cloned_from={}".format(repr(self._cloned_from)))
        fields.append("creation_origin={}".format(repr(self._creation_origin)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("execution_origin={}".format(repr(self._execution_origin)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("outputs={}".format(repr(self._outputs)))
        fields.append("scheduled_on={}".format(repr(self._scheduled_on)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("workflow_task_group={}".format(repr(self._workflow_task_group)))
        fields.append("display_id={}".format(repr(self._display_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTask({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        execution_type: Union[Unset, int] = UNSET
        if not isinstance(self._execution_type, Unset):
            execution_type = self._execution_type.value

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

        root_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._root_task, Unset):
            root_task = self._root_task.to_dict()

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

        assignee: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._assignee, Unset):
            assignee = self._assignee.to_dict() if self._assignee else None

        cloned_from: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._cloned_from, Unset):
            cloned_from = self._cloned_from.to_dict() if self._cloned_from else None

        creation_origin: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creation_origin, Unset):
            creation_origin = self._creation_origin.to_dict()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        execution_origin: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._execution_origin, Unset):
            execution_origin = self._execution_origin.to_dict() if self._execution_origin else None

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        outputs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._outputs, Unset):
            outputs = []
            for outputs_item_data in self._outputs:
                outputs_item = outputs_item_data.to_dict()

                outputs.append(outputs_item)

        scheduled_on: Union[Unset, None, str] = UNSET
        if not isinstance(self._scheduled_on, Unset):
            scheduled_on = self._scheduled_on.isoformat() if self._scheduled_on else None

        status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._status, Unset):
            status = self._status.to_dict()

        web_url = self._web_url
        workflow_task_group: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._workflow_task_group, Unset):
            workflow_task_group = self._workflow_task_group.to_dict()

        display_id = self._display_id
        id = self._id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if execution_type is not UNSET:
            field_dict["executionType"] = execution_type
        if next_outputs is not UNSET:
            field_dict["nextOutputs"] = next_outputs
        if next_tasks is not UNSET:
            field_dict["nextTasks"] = next_tasks
        if root_task is not UNSET:
            field_dict["rootTask"] = root_task
        if source_outputs is not UNSET:
            field_dict["sourceOutputs"] = source_outputs
        if source_tasks is not UNSET:
            field_dict["sourceTasks"] = source_tasks
        if assignee is not UNSET:
            field_dict["assignee"] = assignee
        if cloned_from is not UNSET:
            field_dict["clonedFrom"] = cloned_from
        if creation_origin is not UNSET:
            field_dict["creationOrigin"] = creation_origin
        if creator is not UNSET:
            field_dict["creator"] = creator
        if execution_origin is not UNSET:
            field_dict["executionOrigin"] = execution_origin
        if fields is not UNSET:
            field_dict["fields"] = fields
        if outputs is not UNSET:
            field_dict["outputs"] = outputs
        if scheduled_on is not UNSET:
            field_dict["scheduledOn"] = scheduled_on
        if status is not UNSET:
            field_dict["status"] = status
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

        def get_execution_type() -> Union[Unset, WorkflowTaskExecutionType]:
            execution_type = None
            _execution_type = d.pop("executionType")
            if _execution_type is not None and _execution_type is not UNSET:
                try:
                    execution_type = WorkflowTaskExecutionType(_execution_type)
                except ValueError:
                    execution_type = WorkflowTaskExecutionType.of_unknown(_execution_type)

            return execution_type

        execution_type = (
            get_execution_type()
            if "executionType" in d
            else cast(Union[Unset, WorkflowTaskExecutionType], UNSET)
        )

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

        def get_root_task() -> Union[Unset, WorkflowTaskSummary]:
            root_task: Union[Unset, WorkflowTaskSummary] = UNSET
            _root_task = d.pop("rootTask")
            if not isinstance(_root_task, Unset):
                root_task = WorkflowTaskSummary.from_dict(_root_task)

            return root_task

        root_task = get_root_task() if "rootTask" in d else cast(Union[Unset, WorkflowTaskSummary], UNSET)

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

        def get_assignee() -> Union[Unset, None, UserSummary]:
            assignee = None
            _assignee = d.pop("assignee")
            if _assignee is not None and not isinstance(_assignee, Unset):
                assignee = UserSummary.from_dict(_assignee)

            return assignee

        assignee = get_assignee() if "assignee" in d else cast(Union[Unset, None, UserSummary], UNSET)

        def get_cloned_from() -> Union[Unset, None, WorkflowTaskSummary]:
            cloned_from = None
            _cloned_from = d.pop("clonedFrom")
            if _cloned_from is not None and not isinstance(_cloned_from, Unset):
                cloned_from = WorkflowTaskSummary.from_dict(_cloned_from)

            return cloned_from

        cloned_from = (
            get_cloned_from() if "clonedFrom" in d else cast(Union[Unset, None, WorkflowTaskSummary], UNSET)
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

        def get_creator() -> Union[Unset, UserSummary]:
            creator: Union[Unset, UserSummary] = UNSET
            _creator = d.pop("creator")
            if not isinstance(_creator, Unset):
                creator = UserSummary.from_dict(_creator)

            return creator

        creator = get_creator() if "creator" in d else cast(Union[Unset, UserSummary], UNSET)

        def get_execution_origin() -> Union[Unset, None, WorkflowTaskExecutionOrigin]:
            execution_origin = None
            _execution_origin = d.pop("executionOrigin")
            if _execution_origin is not None and not isinstance(_execution_origin, Unset):
                execution_origin = WorkflowTaskExecutionOrigin.from_dict(_execution_origin)

            return execution_origin

        execution_origin = (
            get_execution_origin()
            if "executionOrigin" in d
            else cast(Union[Unset, None, WorkflowTaskExecutionOrigin], UNSET)
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_outputs() -> Union[Unset, List[WorkflowOutputSummary]]:
            outputs = []
            _outputs = d.pop("outputs")
            for outputs_item_data in _outputs or []:
                outputs_item = WorkflowOutputSummary.from_dict(outputs_item_data)

                outputs.append(outputs_item)

            return outputs

        outputs = get_outputs() if "outputs" in d else cast(Union[Unset, List[WorkflowOutputSummary]], UNSET)

        def get_scheduled_on() -> Union[Unset, None, datetime.date]:
            scheduled_on: Union[Unset, None, datetime.date] = UNSET
            _scheduled_on = d.pop("scheduledOn")
            if _scheduled_on is not None and not isinstance(_scheduled_on, Unset):
                scheduled_on = isoparse(cast(str, _scheduled_on)).date()

            return scheduled_on

        scheduled_on = (
            get_scheduled_on() if "scheduledOn" in d else cast(Union[Unset, None, datetime.date], UNSET)
        )

        def get_status() -> Union[Unset, WorkflowTaskStatus]:
            status: Union[Unset, WorkflowTaskStatus] = UNSET
            _status = d.pop("status")
            if not isinstance(_status, Unset):
                status = WorkflowTaskStatus.from_dict(_status)

            return status

        status = get_status() if "status" in d else cast(Union[Unset, WorkflowTaskStatus], UNSET)

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

        workflow_task = cls(
            execution_type=execution_type,
            next_outputs=next_outputs,
            next_tasks=next_tasks,
            root_task=root_task,
            source_outputs=source_outputs,
            source_tasks=source_tasks,
            assignee=assignee,
            cloned_from=cloned_from,
            creation_origin=creation_origin,
            creator=creator,
            execution_origin=execution_origin,
            fields=fields,
            outputs=outputs,
            scheduled_on=scheduled_on,
            status=status,
            web_url=web_url,
            workflow_task_group=workflow_task_group,
            display_id=display_id,
            id=id,
        )

        workflow_task.additional_properties = d
        return workflow_task

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
    def execution_type(self) -> WorkflowTaskExecutionType:
        """ The method by which the task of the workflow is executed """
        if isinstance(self._execution_type, Unset):
            raise NotPresentError(self, "execution_type")
        return self._execution_type

    @execution_type.setter
    def execution_type(self, value: WorkflowTaskExecutionType) -> None:
        self._execution_type = value

    @execution_type.deleter
    def execution_type(self) -> None:
        self._execution_type = UNSET

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
    def root_task(self) -> WorkflowTaskSummary:
        if isinstance(self._root_task, Unset):
            raise NotPresentError(self, "root_task")
        return self._root_task

    @root_task.setter
    def root_task(self, value: WorkflowTaskSummary) -> None:
        self._root_task = value

    @root_task.deleter
    def root_task(self) -> None:
        self._root_task = UNSET

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
    def assignee(self) -> Optional[UserSummary]:
        if isinstance(self._assignee, Unset):
            raise NotPresentError(self, "assignee")
        return self._assignee

    @assignee.setter
    def assignee(self, value: Optional[UserSummary]) -> None:
        self._assignee = value

    @assignee.deleter
    def assignee(self) -> None:
        self._assignee = UNSET

    @property
    def cloned_from(self) -> Optional[WorkflowTaskSummary]:
        if isinstance(self._cloned_from, Unset):
            raise NotPresentError(self, "cloned_from")
        return self._cloned_from

    @cloned_from.setter
    def cloned_from(self, value: Optional[WorkflowTaskSummary]) -> None:
        self._cloned_from = value

    @cloned_from.deleter
    def cloned_from(self) -> None:
        self._cloned_from = UNSET

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
    def creator(self) -> UserSummary:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: UserSummary) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

    @property
    def execution_origin(self) -> Optional[WorkflowTaskExecutionOrigin]:
        """ The context into which a task was executed """
        if isinstance(self._execution_origin, Unset):
            raise NotPresentError(self, "execution_origin")
        return self._execution_origin

    @execution_origin.setter
    def execution_origin(self, value: Optional[WorkflowTaskExecutionOrigin]) -> None:
        self._execution_origin = value

    @execution_origin.deleter
    def execution_origin(self) -> None:
        self._execution_origin = UNSET

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
    def outputs(self) -> List[WorkflowOutputSummary]:
        if isinstance(self._outputs, Unset):
            raise NotPresentError(self, "outputs")
        return self._outputs

    @outputs.setter
    def outputs(self, value: List[WorkflowOutputSummary]) -> None:
        self._outputs = value

    @outputs.deleter
    def outputs(self) -> None:
        self._outputs = UNSET

    @property
    def scheduled_on(self) -> Optional[datetime.date]:
        """ The date on which the task is scheduled to be executed """
        if isinstance(self._scheduled_on, Unset):
            raise NotPresentError(self, "scheduled_on")
        return self._scheduled_on

    @scheduled_on.setter
    def scheduled_on(self, value: Optional[datetime.date]) -> None:
        self._scheduled_on = value

    @scheduled_on.deleter
    def scheduled_on(self) -> None:
        self._scheduled_on = UNSET

    @property
    def status(self) -> WorkflowTaskStatus:
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: WorkflowTaskStatus) -> None:
        self._status = value

    @status.deleter
    def status(self) -> None:
        self._status = UNSET

    @property
    def web_url(self) -> str:
        """ URL of the workflow task """
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
        """ User-friendly ID of the workflow task """
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
        """ The ID of the workflow task """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET
