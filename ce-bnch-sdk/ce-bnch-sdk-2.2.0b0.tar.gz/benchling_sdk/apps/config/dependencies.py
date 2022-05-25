from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from benchling_api_client.v2.beta.models.benchling_app_configuration import BenchlingAppConfiguration
from benchling_api_client.v2.beta.models.dropdown_dependency_link import DropdownDependencyLink
from benchling_api_client.v2.beta.models.entity_schema_dependency_link import EntitySchemaDependencyLink
from benchling_api_client.v2.beta.models.resource_dependency_link import ResourceDependencyLink
from benchling_api_client.v2.beta.models.scalar_config import ScalarConfig
from benchling_api_client.v2.beta.models.scalar_config_types import ScalarConfigTypes
from benchling_api_client.v2.beta.models.schema_dependency_link import SchemaDependencyLink
from benchling_api_client.v2.beta.models.secure_text_config import SecureTextConfig
from benchling_api_client.v2.beta.models.subdependency_link import SubdependencyLink
from benchling_api_client.v2.beta.models.workflow_task_schema_dependency_link import (
    WorkflowTaskSchemaDependencyLink,
)
from benchling_api_client.v2.extensions import UnknownType
from typing_extensions import Protocol

from benchling_sdk.apps.config.scalars import DEFAULT_SCALAR_DEFINITIONS, ScalarDefinition, ScalarType
from benchling_sdk.benchling import Benchling


class MissingDependencyError(Exception):
    pass


class MissingAppConfigError(Exception):
    pass


class UnsupportedDependencyError(Exception):
    pass


class MissingScalarDefinitionError(Exception):
    pass


ApiConfigurationReference = Union[
    DropdownDependencyLink,
    EntitySchemaDependencyLink,
    ResourceDependencyLink,
    SchemaDependencyLink,
    SubdependencyLink,
    WorkflowTaskSchemaDependencyLink,
]
ConfigurationReference = Union[ApiConfigurationReference, ScalarConfig, SecureTextConfig]

AnyConfigType = TypeVar(
    "AnyConfigType",
    DropdownDependencyLink,
    EntitySchemaDependencyLink,
    ResourceDependencyLink,
    ScalarConfig,
    SecureTextConfig,
    SchemaDependencyLink,
    SubdependencyLink,
    WorkflowTaskSchemaDependencyLink,
)
ApiConfigType = TypeVar(
    "ApiConfigType",
    DropdownDependencyLink,
    EntitySchemaDependencyLink,
    ResourceDependencyLink,
    SchemaDependencyLink,
    SubdependencyLink,
    WorkflowTaskSchemaDependencyLink,
)

D = TypeVar("D", bound="BaseDependencies")


class ConfigProvider(Protocol):
    def config(self) -> BenchlingAppConfiguration:
        ...


class BenchlingConfigProvider(ConfigProvider):
    _client: Benchling
    _app_id: str

    def __init__(self, client: Benchling, app_id: str):
        self._client = client
        self._app_id = app_id

    def config(self) -> BenchlingAppConfiguration:
        app_config = self._client.apps.get_configuration_by_app_id(app_id=self._app_id)
        if not (app_config and app_config.configuration):
            raise MissingAppConfigError(
                f"The configuration for app {self._app_id} was empty or "
                f"the app may not have the necessary permissions."
            )
        return app_config


class StaticConfigProvider(ConfigProvider):
    _configuration: BenchlingAppConfiguration

    def __init__(self, configuration: BenchlingAppConfiguration):
        self._configuration = configuration

    def config(self) -> BenchlingAppConfiguration:
        return self._configuration


