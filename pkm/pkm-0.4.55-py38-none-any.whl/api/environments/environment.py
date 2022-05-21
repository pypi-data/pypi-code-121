from __future__ import annotations

import dataclasses
import hashlib
import os
import sys
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from subprocess import CompletedProcess
from typing import List, Set, Dict, Optional, Union, TypeVar, NoReturn, MutableMapping, TYPE_CHECKING

from pkm.api.dependencies.dependency import Dependency
from pkm.api.distributions.pth_link import PthLink
from pkm.api.environments.environment_introspection import EnvironmentIntrospection
from pkm.api.packages.package_installation import PackageInstallationTarget
from pkm.api.packages.site_packages import SitePackages
from pkm.api.pkm import HasAttachedRepository
from pkm.api.repositories.repository import Repository
from pkm.api.versions.version import StandardVersion, Version
from pkm.utils.commons import unone, NoSuchElementException
from pkm.utils.entrypoints import EntryPoint
from pkm.utils.files import is_root_path
from pkm.utils.iterators import find_first
from pkm.utils.processes import execvpe, monitored_run
from pkm.utils.properties import cached_property, clear_cached_properties
from pkm.utils.types import Comparable

if TYPE_CHECKING:
    from pkm.api.environments.environments_zoo import EnvironmentsZoo
    from pkm.api.environments.containerized_apps import ContainerizedApplications
    from pkm.api.repositories.repository_management import RepositoryManagement

_DEPENDENCIES_T = Union[Dependency, str, List[Union[Dependency, str]]]
_PACKAGE_NAMES_T = Union[str, List[str]]
_T = TypeVar("_T")


