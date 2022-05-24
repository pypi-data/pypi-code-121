from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.dropdown_dependency_link import DropdownDependencyLink
from ..models.entity_schema_dependency_link import EntitySchemaDependencyLink
from ..models.resource_dependency_link import ResourceDependencyLink
from ..models.scalar_config import ScalarConfig
from ..models.schema_dependency_link import SchemaDependencyLink
from ..models.secure_text_config import SecureTextConfig
from ..models.workflow_task_schema_dependency_link import WorkflowTaskSchemaDependencyLink
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppUpdate")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppUpdate:
    """  """

    _description: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _configuration: Union[
        Unset,
        List[
            Union[
                SchemaDependencyLink,
                EntitySchemaDependencyLink,
                WorkflowTaskSchemaDependencyLink,
                DropdownDependencyLink,
                ResourceDependencyLink,
                ScalarConfig,
                SecureTextConfig,
                UnknownType,
            ]
        ],
    ] = UNSET

    def __repr__(self):
        fields = []
        fields.append("description={}".format(repr(self._description)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("configuration={}".format(repr(self._configuration)))
        return "BenchlingAppUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        description = self._description
        name = self._name
        configuration: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._configuration, Unset):
            configuration = []
            for configuration_item_data in self._configuration:
                if isinstance(configuration_item_data, UnknownType):
                    configuration_item = configuration_item_data.value
                elif isinstance(configuration_item_data, SchemaDependencyLink):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, EntitySchemaDependencyLink):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, WorkflowTaskSchemaDependencyLink):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, DropdownDependencyLink):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, ResourceDependencyLink):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, ScalarConfig):
                    configuration_item = configuration_item_data.to_dict()

                else:
                    configuration_item = configuration_item_data.to_dict()

                configuration.append(configuration_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name
        if configuration is not UNSET:
            field_dict["configuration"] = configuration

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_description() -> Union[Unset, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_configuration() -> Union[
            Unset,
            List[
                Union[
                    SchemaDependencyLink,
                    EntitySchemaDependencyLink,
                    WorkflowTaskSchemaDependencyLink,
                    DropdownDependencyLink,
                    ResourceDependencyLink,
                    ScalarConfig,
                    SecureTextConfig,
                    UnknownType,
                ]
            ],
        ]:
            configuration = []
            _configuration = d.pop("configuration")
            for configuration_item_data in _configuration or []:

                def _parse_configuration_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[
                    SchemaDependencyLink,
                    EntitySchemaDependencyLink,
                    WorkflowTaskSchemaDependencyLink,
                    DropdownDependencyLink,
                    ResourceDependencyLink,
                    ScalarConfig,
                    SecureTextConfig,
                    UnknownType,
                ]:
                    configuration_item: Union[
                        SchemaDependencyLink,
                        EntitySchemaDependencyLink,
                        WorkflowTaskSchemaDependencyLink,
                        DropdownDependencyLink,
                        ResourceDependencyLink,
                        ScalarConfig,
                        SecureTextConfig,
                        UnknownType,
                    ]
                    discriminator_value: str = cast(str, data.get("type"))
                    if discriminator_value is not None:
                        if discriminator_value == "aa_sequence":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "boolean":
                            configuration_item = ScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "box":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "box_schema":
                            configuration_item = SchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "container":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "container_schema":
                            configuration_item = SchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "custom_entity":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "date":
                            configuration_item = ScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "datetime":
                            configuration_item = ScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "dna_oligo":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "dna_sequence":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "dropdown":
                            configuration_item = DropdownDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "entity_schema":
                            configuration_item = EntitySchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "entry":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "entry_schema":
                            configuration_item = SchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "float":
                            configuration_item = ScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "folder":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "integer":
                            configuration_item = ScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "location":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "location_schema":
                            configuration_item = SchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "mixture":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "plate":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "plate_schema":
                            configuration_item = SchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "project":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "registry":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "request_schema":
                            configuration_item = SchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "result_schema":
                            configuration_item = SchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "run_schema":
                            configuration_item = SchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "secure_text":
                            configuration_item = SecureTextConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "text":
                            configuration_item = ScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "workflow_task_schema":
                            configuration_item = WorkflowTaskSchemaDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "workflow_task_status":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item
                        if discriminator_value == "worklist":
                            configuration_item = ResourceDependencyLink.from_dict(data)

                            return configuration_item

                        return UnknownType(value=data)
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = SchemaDependencyLink.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = EntitySchemaDependencyLink.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = WorkflowTaskSchemaDependencyLink.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = DropdownDependencyLink.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = ResourceDependencyLink.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = ScalarConfig.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = SecureTextConfig.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                configuration_item = _parse_configuration_item(configuration_item_data)

                configuration.append(configuration_item)

            return configuration

        configuration = (
            get_configuration()
            if "configuration" in d
            else cast(
                Union[
                    Unset,
                    List[
                        Union[
                            SchemaDependencyLink,
                            EntitySchemaDependencyLink,
                            WorkflowTaskSchemaDependencyLink,
                            DropdownDependencyLink,
                            ResourceDependencyLink,
                            ScalarConfig,
                            SecureTextConfig,
                            UnknownType,
                        ]
                    ],
                ],
                UNSET,
            )
        )

        benchling_app_update = cls(
            description=description,
            name=name,
            configuration=configuration,
        )

        return benchling_app_update

    @property
    def description(self) -> str:
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def configuration(
        self,
    ) -> List[
        Union[
            SchemaDependencyLink,
            EntitySchemaDependencyLink,
            WorkflowTaskSchemaDependencyLink,
            DropdownDependencyLink,
            ResourceDependencyLink,
            ScalarConfig,
            SecureTextConfig,
            UnknownType,
        ]
    ]:
        if isinstance(self._configuration, Unset):
            raise NotPresentError(self, "configuration")
        return self._configuration

    @configuration.setter
    def configuration(
        self,
        value: List[
            Union[
                SchemaDependencyLink,
                EntitySchemaDependencyLink,
                WorkflowTaskSchemaDependencyLink,
                DropdownDependencyLink,
                ResourceDependencyLink,
                ScalarConfig,
                SecureTextConfig,
                UnknownType,
            ]
        ],
    ) -> None:
        self._configuration = value

    @configuration.deleter
    def configuration(self) -> None:
        self._configuration = UNSET
