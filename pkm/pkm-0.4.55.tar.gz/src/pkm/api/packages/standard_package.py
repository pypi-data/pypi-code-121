from abc import abstractmethod
from dataclasses import dataclass, field
from io import UnsupportedOperation
from pathlib import Path
from typing import Optional, Any, Dict, List, TYPE_CHECKING

from pkm.api.dependencies.dependency import Dependency
from pkm.api.distributions.distinfo import PackageInstallationInfo
from pkm.api.distributions.source_distribution import SourceDistribution
from pkm.api.distributions.wheel_distribution import WheelDistribution
from pkm.api.packages.package import Package, PackageDescriptor
from pkm.api.packages.package_installation import PackageInstallationTarget
from pkm.api.packages.package_metadata import PackageMetadata
from pkm.api.packages.package_monitors import PackageInstallMonitoredOp
from pkm.api.versions.version_specifiers import VersionSpecifier
from pkm.utils.hashes import HashSignature
from pkm.utils.types import Comparable

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment


@dataclass(frozen=True, eq=True)
class PackageArtifact:
    file_name: str
    requires_python: Optional[VersionSpecifier] = None
    other_info: Dict[str, Any] = field(default_factory=dict)
    hash_sig: Optional[HashSignature] = None

    def is_binary(self):
        return self.file_name.endswith(".whl")


class AbstractPackage(Package):

    def __init__(self, descriptor: PackageDescriptor, artifacts: List[PackageArtifact],
                 published_metadata: Optional[PackageMetadata] = None):
        self._descriptor = descriptor
        self._artifacts = artifacts
        self._dependencies_per_artifact_id: Dict[int, List["Dependency"]] = {}
        self._path_per_artifact_id: Dict[int, Path] = {}
        self._published_metadata = published_metadata

    @property
    def published_metadata(self) -> Optional[PackageMetadata]:
        return self._published_metadata

    @property
    def descriptor(self) -> PackageDescriptor:
        return self._descriptor

    def best_artifact_for(self, env: "Environment") -> Optional[PackageArtifact]:
        """
        searches for the best artifact that compatible with `env`
        :param env: the environment that the searched artifact should be compatible with
        :return: the best artifact found or None if no compatible artifact exists
        """

        env_interpreter = env.interpreter_version

        source_dist: Optional[PackageArtifact] = None
        best_binary_dist: Optional[PackageArtifact] = None
        best_binary_dist_score: Optional[Comparable] = None

        for artifact in self._artifacts:
            requires_python = artifact.requires_python

            file_name: str = artifact.file_name
            is_binary = artifact.is_binary()

            if requires_python:
                try:
                    if not requires_python.allows_version(env_interpreter):
                        continue
                except ValueError:
                    print(
                        'could not parse python requirements for artifact:'
                        f' {file_name} of {self.name}=={self.version}, skipping it')
                    continue

            if is_binary:
                ctag = WheelDistribution.extract_compatibility_tags_of(Path(file_name))
                if (score := env.compatibility_tag_score(ctag)) is not None:
                    if best_binary_dist_score is None or best_binary_dist_score < score:
                        best_binary_dist = artifact
                        best_binary_dist_score = score

            else:
                source_dist = artifact

        return best_binary_dist or source_dist

    def is_compatible_with(self, env: "Environment"):
        return self.best_artifact_for(env) is not None

    @abstractmethod
    def _retrieve_artifact(self, artifact: PackageArtifact) -> Path:
        """
        retrieve the given artifact, storing it to the file system and returning it
        :param artifact: the artifact to retrieve
        :return: the stored artifact
        """

    def install_to(
            self, target: PackageInstallationTarget, user_request: Optional["Dependency"] = None,
            editable: bool = False):

        with PackageInstallMonitoredOp(self.descriptor):
            artifact = self.best_artifact_for(target.env)
            artifact_path = self._get_or_retrieve_artifact_path(artifact)
            if hashsig := artifact.hash_sig:
                if not hashsig.validate_against(artifact_path):
                    raise ValueError(f"Security Risk: invalid hash for {self.descriptor}")

            installation_mode = PackageInstallationInfo(False, editable)
            if artifact.is_binary():
                WheelDistribution(self.descriptor, artifact_path).install_to(target, user_request, installation_mode)
            else:
                SourceDistribution(self.descriptor, artifact_path).install_to(target, user_request, installation_mode)

    def _get_or_retrieve_artifact_path(self, artifact: PackageArtifact):
        if not (artifact_path := self._path_per_artifact_id.get(id(artifact))):
            artifact_path = self._retrieve_artifact(artifact)

            self._path_per_artifact_id[id(artifact)] = artifact_path
        return artifact_path

    def dependencies(
            self, environment: "Environment", extras: Optional[List[str]] = None) -> List["Dependency"]:
        all_deps = self._unfiltered_dependencies(environment)
        return [d for d in all_deps if d.is_applicable_for(environment, extras)]

    def _unfiltered_dependencies(self, environment: "Environment") -> List["Dependency"]:
        artifact = self.best_artifact_for(environment)
        if not artifact:
            raise UnsupportedOperation(
                "attempting to compute dependencies for environment that is not supported by this package")

        if deps := self._dependencies_per_artifact_id.get(id(artifact)):
            return deps
        resource = self._get_or_retrieve_artifact_path(artifact)
        filename = artifact.file_name
        if filename.endswith('.whl'):
            info = WheelDistribution(self.descriptor, resource) \
                .extract_metadata(environment)
        else:
            info = SourceDistribution(self.descriptor, resource) \
                .extract_metadata(environment)

        self._dependencies_per_artifact_id[id(artifact)] = info.dependencies
        return info.dependencies
