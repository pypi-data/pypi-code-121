"""Rules to package node_package targets.

These rules provide the functionality to collect node_library sources,
install npm dependencies, run a node script on the collected code, and
extract the output. The generated bundles/files can be used either as
normal `pants package` calls, or included in a docker container, by
making the node_package target a dependency of the docker target.
"""
import logging
from dataclasses import dataclass
from pathlib import PurePath
from typing import Tuple

from pants.core.goals.package import (BuiltPackage, BuiltPackageArtifact,
                                      PackageFieldSet)
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.environment import Environment, EnvironmentRequest
from pants.engine.fs import (AddPrefix, CreateDigest, Digest, DigestEntries,
                             FileEntry, MergeDigests, RemovePrefix, Snapshot)
from pants.engine.process import (BinaryPathRequest, BinaryPaths, Process,
                                  ProcessResult)
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import (Address, TransitiveTargets,
                                 TransitiveTargetsRequest)
from pants.engine.unions import UnionRule
from pants.source.source_root import SourceRootsRequest, SourceRootsResult
from sendwave.pants_docker.docker_component import (DockerComponent,
                                                    DockerComponentFieldSet)
from sendwave.pants_node.subsystems import NodeSubsystem

from .target import NodeLibrarySourcesField, NodeProjectFieldSet

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StripSourceRoots:
    """Request to strip the source root from every file in the given digest."""

    digest: Digest


@rule
async def strip_source_roots(snapshot_to_strip: StripSourceRoots) -> Digest:
    """Remove Source Root[0] from every item in the passed in digest.

    This can be useful since, for example, python code copied into a
    docker container using the pants-docker plugin will already have
    it's source root stripped. So for the built files to be cleanly
    layered in to the docker container we should also strip the source
    roots. There isn't a clean way to do that without using a
    SourceFiles request, Which I don't think we can create for the new
    files. Anyway this goes through and finds the root for each item
    in a digest, and removes the source root.

    [0] https://www.pantsbuild.org/v2.9/docs/source-roots
    """
    entries = await Get(DigestEntries, Digest, snapshot_to_strip.digest)
    file_paths, dir_paths = [], []
    for e in entries:
        path = PurePath(e.path)
        if isinstance(e, FileEntry):
            file_paths.append(path)
        else:
            dir_paths.append(path)
    root_result = await Get(
        SourceRootsResult, SourceRootsRequest(files=file_paths, dirs=dir_paths)
    )
    roots = root_result.path_to_root
    roots_to_entries = {root: [] for (files, root) in roots.items()}

    # collect every output item in the digest by its source root
    for entry in entries:
        roots_to_entries[roots[PurePath(entry.path)]].append(entry)

    stripped_digests = []
    for root, entries in roots_to_entries.items():
        # create a separate digest for each source root
        digest = await Get(Digest, CreateDigest(entries))
        # remove the source root from the digest
        stripped_digests.append((await Get(Digest, RemovePrefix(digest, root.path))))
    # merge the digests together together
    return await Get(Digest, MergeDigests(stripped_digests))


@dataclass(frozen=True)
class NPMPathRequest:
    """Empty request to get NodePaths.

    Get requires an argument, but all our configuration is in the
    NodeSubsystem which is injected separately. So this is just a type
    marker to tell pants how to give us what we want.
    """

    pass


@dataclass(frozen=True)
class NPMPath:
    """Path to npm executable + search path for launched processes."""

    binary_path: str
    search_paths: Tuple[str]


@rule
async def get_node_search_paths(
    request: NPMPathRequest, node: NodeSubsystem
) -> NPMPath:
    """Build NPMPath object from NodeSubsystem configuration."""
    use_nvm = node.options.use_nvm
    if use_nvm:
        nvm_bin = await Get(Environment, EnvironmentRequest(["NVM_BIN"]))
        if nvm_bin:
            search_paths = [nvm_bin["NVM_BIN"], *node.options.search_paths]
    else:
        search_paths = tuple(node.options.search_paths)

    npm_paths = await Get(
        BinaryPaths,
        BinaryPathRequest(
            binary_name="npm",
            search_path=search_paths,
        ),
    )
    if not npm_paths.first_path:
        raise ValueError(
            "Could not find npm in: ({}) cannot create package".format(search_paths)
        )
    return NPMPath(binary_path=npm_paths.first_path.path, search_paths=search_paths)


@dataclass(frozen=True)
class NodeSourceFilesRequest:
    """Get all tranisitvely dependent source files for given node package."""

    package_address: Address


