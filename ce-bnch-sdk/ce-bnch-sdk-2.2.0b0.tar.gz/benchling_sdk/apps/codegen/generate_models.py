from typing import Dict, Union

from benchling_api_client.v2.alpha.models.benchling_app_manifest import BenchlingAppManifest
from benchling_api_client.v2.alpha.models.dropdown_dependency import DropdownDependency
from benchling_api_client.v2.alpha.models.entity_schema_dependency import EntitySchemaDependency
from benchling_api_client.v2.alpha.models.schema_dependency import SchemaDependency
from jinja2 import Environment, PackageLoader

from benchling_sdk.apps.codegen.helpers import reformat_code_str
from benchling_sdk.apps.helpers.code_format_helpers import (
    dependency_to_pascal_case,
    dependency_to_snake_case,
    to_snake_case,
)
from benchling_sdk.apps.helpers.config_helpers import (
    field_definitions_from_dependency,
    model_type_from_dependency,
)


def generate_model(dependency: Union[DropdownDependency, EntitySchemaDependency, SchemaDependency]) -> str:
    env = Environment(
        loader=PackageLoader("benchling_sdk.apps.codegen", "templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    if isinstance(dependency, (EntitySchemaDependency, SchemaDependency)):
        template = env.get_template("schema_instance_model.py.jinja2")
    else:
        template = env.get_template("dropdown_model.py.jinja2")

    rendered_template = template.render(
        dependency=dependency,
        dependency_to_pascal_case=dependency_to_pascal_case,
        dependency_to_snake_case=dependency_to_snake_case,
        model_type_from_dependency=model_type_from_dependency,
        to_snake_case=to_snake_case,
    )

    return reformat_code_str(rendered_template)


def generate_models(manifest: BenchlingAppManifest) -> Dict[str, str]:
    assert manifest.configuration
    return {
        dependency_to_snake_case(dependency): generate_model(dependency)
        for dependency in manifest.configuration
        if isinstance(dependency, (EntitySchemaDependency, SchemaDependency, DropdownDependency))
        and _has_subdependencies(dependency)
    }


def _has_subdependencies(dependency) -> bool:
    return (
        isinstance(dependency, (EntitySchemaDependency, SchemaDependency))
        and bool(field_definitions_from_dependency(dependency))
    ) or isinstance(dependency, DropdownDependency)
