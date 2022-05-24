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

T = TypeVar("T", bound="BenchlingAppConfiguration")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppConfiguration:
    """  """

    _api_url: Union[Unset, str] = UNSET
    _app_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, str] = UNSET
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
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("app_id={}".format(repr(self._app_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("configuration={}".format(repr(self._configuration)))
        return "BenchlingAppConfiguration({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        api_url = self._api_url
        app_id = self._app_id
        id = self._id
        modified_at = self._modified_at
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
        if api_url is not UNSET:
            field_dict["apiUrl"] = api_url
        if app_id is not UNSET:
            field_dict["appId"] = app_id
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if configuration is not UNSET:
            field_dict["configuration"] = configuration

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiUrl")
            return api_url

        api_url = get_api_url() if "apiUrl" in d else cast(Union[Unset, str], UNSET)

        def get_app_id() -> Union[Unset, str]:
            app_id = d.pop("appId")
            return app_id

        app_id = get_app_id() if "appId" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, str]:
            modified_at = d.pop("modifiedAt")
            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, str], UNSET)

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

        benchling_app_configuration = cls(
            api_url=api_url,
            app_id=app_id,
            id=id,
            modified_at=modified_at,
            configuration=configuration,
        )

        return benchling_app_configuration

    @property
    def api_url(self) -> str:
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

    @property
    def app_id(self) -> str:
        """ The app to which this configuration belongs. """
        if isinstance(self._app_id, Unset):
            raise NotPresentError(self, "app_id")
        return self._app_id

    @app_id.setter
    def app_id(self, value: str) -> None:
        self._app_id = value

    @app_id.deleter
    def app_id(self) -> None:
        self._app_id = UNSET

    @property
    def id(self) -> str:
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
    def modified_at(self) -> str:
        """ DateTime the template was last modified """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: str) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

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
