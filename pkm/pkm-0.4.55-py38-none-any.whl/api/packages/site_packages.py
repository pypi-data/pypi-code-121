import shutil
from pathlib import Path
from typing import Optional, List, Dict, Iterable, TYPE_CHECKING, Iterator

from pkm.api.dependencies.dependency import Dependency
from pkm.api.distributions.distinfo import DistInfo, PackageInstallationInfo
from pkm.api.packages.package import Package, PackageDescriptor
from pkm.api.packages.package_metadata import PackageMetadata
from pkm.api.versions.version_specifiers import VersionMatch
from pkm.utils.files import is_empty_directory, is_relative_to
from pkm.utils.properties import cached_property, clear_cached_properties

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment
    from pkm.api.packages.package_installation import PackageInstallationTarget


class SitePackages:
    def __init__(self, env: "Environment", purelib: Path, platlib: Path):

        self._purelib = purelib
        self._platlib = platlib
        self.env = env

    def all_sites(self) -> Iterator[Path]:
        yield self._purelib
        if self._platlib != self._purelib:
            yield self._platlib

    def __eq__(self, other):
        return isinstance(other, SitePackages) \
               and other._purelib == self._purelib \
               and other._platlib == self._platlib \
               and other.env.path == self.env.path

    @property
    def purelib_path(self) -> Path:
        return self._purelib

    @property
    def platlib_path(self) -> Path:
        return self._platlib

    @cached_property
    def _name_to_packages(self) -> Dict[str, "InstalledPackage"]:
        result: Dict[str, InstalledPackage] = {}
        self._scan_packages(self._purelib, result)
        self._scan_packages(self._platlib, result)
        return result

    @staticmethod
    def normalize_package_name(package_name: str) -> str:
        return PackageDescriptor.normalize_src_package_name(package_name).lower()

    def _scan_packages(self, site: Path, result: Dict[str, "InstalledPackage"]):
        if not site.exists():
            return

        for di in DistInfo.scan(site):
            result[self.normalize_package_name(di.package_name)] = InstalledPackage(di, self)

    def installed_packages(self) -> Iterable["InstalledPackage"]:
        return self._name_to_packages.values()

    def installed_package(self, package_name: str) -> Optional["InstalledPackage"]:
        return self._name_to_packages.get(self.normalize_package_name(package_name))

    def reload(self):
        clear_cached_properties(self)


def _read_user_request(dist_info: DistInfo, metadata: PackageMetadata) -> Optional[Dependency]:
    if stored_request := dist_info.load_user_requested_info():
        return stored_request
    elif dist_info.is_user_requested():
        return Dependency(metadata.package_name, VersionMatch(metadata.package_version))


class InstalledPackage(Package):

    def __init__(self, dist_info: DistInfo, site: Optional[SitePackages] = None):

        self._dist_info = dist_info
        self.site = site

    @cached_property
    def published_metadata(self) -> Optional["PackageMetadata"]:
        return self._dist_info.load_metadata_cfg()

    @property
    def dist_info(self) -> DistInfo:
        """
        :return: the installed package dist-info
        """
        return self._dist_info

    @cached_property
    def descriptor(self) -> PackageDescriptor:
        meta = self.published_metadata
        return PackageDescriptor(meta.package_name, meta.package_version)

    @cached_property
    def user_request(self) -> Optional[Dependency]:
        """
        :return: the dependency that was requested by the user
                 if this package was directly requested by the user or its project
                 otherwise None
        """
        return _read_user_request(self._dist_info, self.published_metadata)

    @cached_property
    def installation_info(self) -> PackageInstallationInfo:
        return self._dist_info.load_installation_info() or PackageInstallationInfo()

    def dependencies(
            self, environment: "Environment", extras: Optional[List[str]] = None) -> List["Dependency"]:
        all_deps = self.published_metadata.dependencies
        return [d for d in all_deps if d.is_applicable_for(environment, extras)]

    def is_compatible_with(self, env: "Environment") -> bool:
        return self.published_metadata.required_python_spec.allows_version(env.interpreter_version)

    def install_to(
            self, target: "PackageInstallationTarget", user_request: Optional["Dependency"] = None,
            editable: bool = False):
        if target.site_packages != self.site:
            raise NotImplemented()  # maybe re-mark user request?

    def is_in_purelib(self) -> bool:
        """
        :return: True if this package is installed to purelib, False if it is installed into platlib
        """

        return is_relative_to(self.dist_info.path, self.site.purelib_path)

    def uninstall(self):
        """
        uninstall this package from its site packages
        """
        parents_to_check = set()
        for installed_file in self._dist_info.installed_files():
            installed_file.unlink(missing_ok=True)
            parents_to_check.add(installed_file.parent)

        installation_site = self.dist_info.path.parent
        while parents_to_check:
            parent = parents_to_check.pop()  # noqa : pycharm does not know's about set's pop method?

            if parent == installation_site or not is_relative_to(parent, installation_site):
                continue

            if (precompiled := parent / "__pycache__").exists():
                shutil.rmtree(precompiled, ignore_errors=True)

            if is_empty_directory(parent):
                parent.rmdir()
                parents_to_check.add(parent.parent)

        if self._dist_info.path.exists():
            shutil.rmtree(self._dist_info.path)

        if self.site:
            self.site.reload()
