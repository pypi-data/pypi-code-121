from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterable

from pkm.api.dependencies.dependency import Dependency
from pkm.api.environments.environment import Environment
from pkm.api.packages.package import PackageDescriptor, Package
from pkm.api.repositories.repository import AbstractRepository, Repository
from pkm.config.configuration import TomlFileConfiguration
from pkm.utils.commons import unone
from pkm.utils.iterators import groupby


@dataclass
class _LockedVersion:
    env_markers_hash: str
    package: PackageDescriptor

    def write(self) -> Dict[str, Any]:
        return {
            'env_markers_hash': self.env_markers_hash,
            'package': self.package.write(),
        }

    @classmethod
    def read(cls, data: Dict[str, Any]) -> "_LockedVersion":
        return _LockedVersion(data['env_markers_hash'], PackageDescriptor.read(data['package']))


class PackagesLock:
    """
    represent a multi-environment packages lock
    this lock type can handle projects that are being worked on by different users, each using different environment
    (e.g., different os, interpreter version, etc.) for the development process without them breaking each other lock
    repeatedly
    """

    def __init__(self, locked_packages: Optional[List[_LockedVersion]] = None, lock_file: Optional[Path] = None):
        locked_packages = unone(locked_packages, list)
        self._locked_packages: Dict[str, List[_LockedVersion]] = \
            groupby(locked_packages, lambda it: it.package.name)
        self._lock_file = lock_file

    def unlock_packages(self, package_names: Iterable[str]) -> PackagesLock:
        """
        unlock the given package names, removing their information from the lock
        (does not automatically save the lock after this operation)
        :param package_names: the packages to unlock
        :return self (for chaining support)
        """
        for pn in package_names:
            self._locked_packages.pop(pn, None)

        return self

    def env_specific_locks(self, env: Environment):
        """
        :param env: the environment to extract lock information to
        :return: list of all locked packages that are specific to the given environment
        """
        env_markers_hash = env.markers_hash
        return [lp.package for lst in self._locked_packages.values() for lp in lst if
                lp.env_markers_hash == env_markers_hash]

    def locked_versions(self, env: Environment, package: str) -> List[PackageDescriptor]:
        """
        :param env: environment that the given dependency should be compatible with
        :param package: the package to find lock information for
        :return: list of package descriptors to try and install on the environment, sorted by importance
                 (try the first one first)
        """

        relevant_locks = [lp for lst in self._locked_packages.values() for lp in lst] if not package else \
            [lp for lp in (self._locked_packages.get(package) or ())]

        if not relevant_locks:
            return []

        env_markers_hash = env.markers_hash

        # the following lines may look wrong but what we are actually trying to achieve here is
        # to try and install the env-specific locked package first if such exists otherwise we would like to
        # try and install non-env specific pre-locked packages
        result = [lock.package for lock in relevant_locks if lock.env_markers_hash != env_markers_hash]
        if len(result) != len(relevant_locks):
            result.insert(0, next(lock.package for lock in relevant_locks if lock.env_markers_hash == env_markers_hash))

        return result

    def update_lock(self, env: Environment):
        """
        lock the packages in the given environment
        :param env: the environment to use to extract lock information
        """

        env_hash = env.markers_hash
        new_locks = [
            lock for locks_by_name in self._locked_packages.values()
            for lock in locks_by_name
            if lock.env_markers_hash != env_hash]

        for package in env.site_packages.installed_packages():
            new_locks.append(_LockedVersion(env_hash, package.descriptor))

        self._locked_packages = groupby(new_locks, lambda it: it.package.name)

    def save(self, lock_file: Optional[Path] = None):
        """
        saves the state of this packages lock to the given file
        :param lock_file:
        """

        lock_file = lock_file or self._lock_file
        if not lock_file:
            raise FileNotFoundError('lock file is not given')

        configuration = TomlFileConfiguration.load(lock_file)
        locks = [lp.write() for locks_by_name in self._locked_packages.values() for lp in locks_by_name]
        configuration['lock'] = locks
        configuration.save()

    def sort_packages_by_lock_preference(self, env: Environment, packages: List[Package]) -> List[Package]:
        if packages:
            locked_versions = {lp.version for lp in self.locked_versions(env, packages[0].name)}
            packages.sort(key=lambda it: 0 if it.version in locked_versions else 1)

        return packages

    @classmethod
    def load(cls, lock_file: Path) -> "PackagesLock":
        """
        load packages lock from the given lock file
        :param lock_file: the file to load from
        :return: the loaded lock
        """

        configuration = TomlFileConfiguration.load(lock_file)
        locked_packages = [_LockedVersion.read(lp) for lp in (configuration['lock'] or [])]
        return PackagesLock(locked_packages, lock_file)


class LockPrioritizingRepository(AbstractRepository):
    def __init__(self, name: str, base_repo: Repository, lock: PackagesLock, env: Environment):
        super().__init__(name)
        self._base_repo = base_repo
        self._lock = lock
        self._env = env

    def _do_match(self, dependency: Dependency, env: Environment) -> List[Package]:
        return self._base_repo.match(dependency, env)

    def _sort_by_priority(self, dependency: Dependency, packages: List[Package]) -> List[Package]:
        return self._lock.sort_packages_by_lock_preference(self._env, packages)

    def accepted_url_protocols(self) -> Iterable[str]:
        return self._base_repo.accepted_url_protocols()

    def accept_non_url_packages(self) -> bool:
        return self._base_repo.accept_non_url_packages()
