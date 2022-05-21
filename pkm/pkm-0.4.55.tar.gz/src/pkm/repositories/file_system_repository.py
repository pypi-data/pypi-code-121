from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional

from pkm.api.dependencies.dependency import Dependency
from pkm.api.distributions.distribution import Distribution
from pkm.api.environments.environment import Environment
from pkm.api.packages.package import Package
from pkm.api.projects.project import Project
from pkm.api.projects.project_group import ProjectGroup
from pkm.api.repositories.repository import AbstractRepository, RepositoryBuilder, Repository
from pkm.resolution.pubgrub import MalformedPackageException
from pkm.utils.strings import endswith_any

FILE_SYSTEM_REPOSITORY_TYPE = "file-system"


class PackagesDictRepository(AbstractRepository):

    def __init__(self, name: str, packages: Dict[str, List[Package]]):
        super().__init__(name)
        self._packages = packages

    def _do_match(self, dependency: Dependency, env: Environment) -> List[Package]:
        all_packages = self._packages.get(dependency.package_name) or []
        return [p for p in all_packages if dependency.version_spec.allows_version(p.version)]


class FileSystemRepositoryBuilder(RepositoryBuilder):

    def __init__(self):
        super().__init__(FILE_SYSTEM_REPOSITORY_TYPE)

    def build(self, name: Optional[str], args: Dict[str, str]) -> Repository:
        path = Path(self._arg(args, 'path', required=True))

        packages: Dict[str, List[Package]] = defaultdict(list)
        if path.is_dir():
            if ProjectGroup.is_valid(path):
                project_group = ProjectGroup.load(path)
                for project in project_group.project_children_recursive:
                    packages[project.name].append(project)
            else:
                try:
                    project = Project.load(path)
                    packages[project.name].append(project)
                except MalformedPackageException:
                    pass

            for dist in path.iterdir():
                if _is_distribution(dist):
                    package = Distribution.package_from(dist)
                    packages[package.name].append(package)
        elif _is_distribution(path):
            package = Distribution.package_from(path)
            packages[package.name].append(package)

        return PackagesDictRepository(name, packages)


def _is_distribution(path: Path) -> bool:
    return endswith_any(path.name, ('.tar.gz', '.whl')) is not None
