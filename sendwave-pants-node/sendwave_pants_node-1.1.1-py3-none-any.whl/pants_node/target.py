from dataclasses import dataclass

import pants.core.goals.package
from pants.core.goals.package import (BuiltPackage, BuiltPackageArtifact,
                                      OutputPathField, PackageFieldSet)
from pants.engine.target import (COMMON_TARGET_FIELDS, Dependencies,
                                 DependenciesRequest, DescriptionField,
                                 HydratedSources, HydrateSourcesRequest,
                                 MultipleSourcesField,
                                 SpecialCasedDependencies, StringField,
                                 StringSequenceField, Tags, Target, Targets,
                                 TransitiveTargets, TransitiveTargetsRequest)
from pants.engine.unions import UnionRule


class NodeLibrarySourcesField(MultipleSourcesField):
    help = "File extensions that should be bundled by webpack"
    default = ("*.js", "*.css", "*.html", "package.json", "package-lock.json")


class NodeLibrary(Target):
    help = "Collection of sources to include in a webpack bundle"
    alias = "node_library"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
        NodeLibrarySourcesField,
    )


class NodeProjectDependencies(Dependencies):
    pass


class NodeArtifactPathsField(StringSequenceField):
    help = "the locations of generated files created by npm run-script pants:build, required for ./pants package to work"
    alias = "artifact_paths"
    required = True


class NodePackage(Target):
    help = "Package together your Node libraries into a bundle! Who knows how js development works"
    alias = "node_package"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        NodeProjectDependencies,
        NodeArtifactPathsField,
        OutputPathField,
    )


@dataclass(frozen=True)
class NodeProjectFieldSet(PackageFieldSet):
    required_fields = (NodeProjectDependencies, NodeArtifactPathsField)
    dependencies: NodeProjectDependencies
    artifact_paths: NodeArtifactPathsField
    output_path: OutputPathField


def rules():
    return [
        UnionRule(PackageFieldSet, NodeProjectFieldSet),
    ]
