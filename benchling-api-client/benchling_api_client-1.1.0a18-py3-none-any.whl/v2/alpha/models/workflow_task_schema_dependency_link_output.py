from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.subdependency_link import SubdependencyLink
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskSchemaDependencyLinkOutput")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskSchemaDependencyLinkOutput:
    """  """

    _field_definitions: Union[Unset, List[SubdependencyLink]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskSchemaDependencyLinkOutput({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        field_definitions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._field_definitions, Unset):
            field_definitions = []
            for field_definitions_item_data in self._field_definitions:
                field_definitions_item = field_definitions_item_data.to_dict()

                field_definitions.append(field_definitions_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_definitions is not UNSET:
            field_dict["fieldDefinitions"] = field_definitions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_field_definitions() -> Union[Unset, List[SubdependencyLink]]:
            field_definitions = []
            _field_definitions = d.pop("fieldDefinitions")
            for field_definitions_item_data in _field_definitions or []:
                field_definitions_item = SubdependencyLink.from_dict(field_definitions_item_data)

                field_definitions.append(field_definitions_item)

            return field_definitions

        field_definitions = (
            get_field_definitions()
            if "fieldDefinitions" in d
            else cast(Union[Unset, List[SubdependencyLink]], UNSET)
        )

        workflow_task_schema_dependency_link_output = cls(
            field_definitions=field_definitions,
        )

        workflow_task_schema_dependency_link_output.additional_properties = d
        return workflow_task_schema_dependency_link_output

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
    def field_definitions(self) -> List[SubdependencyLink]:
        if isinstance(self._field_definitions, Unset):
            raise NotPresentError(self, "field_definitions")
        return self._field_definitions

    @field_definitions.setter
    def field_definitions(self, value: List[SubdependencyLink]) -> None:
        self._field_definitions = value

    @field_definitions.deleter
    def field_definitions(self) -> None:
        self._field_definitions = UNSET
