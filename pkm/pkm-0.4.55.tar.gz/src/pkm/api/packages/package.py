from __future__ import annotations

import re
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from pkm.api.versions.version import Version
from pkm.api.versions.version_specifiers import VersionMatch
from pkm.utils.commons import UnsupportedOperationException

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment
    from pkm.api.dependencies.dependency import Dependency
    from pkm.api.packages.package_metadata import PackageMetadata
    from pkm.api.packages.package_installation import PackageInstallationTarget


@dataclass(frozen=True)
class PackageDescriptor:
    name: str
    version: Version

    @property
    def expected_src_package_name(self) -> str:
        """
        The expected name of the source package is the same name of the package
         when hyphen is replaced with underscore, there is no guarantee that the
         package author used this name, but this is considered the expected behavior.

        :return: the expected name of the source package that is stored in this package,
        """
        return PackageDescriptor.normalize_src_package_name(self.name)

    def __post_init__(self):
        super().__setattr__('name', PackageDescriptor.normalize_name(self.name).replace('_', '-'))

    def to_dependency(self) -> "Dependency":
        from pkm.api.dependencies.dependency import Dependency
        return Dependency(self.name, VersionMatch(self.version))

    def write(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': str(self.version),
        }

    @classmethod
    def read(cls, data: Dict[str, Any]) -> "PackageDescriptor":
        return cls(data['name'], Version.parse(data['version']))

    @staticmethod
    def normalize_src_package_name(package_name: str) -> str:
        return PackageDescriptor.normalize_name(package_name).translate({ord('-'): '_', ord('.'): '_'})

    @staticmethod
    def normalize_name(package_name: str) -> str:
        """
        normalize package names (see: https://packaging.python.org/en/latest/specifications/core-metadata/)

        A valid name consists only of ASCII letters and numbers, period, underscore and hyphen.
        It must start and end with a letter or number.
        Distribution names are limited to those which match the following regex (run with re.IGNORECASE):
        `^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$`

        this function replace any non valid chars in the name with '-'
        and then consecutive runs of chars in '-_.' are replaced with a single dash
        finally '-' chars are removed from the start and end of the name

        :param package_name: the package name to normalize
        :return: the normalized name
        """
        if not (result := re.sub("[^A-Z\\d._]+", '-', package_name, flags=re.IGNORECASE).strip('-')):
            raise ValueError(f"empty name after normalization (un-normalized name: '{package_name}')")
        return result

    @classmethod
    def from_dist_name(cls, name: str) -> PackageDescriptor:
        """
        create package descriptor from a distribution file name, assuming standard distribution file name conventions
        :param name: the file name
        :return: the resulted package descriptor
        """
        parts = name.split("-")
        version = Version.parse(parts[1])
        return PackageDescriptor(parts[0], version)


class Package(ABC):

    @property
    @abstractmethod
    def descriptor(self) -> PackageDescriptor:
        """
        descriptor, describing this package
        :return:
        """

    @property
    def published_metadata(self) -> Optional["PackageMetadata"]:
        """
        :return: the package provided metadata,
                 note that this is not the "computed" metadata but instead only the information available to the
                 providing repository about this package
        """
        return None

    @property
    def name(self) -> str:
        return self.descriptor.name

    @property
    def version(self) -> Version:
        return self.descriptor.version

    @abstractmethod
    def dependencies(
            self, environment: "Environment",
            extras: Optional[List[str]] = None) -> List["Dependency"]:
        """
        :param environment: the environment that the dependencies should be calculated against,
            otherwise all dependencies will be returned
        :param extras: the extras to include in the dependencies' calculation
        :return: the list of dependencies this package has in order to be installed into the given
        [environment] with the given [extras]
        """

    @abstractmethod
    def is_compatible_with(self, env: "Environment") -> bool:
        """
        :param env: the environment to check
        :return: true if this package can be installed given its dependencies into the given environment
        """

    @abstractmethod
    def install_to(
            self, target: "PackageInstallationTarget", user_request: Optional["Dependency"] = None,
            editable: bool = True):
        """
        installs this package into the given `env`
        :param target: the information about the target to install this package into
        :param user_request: if this package was requested by the user,
               supplying this field will mark the installation as user request
        :param editable: if True and able, the package will be installed in editable mode
        """

    def uninstall(self) -> bool:
        """
        uninstall this package from its package installation target, returns true if the package was removed from the
        site. If a package is a dependency of another 'required' package, then this operation will not remove the
        package but instead will remove the "user-requested" mark from it (and then return False)
        :note: this is an optional operation and is only applicable for "installed" packages
        :return: True if the package was fully removed from the installation target, False otherwise
        """
        raise UnsupportedOperationException("uninstalling is not supported for non installed packages")

    # TODO: move implementation to AbstractPackage
    def update_at(self, target: "PackageInstallationTarget", user_request: Optional["Dependency"] = None,
                  editable: bool = True):
        """
        attempt to update the package from a version installed at the given target to this version
        the update may attempt a full re-installation or a smarted "fast" delta-update like installation
        :param target: the target that contains the package to update
        :param user_request: if this package was requested by the user,
               supplying this field will mark the installation as user request
        :param editable: if True, the package will be installed in editable mode, otherwise in standard copy mode
        """
        if preinstalled := target.site_packages.installed_package(self.name):
            user_request = user_request or preinstalled.user_request
            preinstalled.uninstall()

        self.install_to(target, user_request, editable=editable)

    def __str__(self):
        return f"{self.name} {self.version}"

    def __repr__(self):
        return f"Package({str(self)})"
