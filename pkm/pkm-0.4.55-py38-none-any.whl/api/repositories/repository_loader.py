from __future__ import annotations

import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Iterable, Optional, Set, Mapping

from pkm.api.dependencies.dependency import Dependency
from pkm.api.environments.environment import Environment
from pkm.api.packages.package import Package
from pkm.api.repositories.repositories_configuration import RepositoryInstanceConfig, RepositoriesConfiguration, \
    RepositoriesConfigInheritanceMode
from pkm.api.repositories.repository import Repository, RepositoryBuilder, AbstractRepository
from pkm.repositories.file_repository import FileRepository
from pkm.repositories.pypi_repository import PypiRepositoryBuilder
from pkm.utils.commons import NoSuchElementException
from pkm.utils.entrypoints import EntryPoint
from pkm.utils.http.http_client import HttpClient
from pkm.utils.iterators import first_or_none

REPOSITORIES_EXTENSIONS_ENTRYPOINT_GROUP = "pkm-repositories"
REPOSITORIES_CONFIGURATION_PATH = "etc/pkm/repositories.toml"


class RepositoryLoader:
    def __init__(self, main_cfg: Path, http: HttpClient, workspace: Path):

        from pkm.api.environments.environment import Environment
        from pkm.repositories.simple_repository import SimpleRepositoryBuilder
        from pkm.repositories.git_repository import GitRepository
        from pkm.repositories.url_repository import UrlRepository
        from pkm.repositories.file_system_repository import FileSystemRepositoryBuilder

        # common builders
        pypi_builder = PypiRepositoryBuilder()

        self._builders: Dict[str, RepositoryBuilder] = {
            b.repo_type: b for b in (
                SimpleRepositoryBuilder(http),
                FileSystemRepositoryBuilder(),
                pypi_builder
            )
        }

        self._builder_providers: Dict[str, EntryPoint] = {}

        self.pypi = pypi_builder.build('pypi', {'url': 'main'})

        base_repositories = [
            GitRepository(workspace / 'git'), UrlRepository(), FileRepository()]

        # builders from entrypoints
        for epoint in Environment.current().entrypoints[REPOSITORIES_EXTENSIONS_ENTRYPOINT_GROUP]:
            try:
                ext: RepositoriesExtension = epoint.ref.import_object()()
                if not isinstance(ext, RepositoriesExtension):
                    raise ValueError("repositories entrypoint did not provide to a RepositoriesExtension class")

                for builder in ext.builders:
                    self._builders[builder.repo_type] = builder
                    self._builder_providers[builder.repo_type] = epoint

                base_repositories.extend(ext.instances)

            except Exception:  # noqa
                import traceback
                warnings.warn(f"malformed repository entrypoint: {epoint}")
                traceback.print_exc()

        base = _CompositeRepository('base', base_repositories, set(), {})

        self._cached_instances: Dict[RepositoryInstanceConfig, Repository] = {}  # noqa

        self.global_repo_config = RepositoriesConfiguration.load(main_cfg)

        self._global_repo = self.load('global', self.global_repo_config, base)
        self.workspace = workspace

    def available_repository_types(self) -> Iterable[RepositoryTypeInfo]:
        for builder in self._builders.values():
            yield RepositoryTypeInfo(builder, self._builder_providers.get(builder.repo_type))

    @property
    def global_repo(self) -> Repository:
        return self._global_repo

    def load(self, name: str, config: RepositoriesConfiguration, next_in_context: Repository) -> Repository:

        print(f"DBG: loading package config at {config.path}")

        package_search_list = []
        binding_only_repositories = set()

        for definition in config.repositories:
            instance = self.build(definition)
            package_search_list.append(instance)
            if definition.bind_only:
                binding_only_repositories.add(definition.name)

        if config.inheritance_mode == RepositoriesConfigInheritanceMode.INHERIT_CONTEXT:
            package_search_list.append(next_in_context)
        elif config.inheritance_mode == RepositoriesConfigInheritanceMode.INHERIT_GLOBAL:
            package_search_list.append(self.global_repo)

        package_binding: Dict[str, str] = {}
        print(f"DBG: {config.package_bindings=}")
        for package, binding in config.package_bindings.items():

            print(f"DBG: considering package binding: {package} = {binding}")

            if isinstance(binding, str):
                package_binding[package] = binding
            else:
                binding = self.build(RepositoryInstanceConfig.from_config(f'_unnamed_repo_for_{package}', binding))
                print(f"DBG: build unnamed repository: {binding.name}")
                binding_only_repositories.add(binding.name)
                package_search_list.append(binding)
                package_binding[package] = binding.name

        if not package_search_list:
            if config.inheritance_mode == RepositoriesConfigInheritanceMode.INHERIT_GLOBAL:
                return self.global_repo
            return next_in_context

        return _CompositeRepository(name, package_search_list, binding_only_repositories, package_binding)

    def build(self, config: RepositoryInstanceConfig) -> Repository:
        if not (cached := self._cached_instances.get(config)):
            if not (builder := self._builders.get(config.type)):
                raise KeyError(f"unknown repository type: {config.type}")
            cached = builder.build(config.name, config.args)
            self._cached_instances[config] = cached

        return cached


class _CompositeRepository(AbstractRepository):
    def __init__(
            self, name: str, package_search_list: List[Repository],
            binding_only_repositories: Set[str], package_bindings: Mapping[str, str]):
        super().__init__(name)

        self._url_handlers: Dict[str, List[Repository]] = defaultdict(list)
        self._package_search_list = []
        self._binding_only_repositories = binding_only_repositories
        self._package_binding = package_bindings

        for repo in package_search_list:
            if repo.accept_non_url_packages():
                self._package_search_list.append(repo)
            for protocol in repo.accepted_url_protocols():
                self._url_handlers[protocol].append(repo)

    def _do_match(self, dependency: Dependency, env: Environment) -> List[Package]:

        if url := dependency.required_url():
            for repo in self._url_handlers[url.protocol]:
                if match := repo.match(dependency, env):
                    return match
            raise []

        if repo_name := self._package_binding.get(dependency.package_name):
            if not (repo := first_or_none(it for it in self._package_search_list if it.name == repo_name)):
                print(f"DBG: repositories are {[r.name for r in self._package_search_list]}")
                print(f"DBG: type of repo_name is {type(repo_name)}")

                raise NoSuchElementException(f"package: {dependency.package_name} is bound to "
                                             f"repository: {repo_name}, but this repository is not defined")
            return repo.match(dependency, env)

        for repo in self._package_search_list:
            if repo.name not in self._binding_only_repositories and (result := repo.match(dependency, env)):
                return result

        return []

    def _sort_by_priority(self, dependency: Dependency, packages: List[Package]) -> List[Package]:
        return packages

    def accepted_url_protocols(self) -> Iterable[str]:
        return self._url_handlers.keys()


@dataclass
class RepositoryTypeInfo:
    builder: RepositoryBuilder
    provider: Optional[EntryPoint]

    def is_builtin(self):
        return self.provider is None

    @property
    def type_name(self) -> str:
        return self.builder.repo_type


@dataclass
class RepositoriesExtension:
    builders: List[RepositoryBuilder] = field(default_factory=list)
    instances: List[Repository] = field(default_factory=list)