@rule
async def get_node_package_file_sources(request: NodeSourceFilesRequest) -> SourceFiles:
    """Transitively looks up all source files for the node package."""
    transitive_targets = await Get(
        TransitiveTargets, TransitiveTargetsRequest([request.package_address])
    )
    all_sources = [
        t.get(NodeLibrarySourcesField)
        for t in transitive_targets.closure
        if t.has_field(NodeLibrarySourcesField)
    ]
    return await Get(SourceFiles, SourceFilesRequest(all_sources))


def log_console_output(output: bytes) -> None:
    """Log bytes from console output.

    also replaces double escaped newlines.
    """
    logger.info(output.decode("utf-8").replace("\\n", "\n"))


@rule
async def get_node_package_digest(field_set: NodeProjectFieldSet) -> Digest:
    """Build & retrieve output from a node_package target.

    This is the main function of the pants-node plugin. It evaluates
    the following steps:

    1) Fetch all source files for the target

    2) Roots all the files at the definition of the node_package
    target. This means that when we run npm it will be as if we are
    running it in the directory the node_package target was defined.

    3) Lookup the locations of installed npm using the NodeSubsytem
    configuration

    4) run npm install using the system npm, and copy the resulting
    node modules. NOTE: due to [1] we disable symlinks when running
    npm install.

    5) run `npm run-scripts pants:build` in a build context created by
    merging the stripped source files with the newly installed
    node_modules directory. When done we extract everything from the
    'artifact_paths' field on the target as the package output.

    6a) if an output_path is configured we add that to the generated files

    6b) if an output path is not configured we add the package root
    back to the newly created files and then strip the source roots
    from the generated files (since these will generally be stripped
    in other types of packaging and we would like the distributions
    from this plugin to be overlaid onto those other package
    (i.e. with the pants-docker integration)
    """
    package_root = field_set.address.spec_path
    artifact_paths = field_set.artifact_paths.value
    source_files = await Get(SourceFiles, NodeSourceFilesRequest(field_set.address))
    stripped_files = await Get(
        Snapshot, RemovePrefix(source_files.snapshot.digest, package_root)
    )
    node_paths = await Get(NPMPath, NPMPathRequest())
    npm_path = node_paths.binary_path
    search_path = ":".join(node_paths.search_paths)
    logger.info(
        "Using npm at {npm_path} ($PATH={search_paths})".format(
            npm_path=npm_path, search_paths=node_paths.search_paths
        )
    )
    npm_install_result = await Get(
        ProcessResult,
        Process(
            argv=[npm_path, "install", "--no-bin-links"],
            output_directories=["./node_modules"],
            input_digest=stripped_files.digest,
            env={"PATH": search_path},
            description="installing node project dependencies",
        ),
    )
    log_console_output(npm_install_result.stdout)
    build_context = await Get(
        Digest, MergeDigests([stripped_files.digest, npm_install_result.output_digest])
    )
    build_result = await Get(
        ProcessResult,
        Process(
            description="Running npm run-script pants:build",
            argv=[npm_path, "run-script", "pants:build"],
            input_digest=build_context,
            output_directories=artifact_paths,
            env={"PATH": search_path},
        ),
    )
    log_console_output(build_result.stdout)
    if field_set.output_path and field_set.output_path.value is not None:
        return await Get(
            Digest, AddPrefix(build_result.output_digest, field_set.output_path.value)
        )
    else:
        output = await Get(Digest, AddPrefix(build_result.output_digest, package_root))
        return await Get(Digest, StripSourceRoots(digest=output))


@rule
async def node_project_package(field_set: NodeProjectFieldSet) -> BuiltPackage:
    """Build a node_package target into a BuiltPackage."""
    package = await Get(Snapshot, NodeProjectFieldSet, field_set)
    return BuiltPackage(
        digest=package.digest,
        artifacts=tuple(BuiltPackageArtifact(f) for f in package.files),
    )


@rule
async def node_project_docker(field_set: NodeProjectFieldSet) -> DockerComponent:
    """Build a node_package target into a DockerComponent.

    This allows files generated by the node process to be included in
    the docker image.
    """
    package = await Get(Digest, NodeProjectFieldSet, field_set)
    return DockerComponent(sources=package, commands=[])


def rules():
    """Return the pants rules for this module."""
    return [
        UnionRule(PackageFieldSet, NodeProjectFieldSet),
        UnionRule(DockerComponentFieldSet, NodeProjectFieldSet),
        *collect_rules(),
    ]
