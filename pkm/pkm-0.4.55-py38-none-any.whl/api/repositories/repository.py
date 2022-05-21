from abc import abstractmethod, ABC
from pathlib import Path
from typing import List, Union, Optional, Protocol, Iterable, TYPE_CHECKING, Dict

from pkm.api.dependencies.dependency import Dependency
from pkm.api.packages.package import Package
from pkm.api.packages.package_metadata import PackageMetadata
from pkm.api.versions.version_specifiers import AllowAllVersions
from pkm.utils.commons import unone
from pkm.utils.iterators import partition

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment


class Repository(Protocol):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def match(self, dependency: Union[Dependency, str], env: "Environment") -> List[Package]:
        """
        :param dependency: the dependency to match (or a pep508 string representing it)
        :param env: the environment that the returned packages should be compatible with
        :return: list of all the packages in this repository that match the given `dependency`
        """

    def list(self, package_name: str, env: "Environment") -> List[Package]:
        """
        :param package_name: the package to match
        :param env: the environment that the returned packages should be compatible with
        :return: list of all the packages that match the given `package_name`
        """
        return self.match(Dependency(package_name, AllowAllVersions), env)

    @property
    @abstractmethod
    def publisher(self) -> Optional["RepositoryPublisher"]:
        """
        :return: if this repository is 'publishable' returns its publisher
        """

    # noinspection PyMethodMayBeStatic
    def accepted_url_protocols(self) -> Iterable[str]:
        """
        :return: sequence of url-dependency protocols that this repository can handle
        """
        return ()

    # noinspection PyMethodMayBeStatic
    def accept_non_url_packages(self) -> bool:
        """
        :return: True if this repository should be used for non url packages
        """
        return True


# noinspection PyMethodMayBeStatic
class AbstractRepository(Repository, ABC):

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def match(self, dependency: Union[Dependency, str], env: "Environment") -> List[Package]:
        if isinstance(dependency, str):
            dependency = Dependency.parse(dependency)

        matched = [d for d in self._do_match(dependency, env) if d.is_compatible_with(env)]
        filtered = self._filter_prereleases(matched, dependency)
        return self._sort_by_priority(dependency, filtered)

    @property
    def publisher(self) -> Optional["RepositoryPublisher"]:
        return None

    def _filter_prereleases(self, packages: List[Package], dependency: Dependency) -> List[Package]:
        if dependency.version_spec.allows_pre_or_dev_releases():
            return packages
        pre_release, rest = partition(packages, lambda it: it.version.is_pre_or_dev_release())
        return rest or packages

    def _sort_by_priority(self, dependency: Dependency, packages: List[Package]) -> List[Package]:
        """
        sorts `matches` by the required priority
        :param dependency: the dependency that resulted in the given `packages`
        :param packages: the packages that were the result `_do_match(dependency)`
        :return: sorted packages by priority (first is more important than last)
        """
        packages.sort(key=lambda it: it.version, reverse=True)
        return packages

    @abstractmethod
    def _do_match(self, dependency: Dependency, env: "Environment") -> List[Package]:
        """
        IMPLEMENTATION NOTICE:
            you don't have to filter pre-releases or packages based on the given environment
            it is handled for you in the `match` method that call this one.

        :param dependency: the dependency to match
        :param env: the environment that the returned packages should be applicable with
        :return: list of all the packages in this repository that match the given `dependency` version spec
        """


class RepositoryPublisher:
    def __init__(self, repository_name: str):
        self.repository_name = repository_name

    # noinspection PyMethodMayBeStatic
    def requires_authentication(self) -> bool:
        return True

    @abstractmethod
    def publish(self, auth_args: Dict[str, str], package_meta: PackageMetadata, distribution: Path):
        """
        publish a `distribution` belonging to the given `package_meta` into the repository (registering it if needed)
        :param auth_args: dictionary filled with authentication data as supplied by user
        :param package_meta: metadata for the package that this distribution belongs to
        :param distribution: the distribution archive (e.g., wheel, sdist)
        """


class RepositoryBuilder(ABC):

    def __init__(self, repo_type: str):
        self.repo_type = repo_type

    def _arg(self, args: Dict[str, str], name: str,
             default: Optional[str] = None, required: bool = False) -> Optional[str]:
        result = args.get(name)
        if not result and required:
            raise ValueError(f"missing argument: {name} for repository type: {self.repo_type}")

        return unone(result, lambda: default)

    @abstractmethod
    def build(self, name: str, args: Dict[str, str]) -> Repository:
        """
        build a new repository instance using the given `kwargs`
        :param name: name for the created repository
        :param args: arguments for the instance creation, may be defined by derived classes
        :return: the created instance
        """

    def build_publisher(self, name: str, args: Dict[str, str]) -> Optional[RepositoryPublisher]:
        return self.build(name, args).publisher
