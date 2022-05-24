from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.base_manifest_config import BaseManifestConfig
from ..models.workflow_task_schema_dependency_output import WorkflowTaskSchemaDependencyOutput
from ..models.workflow_task_schema_dependency_type import WorkflowTaskSchemaDependencyType
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskSchemaDependency")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskSchemaDependency:
    """  """

    _type: WorkflowTaskSchemaDependencyType
    _name: str
    _output: Union[Unset, WorkflowTaskSchemaDependencyOutput] = UNSET
    _field_definitions: Union[Unset, List[BaseManifestConfig]] = UNSET
    _description: Union[Unset, None, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("output={}".format(repr(self._output)))
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("description={}".format(repr(self._description)))
        return "WorkflowTaskSchemaDependency({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type = self._type.value

        name = self._name
        output: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._output, Unset):
            output = self._output.to_dict()

        field_definitions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._field_definitions, Unset):
            field_definitions = []
            for field_definitions_item_data in self._field_definitions:
                field_definitions_item = field_definitions_item_data.to_dict()

                field_definitions.append(field_definitions_item)

        description = self._description

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
                "name": name,
            }
        )
        if output is not UNSET:
            field_dict["output"] = output
        if field_definitions is not UNSET:
            field_dict["fieldDefinitions"] = field_definitions
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> WorkflowTaskSchemaDependencyType:
            _type = d.pop("type")
            try:
                type = WorkflowTaskSchemaDependencyType(_type)
            except ValueError:
                type = WorkflowTaskSchemaDependencyType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(WorkflowTaskSchemaDependencyType, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_output() -> Union[Unset, WorkflowTaskSchemaDependencyOutput]:
            output: Union[Unset, WorkflowTaskSchemaDependencyOutput] = UNSET
            _output = d.pop("output")
            if not isinstance(_output, Unset):
                output = WorkflowTaskSchemaDependencyOutput.from_dict(_output)

            return output

        output = (
            get_output() if "output" in d else cast(Union[Unset, WorkflowTaskSchemaDependencyOutput], UNSET)
        )

        def get_field_definitions() -> Union[Unset, List[BaseManifestConfig]]:
            field_definitions = []
            _field_definitions = d.pop("fieldDefinitions")
            for field_definitions_item_data in _field_definitions or []:
                field_definitions_item = BaseManifestConfig.from_dict(field_definitions_item_data)

                field_definitions.append(field_definitions_item)

            return field_definitions

        field_definitions = (
            get_field_definitions()
            if "fieldDefinitions" in d
            else cast(Union[Unset, List[BaseManifestConfig]], UNSET)
        )

        def get_description() -> Union[Unset, None, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, None, str], UNSET)

        workflow_task_schema_dependency = cls(
            type=type,
            name=name,
            output=output,
            field_definitions=field_definitions,
            description=description,
        )

        return workflow_task_schema_dependency

    @property
    def type(self) -> WorkflowTaskSchemaDependencyType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: WorkflowTaskSchemaDependencyType) -> None:
        self._type = value

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def output(self) -> WorkflowTaskSchemaDependencyOutput:
        if isinstance(self._output, Unset):
            raise NotPresentError(self, "output")
        return self._output

    @output.setter
    def output(self, value: WorkflowTaskSchemaDependencyOutput) -> None:
        self._output = value

    @output.deleter
    def output(self) -> None:
        self._output = UNSET

    @property
    def field_definitions(self) -> List[BaseManifestConfig]:
        if isinstance(self._field_definitions, Unset):
            raise NotPresentError(self, "field_definitions")
        return self._field_definitions

    @field_definitions.setter
    def field_definitions(self, value: List[BaseManifestConfig]) -> None:
        self._field_definitions = value

    @field_definitions.deleter
    def field_definitions(self) -> None:
        self._field_definitions = UNSET

    @property
    def description(self) -> Optional[str]:
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET
