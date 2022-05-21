from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Union, Set, TYPE_CHECKING

from pkm.api.dependencies.dependency import Dependency
from pkm.api.packages.package import Package, PackageDescriptor
from pkm.api.packages.package_metadata import PackageMetadata
from pkm.api.packages.site_packages import InstalledPackage
from pkm.api.packages.site_packages import SitePackages
from pkm.api.repositories.repository import Repository, AbstractRepository
from pkm.api.versions.version import StandardVersion
from pkm.api.versions.version_specifiers import VersionMatch
from pkm.resolution.dependency_resolver import resolve_dependencies
from pkm.resolution.pubgrub import UnsolvableProblemException
from pkm.utils.delegations import delegate
from pkm.utils.iterators import first_or_none, single_or_raise
from pkm.utils.promises import Promise
from pkm.utils.properties import cached_property, clear_cached_properties

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment
    from pkm.api.environments.containerized_apps import ContainerizedApplications


@dataclass
class PackageInstallationTarget:  # TODO: maybe rename into package installation site?
    env: "Environment"
    stdlib: str
    platstdlib: str
    platinclude: str
    purelib: str
    platlib: str
    include: str
    data: str
    scripts: str

    @cached_property
    def site_packages(self) -> "SitePackages":
        from pkm.api.packages.site_packages import SitePackages
        return SitePackages(self.env, Path(self.purelib), Path(self.platlib))

    @cached_property
    def app_containers(self) -> "ContainerizedApplications":
        from pkm.api.environments.containerized_apps import ContainerizedApplications
        return ContainerizedApplications(self)

    def reload(self):
        clear_cached_properties(self)

    def uninstall(self, packages_to_remove: List[str]) -> Set[str]:
        """
        attempt to remove the required packages from this target together will all the dependencies
        that may become orphan as a result of this step.

        if a package `p in packages` is a dependency (directly or indirectly) of another
        "user requested" package `q not in packages` then `p` will be kept in the target but its
        "user requested" flag will be removed (if it was existed)

        :param packages_to_remove: the package names to remove
        :return the set of package names that were successfully removed from the environment
        """

        self.reload()

        preinstalled_packages = list(self.site_packages.installed_packages())
        requested_deps = {p.name: p.user_request for p in preinstalled_packages if p.user_request}
        for package_name in packages_to_remove:
            requested_deps.pop(package_name, None)

        user_request = _UserRequestPackage(list(requested_deps.values()))
        installation_repo = _RemovalRepository(preinstalled_packages, user_request)

        installation = resolve_dependencies(user_request.to_dependency(), self.env, installation_repo)
        InstallationPlan(self, installation, {}).execute()

        kept = {p.name for p in installation}

        for p in packages_to_remove:
            if p in kept:
                self.site_packages.installed_package(p).dist_info.unmark_as_user_requested()

        self.reload()
        return {p for p in packages_to_remove if p not in kept}

    def install(
            self, dependencies: List[Dependency], repository: Optional[Repository] = None, user_requested: bool = True,
            dependencies_override: Optional[Dict[str, Dependency]] = None, editables: Optional[Dict[str, bool]] = None,
            updates: Optional[List[str]] = None):
        """
        installs the given set of dependencies into this target.
        see: `prepare_installation` and `PreparedInstallation:install` for more information about this method arguments
        """
        if not dependencies:
            return  # nothing to do...

        repository = repository or self.env.attached_repository
        plan = self.plan_installation(dependencies, repository, user_requested, dependencies_override, updates)
        plan.editables = editables
        plan.execute()

    def force_remove(self, package: str):
        """
        forcefully remove the required package, will not remove its dependencies and will not check if other packages
        depends on it - use this method with care (or don't use it at all :) )
        :param package: the name of the package to be removed
        """
        if installed := self.site_packages.installed_package(package):
            installed.uninstall()

    def plan_installation(
            self, dependencies: List[Dependency], repository: Repository,
            user_requested: bool = True, dependencies_override: Optional[Dict[str, Dependency]] = None,
            updates: Optional[List[str]] = None
    ) -> InstallationPlan:
        """
        plan but does not install an installation for the given dependencies.
        resolve the `dependencies` using the given `repository`, making sure to not break any pre-installed
        "user-requested" packages (but may upgrade their dependencies if it needs to)

        :param dependencies: the dependency to install
        :param repository: the repository to fetch this dependency from, if not given will use the attached repository
        :param user_requested: indicator that the user requested this dependency themselves
            (this will be marked on the installation as per pep376)
        :param dependencies_override: mapping from package name into dependency that should be "forcefully"
            used for this package
        :param updates: If given, the packages listed will be updated if required and already installed
        """

        self.reload()

        updates = set(updates or [])
        preinstalled_packages = [p for p in self.site_packages.installed_packages() if p.name not in updates]
        pre_requested_deps = {p: p.user_request for p in preinstalled_packages if p.user_request}

        new_deps = {d.package_name: d for d in dependencies}
        all_deps = {**pre_requested_deps, **new_deps}

        run_slow_path = False
        installation = None

        try:
            # first we try the fast path: only adding packages without updating
            user_request = _UserRequestPackage(list(new_deps.values()))
            installation_repo = _InstallationRepository(repository, preinstalled_packages, user_request, True)
            installation = resolve_dependencies(
                user_request.to_dependency(), self.env, installation_repo, dependencies_override)

            installation_names = {i.name for i in installation}
            for preinstalled in preinstalled_packages:
                if preinstalled.name not in installation_names:
                    installation.append(preinstalled)

        except UnsolvableProblemException:
            # don't execute the slow path code here so that the stacktrace will be cleaner if exception will happen
            run_slow_path = True

        if run_slow_path:
            # if we cannot we try the slow path in which we allow preinstalled packages dependencies to be updated
            user_request = _UserRequestPackage(list(all_deps.values()))
            installation_repo = _InstallationRepository(repository, preinstalled_packages, user_request, False)
            installation = resolve_dependencies(
                user_request.to_dependency(), self.env, installation_repo)

        return InstallationPlan(self, installation, new_deps if user_requested else {})