class DependencyLinkStore(object):
    _configuration_provider: ConfigProvider
    _configuration: Optional[BenchlingAppConfiguration] = None
    _configuration_map: Optional[Dict[str, ConfigurationReference]] = None

    def __init__(self, configuration_provider: ConfigProvider):
        self._configuration_provider = configuration_provider

    @classmethod
    def from_app(cls, client: Benchling, app_id: str) -> DependencyLinkStore:
        config_provider = BenchlingConfigProvider(client, app_id)
        return DependencyLinkStore(config_provider)

    @property
    def configuration(self) -> BenchlingAppConfiguration:
        if not self._configuration:
            self._configuration = self._configuration_provider.config()
        return self._configuration

    @property
    def config_links(self) -> Dict[str, ConfigurationReference]:
        if not self._configuration_map:
            self._configuration_map = self.map_from_configuration(self.configuration)
        return self._configuration_map

    def config_by_name(self, name: str, config_type: Type[AnyConfigType]) -> AnyConfigType:
        """
        Config by name.

        Looks up a configuration reference by its name. Only applies to named configuration at the top level,
        not subdependencies.
        """
        if name not in self.config_links:
            raise MissingDependencyError(
                f"The configuration did not have an option named '{name}'. "
                f"Valid configuration names are: {sorted(self.config_links.keys())}"
            )
        config = self.config_links[name]
        assert isinstance(config, config_type), (
            f"Expected configuration for `{name}` to be of type " f"{config_type} but found {type(config)}"
        )
        return config

    def map_from_configuration(self, config: BenchlingAppConfiguration) -> Dict[str, ConfigurationReference]:
        """
        Map from configuration.

        Produces a map of Benchling configuration references where the `name` is the key for easy lookup.
        """
        return {
            item.name: item
            # Use map to avoid MyPy thinking item can be UnknownType
            for item in map(self.to_map_value, config.configuration)
        }

    # noinspection PyMethodMayBeStatic
    def to_map_value(
        self,
        configuration_item: Union[ConfigurationReference, UnknownType],
    ) -> ConfigurationReference:
        """
        Transform configuration item for map.

        This method can be overridden to change handling of UnknownType and type safety for ConfigurationReference.
        """
        # We don't have a productive way of handling UnknownType
        if type(configuration_item) == UnknownType:
            raise UnsupportedDependencyError(
                f"Unable to read configuration with unsupported dependency {configuration_item}"
            )
        assert isinstance(
            configuration_item,
            (
                DropdownDependencyLink,
                EntitySchemaDependencyLink,
                ResourceDependencyLink,
                SchemaDependencyLink,
                ScalarConfig,
                SubdependencyLink,
                WorkflowTaskSchemaDependencyLink,
            ),
        ), f"Type of configuration was invalid {type(configuration_item)}"
        return configuration_item

    # Allow apps to live-update the values if desired
    def invalidate_cache(self) -> None:
        self._configuration = None
        self._configuration_map = None


@dataclass
class ApiDependency(ABC, Generic[ApiConfigType]):
    link: ApiConfigType


class HasLink(Protocol):
    @property
    def link(self) -> ApiConfigurationReference:
        ...


class HasEntityLink(Protocol):
    @property
    def link(self) -> Union[EntitySchemaDependencyLink, SchemaDependencyLink]:
        ...


class HasWorkflowTaskSchemaParentLink(Protocol):
    @property
    def parent(self) -> HasWorkflowTaskSchemaLink:
        ...


class HasWorkflowTaskSchemaLink(Protocol):
    @property
    def link(self) -> WorkflowTaskSchemaDependencyLink:
        ...


class HasScalarDefinition(Protocol):
    @property
    def config(self) -> ScalarConfig:
        ...

    @property
    def definition(self) -> Optional[ScalarDefinition]:
        ...


class RequiredApiDependencyMixin:
    """
    Require Api Link.

    A mixin for accessing an API link which is required and should always be present. Should
    only be mixed in with ApiDependency or another class that provides the `self.link` attribute.
    """

    @property
    def id(self: HasLink) -> str:
        # Currently, the API does not have a concept of required dependencies
        # Treat all dependencies as required for now so we don't have to null check in code
        assert self.link.resource_id is not None, f"The dependency {self.link} is not linked in Benchling"
        return self.link.resource_id

    @property
    def name(self: HasLink) -> str:
        # Currently, the API does not have a concept of required dependencies
        # Treat all dependencies as required for now so we don't have to null check in code
        assert self.link.resource_name is not None, f"The dependency {self.link} is not linked in Benchling"
        return self.link.resource_name


class RequiredScalarDependencyMixin(Generic[ScalarType]):
    """
    Require Scalar Config.

    A mixin for accessing a scalar config which is required and should always be present.
    Should only be mixed in with ScalarConfig.
    """

    @property
    def value(self: HasScalarDefinition) -> ScalarType:
        # Currently, the API does not have a concept of required dependencies
        # Treat all dependencies as required for now so we don't have to null check in code
        if self.definition:
            assert self.config.value is not None, f"The dependency {self.config} is not set in Benchling"
            optional_typed_value = self.definition.from_str(value=self.config.value)
            assert optional_typed_value is not None
            return optional_typed_value
        raise MissingScalarDefinitionError(f"No definition registered for scalar config {self.config}")

    @property
    def value_str(self: HasScalarDefinition) -> str:
        # Currently, the API does not have a concept of required dependencies
        # Treat all dependencies as required for now so we don't have to null check in code
        assert self.config.value is not None, f"The dependency {self.config} is not set in Benchling"
        # Booleans are currently specified as str in the spec but are bool at runtime in JSON
        return str(self.config.value)


