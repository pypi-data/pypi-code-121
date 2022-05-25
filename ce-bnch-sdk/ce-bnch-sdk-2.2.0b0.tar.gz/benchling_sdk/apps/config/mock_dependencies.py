from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
import random
import string
from typing import Optional, Union

from benchling_api_client.v2.alpha.models.base_manifest_config import BaseManifestConfig
from benchling_api_client.v2.alpha.models.benchling_app_manifest import BenchlingAppManifest
from benchling_api_client.v2.alpha.models.dropdown_dependency import DropdownDependency
from benchling_api_client.v2.alpha.models.entity_schema_dependency import EntitySchemaDependency
from benchling_api_client.v2.alpha.models.entity_schema_dependency_link_type import (
    EntitySchemaDependencyLinkType,
)
from benchling_api_client.v2.alpha.models.manifest_scalar_config import ManifestScalarConfig
from benchling_api_client.v2.alpha.models.resource_dependency import ResourceDependency
from benchling_api_client.v2.alpha.models.schema_dependency import SchemaDependency
from benchling_api_client.v2.alpha.models.workflow_task_schema_dependency import WorkflowTaskSchemaDependency
from benchling_api_client.v2.beta.models.benchling_app_configuration import BenchlingAppConfiguration
from benchling_api_client.v2.beta.models.dropdown_dependency_link import DropdownDependencyLink
from benchling_api_client.v2.beta.models.entity_schema_dependency_link import EntitySchemaDependencyLink
from benchling_api_client.v2.beta.models.resource_dependency_link import ResourceDependencyLink
from benchling_api_client.v2.beta.models.scalar_config import ScalarConfig
from benchling_api_client.v2.beta.models.scalar_config_types import ScalarConfigTypes
from benchling_api_client.v2.beta.models.schema_dependency_link import SchemaDependencyLink
from benchling_api_client.v2.beta.models.subdependency_link import SubdependencyLink
from benchling_api_client.v2.beta.models.workflow_task_schema_dependency_link import (
    WorkflowTaskSchemaDependencyLink,
)
from benchling_api_client.v2.beta.models.workflow_task_schema_dependency_link_output import (
    WorkflowTaskSchemaDependencyLinkOutput,
)
from benchling_api_client.v2.beta.models.workflow_task_schema_dependency_link_type import (
    WorkflowTaskSchemaDependencyLinkType,
)
from benchling_api_client.v2.stable.extensions import UnknownType

from benchling_sdk.apps.config.scalars import DateTimeScalar
from benchling_sdk.apps.helpers.config_helpers import (
    field_definitions_from_dependency,
    options_from_dependency,
    workflow_task_schema_output_from_dependency,
)

ManifestDependencies = Union[
    DropdownDependency,
    EntitySchemaDependency,
    ManifestScalarConfig,
    ResourceDependency,
    SchemaDependency,
    WorkflowTaskSchemaDependency,
    UnknownType,
]


class ReplaceSubdependency(ABC):
    @abstractmethod
    def with_subdependency(self, name: str, dependency: MockSubdependencyLink):
        """Return a new dependency with a specific subdependency updated with the specified mock."""
        pass


class MockDropdownDependencyLink(DropdownDependencyLink, ReplaceSubdependency):
    @classmethod
    def from_dependency(cls, dependency: DropdownDependency) -> MockDropdownDependencyLink:
        mock_options = [
            MockSubdependencyLink.from_dependency(subdependency)
            for subdependency in options_from_dependency(dependency)
        ]
        return cls(
            type=dependency.type,
            name=dependency.name,
            resource_id=random_string("id"),
            resource_name=random_string("name"),
            # list() solves '"List" is invariant type error'
            options=list(mock_options),
        )

    def with_subdependency(self, name: str, dependency: MockSubdependencyLink) -> MockDropdownDependencyLink:
        """Return a new dependency with a specific subdependency updated with the specified mock."""
        updated_subdependencies = [
            dependency
            if not isinstance(current_dependency, UnknownType) and current_dependency.name == name
            else current_dependency
            for current_dependency in self.options
        ]
        return MockDropdownDependencyLink(
            type=self.type,
            name=self.name,
            resource_id=self.resource_id,
            resource_name=self.resource_name,
            # list() solves '"List" is invariant type error'
            options=list(updated_subdependencies),
        )