class PackageOperation(Enum):
    INSTALL = "install"
    UPDATE = "update"
    REMOVE = "remove"
    SKIP = "skip"


class InstallationPlan:
    def __init__(self, target: PackageInstallationTarget, packages: List[Package],
                 user_requests: Dict[str, "Dependency"]):
        self.default_target = target
        self.packages = packages
        self.user_requests = user_requests
        self.editables: Optional[Dict[str, bool]] = None

    def selected_package(self, name: str) -> Optional[Package]:
        return first_or_none(it for it in self.packages if it.name == name)

    def compute_operations_for_target(
            self, target: Optional[PackageInstallationTarget] = None) -> Dict[Package, PackageOperation]:

        operations: Dict[Package, PackageOperation] = {}

        target = target or self.default_target
        editables = self.editables or {}

        preinstalled: Dict[str, InstalledPackage] = {
            SitePackages.normalize_package_name(p.name): p
            for p in target.site_packages.installed_packages()}

        toinstall: Dict[str, Package] = {
            SitePackages.normalize_package_name(p.name): p
            for p in self.packages
            if not isinstance(p, _UserRequestPackage)}

        editables = {SitePackages.normalize_package_name(name): value for name, value in editables.items()} \
            if editables else {}

        for norm_package_name, package_to_install in toinstall.items():

            if preinstalled_package := preinstalled.pop(norm_package_name, None):
                prev_install_editable = preinstalled_package.installation_info.editable
                editable = editables.get(norm_package_name, prev_install_editable)
                if preinstalled_package.version == package_to_install.version and editable == prev_install_editable:
                    operations[package_to_install] = PackageOperation.SKIP
                    continue

                operations[package_to_install] = PackageOperation.UPDATE
            else:
                operations[package_to_install] = PackageOperation.INSTALL

        for package_to_remove in preinstalled.values():
            operations[package_to_remove] = PackageOperation.REMOVE

        return operations

    def execute(self, target: Optional[PackageInstallationTarget] = None):
        """
        executes the prepared installation inside the given `target`
        :param target: the site in which to execute this installation
        """

        from pkm.api.pkm import pkm

        target = target or self.default_target
        operations = self.compute_operations_for_target(target)
        editables = self.editables or {}
        site = target.site_packages

        promises: List[Promise] = []

        for package, operation in operations.items():
            editable = editables.get(package.name)
            if operation == PackageOperation.INSTALL:
                promises.append(Promise.execute(
                    pkm.threads, package.install_to, target, editable=bool(editable),
                    user_request=self.user_requests.get(package.name)))
            elif operation == PackageOperation.UPDATE:
                if editable is None:
                    editable = site.installed_package(package.name).installation_info.editable
                promises.append(Promise.execute(
                    pkm.threads, package.update_at, target, editable=editable,
                    user_request=self.user_requests.get(package.name)))
            elif operation == PackageOperation.REMOVE:
                promises.append(Promise.execute(pkm.threads, package.uninstall))

        for promise in promises:
            promise.result()

        site.reload()