class Subdependencies(ABC):
    _subdependency_map: Optional[Dict[str, SubdependencyLink]] = None

    @abstractmethod
    def subdependency_links(self) -> List[SubdependencyLink]:
        pass

    @abstractmethod
    def subdependency_type_display_name(self) -> str:
        pass

    @property
    def subdependency_mapping(self) -> Dict[str, SubdependencyLink]:
        if not self._subdependency_map:
            self._subdependency_map = {item.name: item for item in self.subdependency_links()}
        return self._subdependency_map

    def subdependency_by_name(self, name: str) -> SubdependencyLink:
        if name not in self.subdependency_mapping:
            raise MissingDependencyError(
                f"The configuration did not have a "
                f"{self.subdependency_type_display_name()} named '{name}'. "
                f"Valid {self.subdependency_type_display_name()} names are: "
                f"{sorted(self.subdependency_mapping.keys())}"
            )
        return self.subdependency_mapping[name]


class SchemaFieldsMixin(Subdependencies):
    def subdependency_links(self: HasEntityLink) -> List[SubdependencyLink]:
        return self.link.field_definitions

    def subdependency_type_display_name(self) -> str:
        return "field"


class WorkflowTaskSchemaOutputFieldsMixin(Subdependencies):
    def subdependency_links(self: HasWorkflowTaskSchemaParentLink) -> List[SubdependencyLink]:
        return self.parent.link.output.field_definitions

    def subdependency_type_display_name(self) -> str:
        return "workflow task schema output field"


@dataclass
class SchemaDependency(ApiDependency[SchemaDependencyLink], SchemaFieldsMixin):
    link: SchemaDependencyLink


@dataclass
class EntitySchemaDependency(ApiDependency[EntitySchemaDependencyLink], SchemaFieldsMixin):
    link: EntitySchemaDependencyLink


@dataclass
class DropdownDependency(ApiDependency[DropdownDependencyLink], Subdependencies):
    link: DropdownDependencyLink

    def subdependency_links(self) -> List[SubdependencyLink]:
        return self.link.options

    def subdependency_type_display_name(self) -> str:
        return "option"


@dataclass
class DropdownOptionsDependency:
    parent: DropdownDependency


@dataclass
class SchemaFieldsDependency:
    parent: Union[
        EntitySchemaDependency,
        SchemaDependency,
        WorkflowTaskSchemaDependency,
        WorkflowTaskSchemaOutputDependency,
    ]


@dataclass
class Subdependency(ApiDependency[SubdependencyLink]):
    link: SubdependencyLink


@dataclass
class ResourceDependency(ApiDependency[ResourceDependencyLink]):
    link: ResourceDependencyLink


@dataclass
class ScalarDependency:
    config: ScalarConfig
    definition: Optional[ScalarDefinition]


@dataclass
class WorkflowTaskSchemaDependency(ApiDependency[WorkflowTaskSchemaDependencyLink], SchemaFieldsMixin):
    link: WorkflowTaskSchemaDependencyLink


@dataclass
class WorkflowTaskSchemaOutputDependency(WorkflowTaskSchemaOutputFieldsMixin):
    parent: WorkflowTaskSchemaDependency


class BaseDependencies:
    _store: DependencyLinkStore
    _scalar_definitions: Dict[ScalarConfigTypes, ScalarDefinition]
    _unknown_scalar_definition: Optional[ScalarDefinition]

    def __init__(
        self,
        store: DependencyLinkStore,
        scalar_definitions: Dict[ScalarConfigTypes, ScalarDefinition] = DEFAULT_SCALAR_DEFINITIONS,
        unknown_scalar_definition: Optional[ScalarDefinition] = None,
    ):
        self._store = store
        self._scalar_definitions = scalar_definitions
        self._unknown_scalar_definition = unknown_scalar_definition

    @classmethod
    def from_app(cls: Type[D], client: Benchling, app_id: str) -> D:
        link_store = DependencyLinkStore.from_app(client=client, app_id=app_id)
        return cls(link_store)

    # Allow integrations to live-update the values if desired
    def invalidate_cache(self) -> None:
        self._store.invalidate_cache()
