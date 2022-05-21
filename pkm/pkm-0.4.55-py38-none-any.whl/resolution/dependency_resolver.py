from __future__ import annotations

from dataclasses import dataclass, replace
from typing import List, Dict, Optional, TYPE_CHECKING, cast

from pkm.api.dependencies.dependency import Dependency
from pkm.api.packages.package import PackageDescriptor, Package
from pkm.api.versions.version import Version, UrlVersion, StandardVersion
from pkm.api.versions.version_specifiers import VersionMatch
from pkm.pep517_builders.external_builders import BuildError
from pkm.resolution.pubgrub import Problem, MalformedPackageException, Term, Solver
from pkm.utils.dicts import get_or_put
from pkm.utils.hashes import HashBuilder
from pkm.utils.promises import Promise
from pkm.utils.sequences import single_or_raise

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment
    from pkm.api.repositories.repository import Repository


def resolve_dependencies(root: Dependency, env: "Environment", repo: "Repository",
                         dependency_overrides: Optional[Dict[str, Dependency]] = None) -> List[Package]:
    """
    transform the give input into pubgrub's dependency resolution problem, use pubgrub to
     solve the transformed problem and transform its output to list of packages
    :param root: the root package to resolve dependencies for
    :param env: the environment that all dependencies should be compatible with
    :param repo: repository to locate dependencies
    :param dependency_overrides: package to dependency mapping that is used to override some of the dependencies
           e.g., when a dependency: x==v found (anywhere in the resolution graph) and `dependency_overrides` contains
           {'x':'>=u'} then the original dependency will be replaced with the new one.
    :return: the list of packages that are required to be installed so that the `root` dependency works correctly
    """

    problem = _PkmPackageInstallationProblem(env, repo, root, dependency_overrides)
    solver = Solver(problem, _Pkg.of(root))
    solution: Dict[_Pkg, Version] = solver.solve()

    result: List[Package] = []

    for pkg, version in solution.items():
        if pkg.extras:
            continue

        result.append(problem.opened_packages[PackageDescriptor(pkg.name, version)])

    return result


class _PkmPackageInstallationProblem(Problem):

    def __init__(self, env: "Environment", repo: "Repository", root: Dependency,
                 dependency_overrides: Optional[Dict[str, Dependency]] = None):
        self._env = env
        self._repo = repo
        self._root = root
        self._dependency_overrides = dependency_overrides or {}

        from pkm.api.pkm import pkm
        self._threads = pkm.threads

        self.opened_packages: Dict[PackageDescriptor, Package] = {}
        self._prefetched_packages: Dict[_Pkg, Promise[List[Package]]] = {}

    def _prefetch(self, package: _Pkg) -> Promise[List[Package]]:
        return get_or_put(self._prefetched_packages, package,
                          lambda: Promise.execute(self._threads, self._repo.list, package.name, self._env))

    def get_dependencies(self, package: _Pkg, version: Version) -> List[Term]:
        descriptor = PackageDescriptor(package.name, version)

        try:
            if isinstance(version, UrlVersion) and descriptor not in self.opened_packages:
                self.opened_packages[descriptor] = single_or_raise(
                    self._repo.match(f"{package} @ {version}", self._env))

            dependencies = self.opened_packages[descriptor] \
                .dependencies(self._env, package.extras)

            for d in dependencies:
                if not d.required_url():
                    self._prefetch(_Pkg.of(d))

        except (ValueError, IOError, BuildError) as e:
            raise MalformedPackageException(str(descriptor)) from e

        result: List[Term] = []

        if package.extras:  # add the package itself together with its extras
            result.append(Term(replace(package, extras=None), VersionMatch(version)))

        for d in dependencies:
            if d.is_applicable_for(self._env, package.extras):
                if o := self._dependency_overrides.get(d.package_name):
                    result.append(Term(_Pkg.of(o), o.version_spec))
                else:
                    result.append(Term(_Pkg.of(d), d.version_spec))

        return result

    def get_versions(self, package: _Pkg) -> List[StandardVersion]:
        all_packages = self._prefetch(package).result()
        # packages = [p for p in all_packages if p.is_compatible_with(self._env)]
        # make versions unique
        packages = list({p.version: p for p in all_packages if p.is_compatible_with(self._env)}.values())

        for package in packages:
            self.opened_packages[replace(package.descriptor, name=package.descriptor.name.lower())] = package

        return cast(List[StandardVersion], [p.version for p in packages if isinstance(p.version, StandardVersion)])

    def has_version(self, package: _Pkg, version: Version) -> bool:
        print(f"DBG: checking has version for {package} == {version}")
        return bool(self._repo.match(Dependency(package.name, VersionMatch(version), package.extras), self._env))


@dataclass(frozen=True, eq=True)
class _Pkg:
    name: str
    extras: Optional[List[str]]

    def __str__(self):
        result = self.name
        if self.extras:
            result += "[" + ', '.join(self.extras) + "]"
        return result

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return str(self) < str(other)

    def __hash__(self):
        hb = HashBuilder().regular(self.name)
        if self.extras:
            hb.ordered_seq(self.extras)

        return hb.build()

    @classmethod
    def of(cls, d: Dependency) -> _Pkg:
        return _Pkg(d.package_name.lower(), d.extras)
