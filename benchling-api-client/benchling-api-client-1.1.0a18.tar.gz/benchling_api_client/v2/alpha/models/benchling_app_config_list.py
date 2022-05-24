from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

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

T = TypeVar("T", bound="BenchlingAppConfigList")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppConfigList:
    """  """

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
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("configuration={}".format(repr(self._configuration)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BenchlingAppConfigList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
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
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if configuration is not UNSET:
            field_dict["configuration"] = configuration

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

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

        benchling_app_config_list = cls(
            configuration=configuration,
        )

        benchling_app_config_list.additional_properties = d
        return benchling_app_config_list

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
