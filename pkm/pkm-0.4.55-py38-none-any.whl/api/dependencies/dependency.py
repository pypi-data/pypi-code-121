from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional, List, TYPE_CHECKING

from pkm.api.dependencies.env_markers import PEP508EnvMarkerParser, EnvironmentMarker
from pkm.api.versions.version import UrlVersion
from pkm.api.versions.version_parser import VersionParser
from pkm.api.versions.version_specifiers import VersionSpecifier, VersionMatch, AllowAllVersions
from pkm.utils.parsers import SimpleParser

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment
    from pkm.api.packages.package import PackageDescriptor


@dataclass(frozen=True, eq=True)
class Dependency:
    """
    represents a package dependency (`package a` depends on `package b`)
    where the fields: `package_name` refer to the dependant package, `version_spec` refer to the version requirement,
    `extras` refers to the required package extras and finally, env marker is a constraint for the environments that
    this dependency is applicable for
    """

    package_name: str
    version_spec: VersionSpecifier = AllowAllVersions
    extras: Optional[List[str]] = None
    env_marker: Optional[EnvironmentMarker] = None

    def is_applicable_for(self, env: "Environment", extras: List[str]) -> bool:
        return self.env_marker is None or self.env_marker.evaluate_on(env, extras or [])

    def with_extras(self, extras: Optional[List[str]]) -> Dependency:
        return replace(self, extras=extras)

    def required_url(self) -> Optional[UrlVersion]:
        """
        :return: url version if this dependency is a "url dependency"
            (meaning, its version specifier requires specific url), None otherwise.
        """

        vspec = self.version_spec
        if isinstance(vspec, VersionMatch) and vspec.allow and isinstance(vspec.version, UrlVersion):
            return vspec.version
        return None

    def __str__(self):
        extras_str = f"[{','.join(self.extras)}]" if self.extras else ''

        version_str = "" if self.version_spec is AllowAllVersions else f" {str(self.version_spec)}"

        marker_str = f";{self.env_marker}" if self.env_marker else ''

        return f"{self.package_name}{extras_str}{version_str}{marker_str}"

    def __repr__(self):
        return f"Dependency({self})"

    @classmethod
    def parse(cls, text: str) -> "Dependency":
        return PEP508DependencyParser(text).read_dependency()


class PEP508DependencyParser(SimpleParser):

    def _read_extras(self) -> List[str]:
        self.match_or_err('[', 'expecting extras start ([)')
        extras: List[str] = []

        while self.is_not_empty():
            self.match_ws()
            extras.append(self._read_identifier())
            self.match_ws()
            if not self.match(','):
                break

        self.match_or_err(']', 'expecting extras end (])')

        return extras

    def _read_version_spec(self) -> VersionSpecifier:
        return self.subparser(VersionParser).read_specifier()

    def _read_identifier(self) -> str:
        if (p := self.peek()).isalpha() or p == '_':
            return self.until(lambda i, t: not t[i].isalnum() and t[i] not in '_-.')
        self.raise_err('expecting identifier')

    def read_emarker(self) -> EnvironmentMarker:
        return self.subparser(PEP508EnvMarkerParser).read_marker()

    def read_dependency(self) -> Dependency:
        from pkm.api.packages.package import PackageDescriptor

        self.match_ws()
        package_name = PackageDescriptor.normalize_name(self._read_identifier())
        self.match_ws()

        extras: Optional[List[str]] = None
        if self.peek() == '[':
            extras = self._read_extras()
            self.match_ws()

        version_spec: VersionSpecifier = AllowAllVersions
        if self.peek() != ';':
            version_spec = self._read_version_spec()
            self.match_ws()

        env_marker: Optional[EnvironmentMarker] = None
        if self.match(";", '') and self.is_not_empty():
            env_marker = self.read_emarker()

        return Dependency(package_name, version_spec, extras=extras, env_marker=env_marker)
