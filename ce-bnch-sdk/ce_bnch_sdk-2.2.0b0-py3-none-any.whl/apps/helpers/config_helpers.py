from datetime import date, datetime
from typing import List, Optional, Type, Union

from benchling_api_client.v2.alpha.models.base_manifest_config import BaseManifestConfig
from benchling_api_client.v2.alpha.models.dropdown_dependency import DropdownDependency
from benchling_api_client.v2.alpha.models.entity_schema_dependency import EntitySchemaDependency
from benchling_api_client.v2.alpha.models.schema_dependency import SchemaDependency
from benchling_api_client.v2.alpha.models.schema_dependency_subtypes import SchemaDependencySubtypes
from benchling_api_client.v2.alpha.models.schema_dependency_types import SchemaDependencyTypes
from benchling_api_client.v2.alpha.models.workflow_task_schema_dependency import WorkflowTaskSchemaDependency
from benchling_api_client.v2.alpha.models.workflow_task_schema_dependency_output import (
    WorkflowTaskSchemaDependencyOutput,
)
from benchling_api_client.v2.beta.models.scalar_config import ScalarConfig
from benchling_api_client.v2.beta.models.scalar_config_types import ScalarConfigTypes
from benchling_api_client.v2.stable.extensions import NotPresentError

from benchling_sdk.apps.config.scalars import ScalarModelType
from benchling_sdk.models import (
    AaSequence,
    AssayResult,
    AssayRun,
    Box,
    Container,
    CustomEntity,
    DnaSequence,
    Entry,
    Location,
    Mixture,
    Plate,
    Request,
)

_MODEL_TYPES_FROM_SCHEMA_TYPE = {
    SchemaDependencyTypes.CONTAINER_SCHEMA: Container,
    SchemaDependencyTypes.PLATE_SCHEMA: Plate,
    SchemaDependencyTypes.BOX_SCHEMA: Box,
    SchemaDependencyTypes.LOCATION_SCHEMA: Location,
    SchemaDependencyTypes.ENTRY_SCHEMA: Entry,
    SchemaDependencyTypes.REQUEST_SCHEMA: Request,
    SchemaDependencyTypes.RESULT_SCHEMA: AssayResult,
    SchemaDependencyTypes.RUN_SCHEMA: AssayRun,
    # TODO BNCH-35570 Missing from Enum
    # SchemaType.WORKFLOW_TASK_SCHEMA: WorkflowTask,
}


_SCALAR_TYPES_FROM_CONFIG = {
    ScalarConfigTypes.BOOLEAN: bool,
    ScalarConfigTypes.DATE: date,
    ScalarConfigTypes.DATETIME: datetime,
    ScalarConfigTypes.FLOAT: float,
    ScalarConfigTypes.INTEGER: int,
    ScalarConfigTypes.TEXT: str,
}

ModelType = Union[AssayResult, AssayRun, Box, Container, Entry, Location, Plate, Request]

_INSTANCE_FROM_SCHEMA_SUBTYPE = {
    SchemaDependencySubtypes.AA_SEQUENCE: AaSequence,
    SchemaDependencySubtypes.CUSTOM_ENTITY: CustomEntity,
    SchemaDependencySubtypes.DNA_SEQUENCE: DnaSequence,
    SchemaDependencySubtypes.MIXTURE: Mixture,
    # TODO BNCH-38994 Support for DNA/RNA Oligos and Molecules
}

EntitySubtype = Union[AaSequence, CustomEntity, DnaSequence, Mixture]


class UnsupportedSubTypeError(Exception):
    pass


def model_type_from_dependency(
    dependency: Union[EntitySchemaDependency, SchemaDependency]
) -> Type[Union[ModelType, EntitySubtype]]:
    if isinstance(dependency, EntitySchemaDependency):
        model_type = _subtype_instance_from_dependency(dependency)
    else:
        model_type = _MODEL_TYPES_FROM_SCHEMA_TYPE[dependency.type]
    return model_type


def scalar_type_from_config(config: ScalarConfig) -> Type[ScalarModelType]:
    return _SCALAR_TYPES_FROM_CONFIG.get(config.type, str)


def field_definitions_from_dependency(
    dependency: Union[
        EntitySchemaDependency,
        SchemaDependency,
        WorkflowTaskSchemaDependency,
        WorkflowTaskSchemaDependencyOutput,
    ]
) -> List[BaseManifestConfig]:
    try:
        if hasattr(dependency, "field_definitions"):
            return dependency.field_definitions
    # We can't seem to handle this programmatically by checking isinstance() or field truthiness
    except NotPresentError:
        pass
    return []


def workflow_task_schema_output_from_dependency(
    dependency: WorkflowTaskSchemaDependency,
) -> Optional[WorkflowTaskSchemaDependencyOutput]:
    try:
        if hasattr(dependency, "output"):
            return dependency.output
    # We can't seem to handle this programmatically by checking isinstance() or output truthiness
    except NotPresentError:
        pass
    return None


def options_from_dependency(dependency: DropdownDependency) -> List[BaseManifestConfig]:
    try:
        if hasattr(dependency, "options"):
            return dependency.options
    # We can't seem to handle this programmatically by checking isinstance() or field truthiness
    except NotPresentError:
        pass
    return []


def _subtype_instance_from_dependency(dependency: EntitySchemaDependency) -> Type[EntitySubtype]:
    if dependency.subtype in _INSTANCE_FROM_SCHEMA_SUBTYPE:
        return _INSTANCE_FROM_SCHEMA_SUBTYPE[dependency.subtype]
    # This would mean the spec has a new subtype, the manifest installed in Benchling has declared it,
    # the user has linked it in Benchling, but the app code receiving it was never updated.
    # App developers should support it in deployed app code before republishing the manifest.
    raise UnsupportedSubTypeError(
        f"An unsupported subtype, {dependency.subtype.value} was received. "
        f"The version of the SDK may need to be upgraded to support this."
    )
