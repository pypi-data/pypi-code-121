from abc import abstractmethod
from pathlib import Path
from typing import Protocol, Optional, TYPE_CHECKING, List, Dict

from pkm.api.distributions.distinfo import PackageInstallationInfo
from pkm.api.packages.package import PackageDescriptor, Package
from pkm.api.dependencies.dependency import Dependency
from pkm.api.packages.package_metadata import PackageMetadata

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment
    from pkm.api.packages.package import PackageInstallationTarget


class Distribution(Protocol):

    @property
    @abstractmethod
    def owner_package(self) -> PackageDescriptor:
        """
        :return: the package descriptor that this distribution belongs to
        """

    @abstractmethod
    def install_to(self, target: "PackageInstallationTarget", user_request: Optional[Dependency] = None,
                   installation_mode: Optional[PackageInstallationInfo] = None):
        """
        installs this package into the given `env`
        :param target: information about the target to install this distribution into
        :param user_request: if this package was requested by the user,
               supplying this field will mark the installation as user request and save the given info
        :param installation_mode: information about the installation mode to save while installing
        """

    @abstractmethod
    def extract_metadata(self, env: "Environment") -> PackageMetadata:
        """
        extracts and returns metadata from this distribution
        :param env: the environment that this metadata should be relevant to
        :return: the extracted metadata
        """

    @classmethod
    def package_from(cls, distribution: Path, desc: Optional[PackageDescriptor] = None) -> Package:
        """
        creates a package from the given distribution, assumes proper naming conventions for distribution file name
        :param distribution: the path to the distribution
        :param desc: if given, will be used as the descriptor of the package, otherwise a descriptor will be guessed
            from the file naming conventions
        :return: package that upon install will install the given distribution
        """

        from pkm.api.distributions.source_distribution import SourceDistribution
        from pkm.api.distributions.wheel_distribution import WheelDistribution

        desc = desc or PackageDescriptor.from_dist_name(distribution.name)

        if distribution.name.endswith(".whl"):
            return _DistributionPackage(WheelDistribution(desc, distribution))

        return _DistributionPackage(SourceDistribution(desc, distribution))


class _DistributionPackage(Package):

    def __init__(self, dist: Distribution):
        self._dist = dist
        self._env_hash_to_metadata: Dict[str, PackageMetadata] = {}

    @property
    def descriptor(self) -> PackageDescriptor:
        return self._dist.owner_package

    def _metadata(self, env: "Environment"):
        env_hash = env.markers_hash
        if not (meta := self._env_hash_to_metadata.get(env_hash)):
            meta = self._dist.extract_metadata(env)
            self._env_hash_to_metadata[env_hash] = meta
        return meta

    def dependencies(
            self, environment: "Environment",
            extras: Optional[List[str]] = None) -> List["Dependency"]:
        return [d for d in self.published_metadata.dependencies if d.is_applicable_for(environment, extras)]

    def is_compatible_with(self, env: "Environment") -> bool:
        from pkm.api.distributions.wheel_distribution import WheelDistribution

        if isinstance(self._dist, WheelDistribution):
            return env.compatibility_tag_score(self._dist.compute_compatibility_tags()) is not None
        return True

    def install_to(
            self, target: "PackageInstallationTarget", user_request: Optional["Dependency"] = None,
            editable: bool = False):
        self._dist.install_to(target, user_request, PackageInstallationInfo(editable=editable))