class MockEntitySchemaDependencyLink(EntitySchemaDependencyLink, ReplaceSubdependency):
    @classmethod
    def from_dependency(cls, dependency: EntitySchemaDependency) -> MockEntitySchemaDependencyLink:
        mock_field_definitions = [
            MockSubdependencyLink.from_dependency(field)
            for field in field_definitions_from_dependency(dependency)
        ]
        return cls(
            type=EntitySchemaDependencyLinkType.ENTITY_SCHEMA,
            subtype=dependency.subtype,
            name=dependency.name,
            resource_id=random_string("id"),
            resource_name=random_string("name"),
            field_definitions=list(mock_field_definitions),  # list() solves '"List" is invariant type error'
        )

    def with_subdependency(
        self, name: str, dependency: MockSubdependencyLink
    ) -> MockEntitySchemaDependencyLink:
        """Return a new dependency with a specific subdependency updated with the specified mock."""
        updated_subdependencies = [
            dependency
            if not isinstance(current_dependency, UnknownType) and current_dependency.name == name
            else current_dependency
            for current_dependency in self.field_definitions
        ]
        return MockEntitySchemaDependencyLink(
            type=self.type,
            subtype=self.subtype,
            name=self.name,
            resource_id=self.resource_id,
            resource_name=self.resource_name,
            field_definitions=updated_subdependencies,
        )


class MockScalarConfig(ScalarConfig):
    @classmethod
    def from_dependency(cls, dependency: ManifestScalarConfig) -> MockScalarConfig:
        return cls(
            type=dependency.type,
            name=dependency.name,
            value=mock_scalar_value(dependency.type),
        )


class MockResourceDependencyLink(ResourceDependencyLink):
    @classmethod
    def from_dependency(cls, dependency: ResourceDependency) -> MockResourceDependencyLink:
        return cls(
            type=dependency.type,
            name=dependency.name,
            resource_id=random_string("id"),
            resource_name=random_string("name"),
        )


class MockSchemaDependencyLink(SchemaDependencyLink, ReplaceSubdependency):
    @classmethod
    def from_dependency(cls, dependency: SchemaDependency) -> MockSchemaDependencyLink:
        mock_field_definitions = [
            MockSubdependencyLink.from_dependency(field)
            for field in field_definitions_from_dependency(dependency)
        ]
        return cls(
            type=dependency.type,
            name=dependency.name,
            resource_id=random_string("id"),
            resource_name=random_string("name"),
            # list() solves '"List" is invariant type error'
            field_definitions=list(mock_field_definitions),
        )

    def with_subdependency(self, name: str, dependency: MockSubdependencyLink) -> MockSchemaDependencyLink:
        """Return a new dependency with a specific subdependency updated with the specified mock."""
        updated_subdependencies = [
            dependency
            if not isinstance(current_dependency, UnknownType) and current_dependency.name == name
            else current_dependency
            for current_dependency in self.field_definitions
        ]
        return MockSchemaDependencyLink(
            type=self.type,
            name=self.name,
            resource_id=self.resource_id,
            resource_name=self.resource_name,
            field_definitions=updated_subdependencies,
        )


class MockSubdependencyLink(SubdependencyLink):
    @classmethod
    def from_dependency(cls, dependency: BaseManifestConfig) -> MockSubdependencyLink:
        return cls(
            name=dependency.name,
            resource_id=random_string("id"),
            resource_name=random_string("name"),
        )


class MockWorkflowTaskSchemaDependencyLink(WorkflowTaskSchemaDependencyLink, ReplaceSubdependency):
    @classmethod
    def from_dependency(
        cls, dependency: WorkflowTaskSchemaDependency
    ) -> MockWorkflowTaskSchemaDependencyLink:
        mock_field_definitions = [
            MockSubdependencyLink.from_dependency(field)
            for field in field_definitions_from_dependency(dependency)
        ]
        return cls(
            name=dependency.name,
            type=WorkflowTaskSchemaDependencyLinkType.WORKFLOW_TASK_SCHEMA,
            resource_id=random_string("id"),
            resource_name=random_string("name"),
            output=MockWorkflowTaskSchemaOutputDependency.from_dependency(dependency),
            field_definitions=list(mock_field_definitions),  # list() solves '"List" is invariant type error'
        )

    def with_subdependency(
        self, name: str, dependency: MockSubdependencyLink
    ) -> MockWorkflowTaskSchemaDependencyLink:
        """Return a new dependency with a specific subdependency updated with the specified mock."""
        updated_subdependencies = [
            dependency
            if not isinstance(current_dependency, UnknownType) and current_dependency.name == name
            else current_dependency
            for current_dependency in self.field_definitions
        ]
        return MockWorkflowTaskSchemaDependencyLink(
            name=self.name,
            resource_id=self.resource_id,
            resource_name=self.resource_name,
            field_definitions=updated_subdependencies,
        )


