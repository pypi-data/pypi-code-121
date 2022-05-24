from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.benchling_app_manifest_info import BenchlingAppManifestInfo
from ..models.benchling_app_manifest_manifest_version import BenchlingAppManifestManifestVersion
from ..models.benchling_app_manifest_security import BenchlingAppManifestSecurity
from ..models.dropdown_dependency import DropdownDependency
from ..models.entity_schema_dependency import EntitySchemaDependency
from ..models.manifest_scalar_config import ManifestScalarConfig
from ..models.resource_dependency import ResourceDependency
from ..models.schema_dependency import SchemaDependency
from ..models.workflow_task_schema_dependency import WorkflowTaskSchemaDependency
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppManifest")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppManifest:
    """  """

    _configuration: Union[
        Unset,
        List[
            Union[
                SchemaDependency,
                EntitySchemaDependency,
                WorkflowTaskSchemaDependency,
                DropdownDependency,
                ResourceDependency,
                ManifestScalarConfig,
                UnknownType,
            ]
        ],
    ] = UNSET
    _info: Union[Unset, BenchlingAppManifestInfo] = UNSET
    _manifest_version: Union[Unset, BenchlingAppManifestManifestVersion] = UNSET
    _security: Union[Unset, BenchlingAppManifestSecurity] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("configuration={}".format(repr(self._configuration)))
        fields.append("info={}".format(repr(self._info)))
        fields.append("manifest_version={}".format(repr(self._manifest_version)))
        fields.append("security={}".format(repr(self._security)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BenchlingAppManifest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        configuration: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._configuration, Unset):
            configuration = []
            for configuration_item_data in self._configuration:
                if isinstance(configuration_item_data, UnknownType):
                    configuration_item = configuration_item_data.value
                elif isinstance(configuration_item_data, SchemaDependency):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, EntitySchemaDependency):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, WorkflowTaskSchemaDependency):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, DropdownDependency):
                    configuration_item = configuration_item_data.to_dict()

                elif isinstance(configuration_item_data, ResourceDependency):
                    configuration_item = configuration_item_data.to_dict()

                else:
                    configuration_item = configuration_item_data.to_dict()

                configuration.append(configuration_item)

        info: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._info, Unset):
            info = self._info.to_dict()

        manifest_version: Union[Unset, int] = UNSET
        if not isinstance(self._manifest_version, Unset):
            manifest_version = self._manifest_version.value

        security: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._security, Unset):
            security = self._security.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if configuration is not UNSET:
            field_dict["configuration"] = configuration
        if info is not UNSET:
            field_dict["info"] = info
        if manifest_version is not UNSET:
            field_dict["manifestVersion"] = manifest_version
        if security is not UNSET:
            field_dict["security"] = security

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_configuration() -> Union[
            Unset,
            List[
                Union[
                    SchemaDependency,
                    EntitySchemaDependency,
                    WorkflowTaskSchemaDependency,
                    DropdownDependency,
                    ResourceDependency,
                    ManifestScalarConfig,
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
                    SchemaDependency,
                    EntitySchemaDependency,
                    WorkflowTaskSchemaDependency,
                    DropdownDependency,
                    ResourceDependency,
                    ManifestScalarConfig,
                    UnknownType,
                ]:
                    configuration_item: Union[
                        SchemaDependency,
                        EntitySchemaDependency,
                        WorkflowTaskSchemaDependency,
                        DropdownDependency,
                        ResourceDependency,
                        ManifestScalarConfig,
                        UnknownType,
                    ]
                    discriminator_value: str = cast(str, data.get("type"))
                    if discriminator_value is not None:
                        if discriminator_value == "aa_sequence":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "boolean":
                            configuration_item = ManifestScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "box":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "box_schema":
                            configuration_item = SchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "container":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "container_schema":
                            configuration_item = SchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "custom_entity":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "date":
                            configuration_item = ManifestScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "datetime":
                            configuration_item = ManifestScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "dna_oligo":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "dna_sequence":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "dropdown":
                            configuration_item = DropdownDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "entity_schema":
                            configuration_item = EntitySchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "entry":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "entry_schema":
                            configuration_item = SchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "float":
                            configuration_item = ManifestScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "folder":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "integer":
                            configuration_item = ManifestScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "location":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "location_schema":
                            configuration_item = SchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "mixture":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "plate":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "plate_schema":
                            configuration_item = SchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "project":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "registry":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "request_schema":
                            configuration_item = SchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "result_schema":
                            configuration_item = SchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "run_schema":
                            configuration_item = SchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "secure_text":
                            configuration_item = ManifestScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "text":
                            configuration_item = ManifestScalarConfig.from_dict(data)

                            return configuration_item
                        if discriminator_value == "workflow_task_schema":
                            configuration_item = WorkflowTaskSchemaDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "workflow_task_status":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item
                        if discriminator_value == "worklist":
                            configuration_item = ResourceDependency.from_dict(data)

                            return configuration_item

                        return UnknownType(value=data)
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = SchemaDependency.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = EntitySchemaDependency.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = WorkflowTaskSchemaDependency.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = DropdownDependency.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = ResourceDependency.from_dict(data)

                        return configuration_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        configuration_item = ManifestScalarConfig.from_dict(data)

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
                            SchemaDependency,
                            EntitySchemaDependency,
                            WorkflowTaskSchemaDependency,
                            DropdownDependency,
                            ResourceDependency,
                            ManifestScalarConfig,
                            UnknownType,
                        ]
                    ],
                ],
                UNSET,
            )
        )

        def get_info() -> Union[Unset, BenchlingAppManifestInfo]:
            info: Union[Unset, BenchlingAppManifestInfo] = UNSET
            _info = d.pop("info")
            if not isinstance(_info, Unset):
                info = BenchlingAppManifestInfo.from_dict(_info)

            return info

        info = get_info() if "info" in d else cast(Union[Unset, BenchlingAppManifestInfo], UNSET)

        def get_manifest_version() -> Union[Unset, BenchlingAppManifestManifestVersion]:
            manifest_version = None
            _manifest_version = d.pop("manifestVersion")
            if _manifest_version is not None and _manifest_version is not UNSET:
                try:
                    manifest_version = BenchlingAppManifestManifestVersion(_manifest_version)
                except ValueError:
                    manifest_version = BenchlingAppManifestManifestVersion.of_unknown(_manifest_version)

            return manifest_version

        manifest_version = (
            get_manifest_version()
            if "manifestVersion" in d
            else cast(Union[Unset, BenchlingAppManifestManifestVersion], UNSET)
        )

        def get_security() -> Union[Unset, BenchlingAppManifestSecurity]:
            security: Union[Unset, BenchlingAppManifestSecurity] = UNSET
            _security = d.pop("security")
            if not isinstance(_security, Unset):
                security = BenchlingAppManifestSecurity.from_dict(_security)

            return security

        security = (
            get_security() if "security" in d else cast(Union[Unset, BenchlingAppManifestSecurity], UNSET)
        )

        benchling_app_manifest = cls(
            configuration=configuration,
            info=info,
            manifest_version=manifest_version,
            security=security,
        )

        benchling_app_manifest.additional_properties = d
        return benchling_app_manifest

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
            SchemaDependency,
            EntitySchemaDependency,
            WorkflowTaskSchemaDependency,
            DropdownDependency,
            ResourceDependency,
            ManifestScalarConfig,
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
                SchemaDependency,
                EntitySchemaDependency,
                WorkflowTaskSchemaDependency,
                DropdownDependency,
                ResourceDependency,
                ManifestScalarConfig,
                UnknownType,
            ]
        ],
    ) -> None:
        self._configuration = value

    @configuration.deleter
    def configuration(self) -> None:
        self._configuration = UNSET

    @property
    def info(self) -> BenchlingAppManifestInfo:
        if isinstance(self._info, Unset):
            raise NotPresentError(self, "info")
        return self._info

    @info.setter
    def info(self, value: BenchlingAppManifestInfo) -> None:
        self._info = value

    @info.deleter
    def info(self) -> None:
        self._info = UNSET

    @property
    def manifest_version(self) -> BenchlingAppManifestManifestVersion:
        if isinstance(self._manifest_version, Unset):
            raise NotPresentError(self, "manifest_version")
        return self._manifest_version

    @manifest_version.setter
    def manifest_version(self, value: BenchlingAppManifestManifestVersion) -> None:
        self._manifest_version = value

    @manifest_version.deleter
    def manifest_version(self) -> None:
        self._manifest_version = UNSET

    @property
    def security(self) -> BenchlingAppManifestSecurity:
        if isinstance(self._security, Unset):
            raise NotPresentError(self, "security")
        return self._security

    @security.setter
    def security(self, value: BenchlingAppManifestSecurity) -> None:
        self._security = value

    @security.deleter
    def security(self) -> None:
        self._security = UNSET