class _UserRequestPackage(Package):
    def __init__(self, request: List["Dependency"]):
        self._desc = PackageDescriptor("installation request", StandardVersion(release=(0,)))
        self._request = request

    @property
    def descriptor(self) -> PackageDescriptor:
        return self._desc

    def dependencies(
            self, environment: "Environment", extras: Optional[List[str]] = None) -> List["Dependency"]:
        return self._request

    def is_compatible_with(self, env: "Environment") -> bool: return True

    def install_to(self, *args, **kwargs): pass

    def to_dependency(self) -> "Dependency":
        return Dependency(self.name, VersionMatch(self.version))


class _RemovalRepository(AbstractRepository):

    def __init__(self, preinstalled: List[InstalledPackage], user_request: Package):
        super().__init__('removal repository')
        self._preinstalled: Dict[str, InstalledPackage] = {
            PackageDescriptor.normalize_src_package_name(p.name).lower(): p
            for p in preinstalled
        }

        self._user_request = user_request

    def _do_match(self, dependency: "Dependency", env: Environment) -> List[Package]:
        if dependency.package_name == self._user_request.name:
            return [self._user_request]

        return [self._preinstalled[PackageDescriptor.normalize_src_package_name(dependency.package_name).lower()]]


@delegate(Repository, '_repo')
class _InstallationRepository(Repository, ABC):
    def __init__(
            self, repo: Repository, installed_packages: List[InstalledPackage], user_request: Package,
            limit_to_installed: bool):

        assert repo, "no repository provided"
        self._user_request = user_request
        self._installed_packages: Dict[str, InstalledPackage] = {p.name: p for p in installed_packages}
        self._limit_to_installed = limit_to_installed
        self._repo = repo

    def match(self, dependency: Union["Dependency", str], env: Environment) -> List[Package]:
        if isinstance(dependency, str):
            dependency = Dependency.parse(dependency)

        if dependency.package_name == self._user_request.name:
            return [self._user_request]

        if installed := self._installed_packages.get(dependency.package_name):
            installed = _UpdatableInstalledPackage(installed, self._repo)

            if self._limit_to_installed:
                return [installed]

        packages = self._repo.match(dependency, env)
        if installed:
            packages.sort(key=lambda it: 0 if installed.version == it.version else 1)

        return packages


@delegate(Package, '_installed')
class _UpdatableInstalledPackage(Package, ABC):
    def __init__(self, installed: InstalledPackage, repo: Repository):
        self._installed = installed
        self.repo = repo

    @property
    def descriptor(self) -> PackageDescriptor:
        return self._installed.descriptor

    @property
    def published_metadata(self) -> Optional["PackageMetadata"]:
        return self._installed.published_metadata

    def update_at(self, target: "PackageInstallationTarget", user_request: Optional["Dependency"] = None,
                  editable: bool = True):
        new_ver = single_or_raise(self.repo.match(self._installed.descriptor.to_dependency(), target.env))
        user_request = self._installed.user_request if user_request is None else user_request
        self._installed.uninstall()
        new_ver.install_to(target, user_request=user_request, editable=editable)