class MockWorkflowTaskSchemaOutputDependency(WorkflowTaskSchemaDependencyLinkOutput):
    @classmethod
    def from_dependency(
        cls, dependency: WorkflowTaskSchemaDependency
    ) -> MockWorkflowTaskSchemaOutputDependency:
        workflow_output = workflow_task_schema_output_from_dependency(dependency)
        mock_field_definitions = (
            [
                MockSubdependencyLink.from_dependency(field)
                for field in field_definitions_from_dependency(workflow_output)
            ]
            if workflow_output
            else []
        )
        return cls(list(mock_field_definitions))  # list() solves '"List" is invariant type error'


MockDependencies = Union[
    MockDropdownDependencyLink,
    MockEntitySchemaDependencyLink,
    MockResourceDependencyLink,
    MockScalarConfig,
    MockSchemaDependencyLink,
    MockWorkflowTaskSchemaDependencyLink,
]


class MockBenchlingAppConfig(BenchlingAppConfiguration):
    @classmethod
    def from_manifest(cls, manifest: BenchlingAppManifest) -> MockBenchlingAppConfig:
        mocked_links = [mock_dependency(dependency) for dependency in manifest.configuration]
        # list() solves '"List" is invariant type error'
        return cls(id=random_string("manifest-id"), configuration=list(mocked_links))

    def with_dependency(self, name: str, dependency: MockDependencies) -> BenchlingAppConfiguration:
        """Return MockBenchlingAppConfig with a specific dependency updated with the specified mock."""
        updated_config = [
            dependency
            if not isinstance(current_dependency, UnknownType) and current_dependency.name == name
            else current_dependency
            for current_dependency in self.configuration
        ]
        return MockBenchlingAppConfig(id=self.id, configuration=updated_config)

    def dependency_by_name(self, name: str) -> Optional[MockDependencies]:
        for dependency in self.configuration:
            if not isinstance(dependency, UnknownType) and dependency.name == name:
                assert isinstance(
                    dependency,
                    (
                        MockDropdownDependencyLink,
                        MockEntitySchemaDependencyLink,
                        MockResourceDependencyLink,
                        MockScalarConfig,
                        MockSchemaDependencyLink,
                        MockWorkflowTaskSchemaDependencyLink,
                    ),
                )
                return dependency
        return None


def mock_dependency(
    dependency: ManifestDependencies,
) -> Union[
    MockDropdownDependencyLink,
    MockEntitySchemaDependencyLink,
    MockScalarConfig,
    MockResourceDependencyLink,
    MockSchemaDependencyLink,
    UnknownType,
]:
    if isinstance(dependency, DropdownDependency):
        return MockDropdownDependencyLink.from_dependency(dependency)
    if isinstance(dependency, EntitySchemaDependency):
        return MockEntitySchemaDependencyLink.from_dependency(dependency)
    if isinstance(dependency, ManifestScalarConfig):
        return MockScalarConfig.from_dependency(dependency)
    if isinstance(dependency, ResourceDependency):
        return MockResourceDependencyLink.from_dependency(dependency)
    if isinstance(dependency, SchemaDependency):
        return MockSchemaDependencyLink.from_dependency(dependency)
    if isinstance(dependency, WorkflowTaskSchemaDependency):
        return MockWorkflowTaskSchemaDependencyLink.from_dependency(dependency)
    if isinstance(dependency, UnknownType):
        return UnknownType(value="Unknown")


def mock_scalar_value(scalar_type: ScalarConfigTypes) -> Optional[str]:
    if scalar_type == scalar_type.BOOLEAN:
        return "true"
    elif scalar_type == scalar_type.DATE:
        return date.today().strftime("%Y-%m-%d")
    elif scalar_type == scalar_type.DATETIME:
        return datetime.now().strftime(DateTimeScalar.expected_format())
    elif scalar_type == scalar_type.FLOAT:
        return str(random.random())
    elif scalar_type == scalar_type.INTEGER:
        return str(random.randint(-1000, 1000))
    return random_string()


def random_string(prefix: str = "", random_length: int = 20) -> str:
    delimited_prefix = f"{prefix}-" if prefix else ""
    return f"{delimited_prefix}{''.join(random.choice(string.ascii_letters) for i in range(random_length))}"
