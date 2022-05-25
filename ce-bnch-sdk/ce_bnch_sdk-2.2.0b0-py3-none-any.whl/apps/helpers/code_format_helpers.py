from dataclasses import dataclass
from keyword import iskeyword
import re
from typing import List, Union

from benchling_api_client.v2.alpha.models.base_manifest_config import BaseManifestConfig
from benchling_api_client.v2.alpha.models.dropdown_dependency import DropdownDependency
from benchling_api_client.v2.alpha.models.entity_schema_dependency import EntitySchemaDependency
from benchling_api_client.v2.alpha.models.manifest_scalar_config import ManifestScalarConfig
from benchling_api_client.v2.alpha.models.resource_dependency import ResourceDependency
from benchling_api_client.v2.alpha.models.schema_dependency import SchemaDependency

DependencyType = Union[
    SchemaDependency,
    DropdownDependency,
    EntitySchemaDependency,
    ResourceDependency,
    ManifestScalarConfig,
    BaseManifestConfig,
]


class UnnamedDependencyError(Exception):
    pass


def _clean_and_split(string: str) -> List[str]:
    remove_symbols = re.sub(r"[\W_]", " ", string)
    insert_space_before_uppercase = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", remove_symbols)
    return insert_space_before_uppercase.split()


def _make_valid_identifier(string: str) -> str:
    # If it starts with a digit, prefix with _
    identifier = re.sub(r"^(?=\d)", "_", string)

    if iskeyword(identifier) or identifier == "self" or identifier in dir(dataclass):
        return f"{identifier}_"
    else:
        return identifier


def to_pascal_case(string: str) -> str:
    return _make_valid_identifier("".join([word.title() for word in _clean_and_split(string)]))


def to_snake_case(string: str) -> str:
    return _make_valid_identifier("_".join([word.lower() for word in _clean_and_split(string)]))


def dependency_to_pascal_case(dependency: DependencyType) -> str:
    if not hasattr(dependency, "name"):
        raise UnnamedDependencyError(f"No name available for unknown dependency: {dependency}")
    return to_pascal_case(dependency.name)


def dependency_to_snake_case(dependency: DependencyType) -> str:
    if not hasattr(dependency, "name"):
        raise UnnamedDependencyError(f"No name available for unknown dependency: {dependency}")
    return to_snake_case(dependency.name)