class Environment(HasAttachedRepository):

    def __init__(self, env_path: Path, interpreter_path: Optional[Path] = None, *,
                 use_user_site: bool = False, zoo: Optional["EnvironmentsZoo"] = None):
        self._env_path = env_path
        self._interpreter_path = interpreter_path
        self._use_user_site = use_user_site

        if zoo:
            self.zoo = zoo  # noqa

    @property
    def path(self) -> Path:
        """
        :return: the path for this environment root directory
        """
        return self._env_path

    @cached_property
    def zoo(self) -> Optional["EnvironmentsZoo"]:
        from pkm.api.environments.environments_zoo import EnvironmentsZoo
        if EnvironmentsZoo.is_valid(zoo_path := self.path.parent):
            return EnvironmentsZoo.load(zoo_path)
        return None

    @property
    def app_containers(self) -> "ContainerizedApplications":
        return self.installation_target.app_containers

    @cached_property
    def repository_management(self) -> "RepositoryManagement":
        from pkm.api.repositories.repository_management import EnvRepositoryManagement
        return EnvRepositoryManagement(self)

    @cached_property
    def _introspection(self) -> EnvironmentIntrospection:
        if is_root_path(self._env_path):
            return EnvironmentIntrospection.compute(self.interpreter_path)
        return EnvironmentIntrospection.load_or_compute(
            self._env_path / 'etc/pkm/env_introspection.json', self.interpreter_path, True)

    @property
    def name(self) -> str:
        return self.path.name

    @cached_property
    def installation_target(self) -> PackageInstallationTarget:
        paths = self._introspection.user_paths() if self._use_user_site else self._introspection.paths
        if not paths:
            raise NoSuchElementException("could not find user site configuration matching to the current os")

        result = PackageInstallationTarget(self, **{
            field.name: paths.get(field.name) or ""
            for field in dataclasses.fields(PackageInstallationTarget)
            if field.name != 'env'
        })

        return result

    def __repr__(self):
        return f"Environment({self.path})"

    @cached_property
    def interpreter_version(self) -> StandardVersion:
        """
        :return: the version of the environment's python interpreter
        """
        return StandardVersion(release=tuple(self._introspection.interpreter_version)[:3])

    @cached_property
    def interpreter_path(self) -> Path:
        """
        :return: the path for the environment's python interpreter
        """
        if self._interpreter_path is None:
            self._interpreter_path = _find_interpreter(self._env_path)
            if not self._interpreter_path:
                raise ValueError(f"could not determine the environment interpreter path for env: {self.path}")
        return self._interpreter_path

    @cached_property
    def operating_platform(self) -> "OperatingPlatform":
        emarkers = self.markers
        ispc = self._introspection

        return OperatingPlatform(
            os=emarkers["platform_system"].lower(),
            os_bits=ispc['os.bits'],
            machine=emarkers["platform_machine"].lower(),
            python_version=self.interpreter_version,
            python_implementation=emarkers["platform_python_implementation"].lower(),
            python_interpreter_bits=32 if ispc.is_32bit_interpreter else 64
        )

    def compatibility_tag_score(self, tag: str) -> Optional[Comparable]:
        """
        compute the compatibility score for the given pep425 compatibility tag
        :param tag: the pep425 compatibility tag
        :return: an opaque score object that support __le__ and __eq__ operations (read: comparable)
                 which can be treated as a score (read: higher is better)
        """
        return self._introspection.compatibility_score(tag)

    @cached_property
    def markers(self) -> Dict[str, str]:
        """
        :return: pep508 environment markers  
        """
        return self._introspection.compute_markers()

    @cached_property
    def site_packages(self) -> SitePackages:
        return self.installation_target.site_packages

    @cached_property
    def markers_hash(self) -> str:
        """
        :return: a hash built from the environment's markers, can be used to identify instances of this environment
        """
        sorted_markers = sorted(self.markers.items(), key=lambda item: item[0])
        marker_str = ';'.join(f"{k}={v}" for k, v in sorted_markers)
        return hashlib.md5(marker_str.encode()).hexdigest()

    @contextmanager
    def activate(self, env: MutableMapping[str, str] = os.environ):
        new_path = f"{self._introspection.paths['scripts']}"
        if old_path := env.get("PATH"):
            new_path = f"{new_path}{os.pathsep}{old_path}"

        old_venv = env.get('VIRTUAL_ENV')
        new_venv = str(self.path)

        env["PATH"] = new_path
        env["VIRTUAL_ENV"] = new_venv

        try:
            yield
        finally:
            if old_path is not None:
                env["PATH"] = old_path
            else:
                del env["PATH"]

            if old_venv is not None:
                env["VIRTUAL_ENV"] = old_venv
            else:
                del env["VIRTUAL_ENV"]

    def exec_proc(self, cmd: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> NoReturn:
        """
        similar to `run_proc` but does not return, this process will become the new process
        (on supporting operating systems)

        :param cmd: the command to execute
        :param args: list of arguments
        :param env: environment variables
        """

        with self.activate(env):
            execvpe(cmd, args, env)

    def run_proc(self, args: List[str], **subprocess_run_kwargs) -> CompletedProcess:
        """
        execute the given command in a new process, the process will be executed with its path adjusted to include this
        venv binaries and scripts

        :param args: the command to execute
        :param subprocess_run_kwargs: any argument that is accepted by `subprocess.run` (aside from args)
        :return: a `CompletedProcess` instance describing the completion of the requested process
        """
        env = {}
        if extra_env := subprocess_run_kwargs.get('env'):
            env.update(extra_env)
        else:
            env.update(os.environ)

        subprocess_run_kwargs['env'] = env
        with self.activate(env):
            return monitored_run(args[0], args, **subprocess_run_kwargs)

    def reload(self):
        """
        reload volatile information about this environment (like the installed packages)
        """
        clear_cached_properties(self)

    def install_link(self, name: str, paths: List[Path], imports: Optional[List[str]] = None):
        """
        installs a pth link (named `name`.pth) in the site packages (purelib)
        :param name:
        :param imports: imports to execute at runtime when reading this link
                        (example: `imports` = ['abc'] will import the abc package when the interpreter attached to this
                        environment gets executed and meets the created link)
        :param paths: the paths to add in the created link
        """

        imports = unone(imports, list)
        pth_file = self.site_packages.purelib_path / f"{name}.pth"
        if pth_file.exists():
            raise FileExistsError(f"the file {pth_file} already exists")

        PthLink(pth_file, paths, imports).save()

    def install(
            self, dependencies: _DEPENDENCIES_T, repository: Optional[Repository] = None, user_requested: bool = True,
            dependencies_override: Optional[Dict[str, List[Dependency]]] = None,
            editables: Optional[Dict[str, bool]] = None, updates: Optional[List[str]] = None):
        """
        installs the given set of dependencies into this environment.
        see: `prepare_installation` for more information about this method arguments
        """

        self.installation_target.install(
            _coerce_dependencies(dependencies), repository, user_requested, dependencies_override, editables,
            updates)

    def force_remove(self, package: str):
        """
        forcefully remove the required package, will not remove its dependencies and will not check if other packages
        depends on it - use this method with care (or don't use it at all :) )
        :param package: the name of the package to be removed
        """
        self.installation_target.force_remove(package)

    def uninstall(self, packages: _PACKAGE_NAMES_T) -> Set[str]:
        """
        attempt to remove the required packages from this env together will all the dependencies that may become orphan
        as a result of this step.

        if a package `p in packages` is a dependency (directly or indirectly) of another
        "user requested" package `q not in packages` then `p` will be kept in the environment but its
        "user requested" flag will be removed (if it was existed)

        :param packages: the package names to remove
        :return the set of package names that were successfully removed from the environment
        """
        return self.installation_target.uninstall(_coerce_package_names(packages))

    @cached_property
    def entrypoints(self) -> Dict[str, List[EntryPoint]]:
        """
        :return: all entrypoints in this environment grouped by their defined group
        """
        groups: Dict[str, List[EntryPoint]] = defaultdict(list)

        for package in self.site_packages.installed_packages():
            for ep in package.dist_info.load_entrypoints_cfg().entrypoints:
                groups[ep.group].append(replace(ep, containing_package=package))

        return groups

    @staticmethod
    def is_valid(path: Path) -> bool:
        """
        :param path: a path that may contain a python environment
        :return: true if this path contains a python environment
        """
        return (path / "pyvenv.cfg").exists() and _find_interpreter(path) is not None

    @classmethod
    def of_interpreter(cls, interpreter: Path, site: str = "user") -> Environment:
        """
        load an environment using the given interpreter
        :param interpreter: the interpreter to use
        :param site: control the installation site of the returned environment - acceptable values are
            'user' and 'system', it is only applicable for system (read: non-virtual) environments. the 'system' option
            just use the regular site, you can read about the 'user' site in documentation of
            `site.getusersitepackages()`
        :return: the loaded environment
        """
        if (interpreter.parent.parent / "pyvenv.cfg").exists():
            return cls(interpreter.parent.parent, interpreter)
        else:  # this is a system environment
            return cls(Path("/"), interpreter, use_user_site=site == 'user')

    @classmethod
    def current(cls, site: str = "user") -> Environment:
        """
        load the environment used by the currently executed interpreter
        :param site: control the installation site of the returned environment - acceptable values are
            'user' and 'system', it is only applicable for system (read: non-virtual) environments. the 'system' option
            just use the regular site, you can read about the 'user' site in documentation of
            `site.getusersitepackages()`
        :return: the loaded environment
        """
        return cls.of_interpreter(Path(sys.executable), site)

    @classmethod
    def load(cls, path: Union[Path, str]) -> Environment:
        return cls(Path(path))


def _coerce_dependencies(dependencies: _DEPENDENCIES_T) -> List[Dependency]:
    if isinstance(dependencies, str):
        return [Dependency.parse(dependencies)]
    if isinstance(dependencies, Dependency):
        return [dependencies]
    return [cd for dep in dependencies for cd in _coerce_dependencies(dep)]


def _coerce_package_names(package_names: _PACKAGE_NAMES_T) -> List[str]:
    if isinstance(package_names, str):
        return [package_names]
    return package_names


def _find_interpreter(env_root: Path) -> Optional[Path]:
    return find_first((env_root / "bin/python", env_root / "Scripts/python.exe"), lambda it: it.exists())


@dataclass
class OperatingPlatform:
    os: str  # 'linux', 'darwin', 'java', 'windows' - the value returned by platform.system() in lowercase
    os_bits: int  # 32 or 64
    machine: str  # the value returned by platform.machine() in lowercase
    python_version: Version
    python_implementation: str  # the value returned by platform.python_implementation() in lowercase
    python_interpreter_bits: int  # 32 or 64

    def has_windows_os(self) -> bool:
        return self.os == 'Windows'

    def has_x86_cpu(self) -> bool:
        return self.machine in ("i386", "amd64", "x86", "x86_64")

    def has_arm_cpu(self) -> bool:
        return 'armv71' in self.machine or 'aarch64' in self.machine
