from __future__ import annotations
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Union, Dict, Mapping, Any, Iterator

from pkm.api.dependencies.dependency import Dependency
from pkm.api.dependencies.env_markers import EnvironmentMarker
from pkm.api.distributions.distinfo import EntryPoint, ObjectReference
from pkm.api.packages.package import PackageDescriptor
from pkm.api.versions.version import Version
from pkm.api.versions.version_specifiers import VersionSpecifier, StandardVersionRange, AllowAllVersions
from pkm.config.configuration import TomlFileConfiguration, computed_based_on
from pkm.resolution.pubgrub import MalformedPackageException
from pkm.utils.commons import unone
from pkm.utils.dicts import remove_none_values, without_keys
from pkm.utils.files import path_to
from pkm.utils.properties import cached_property
from pkm.utils.sequences import strs


@dataclass(frozen=True, eq=True)
class BuildSystemConfig:
    requirements: List[Dependency]
    build_backend: str
    backend_path: Optional[List[str]]

    def to_config(self) -> Dict[str, Any]:
        return remove_none_values({
            'requires': [str(d) for d in self.requirements] if self.requirements else None,
            'build-backend': self.build_backend,
            'backend-path': self.backend_path
        })

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "BuildSystemConfig":
        requirements = [Dependency.parse(dep) for dep in (cfg.get('requires') or [])]
        build_backend = cfg.get('build-backend')
        backend_path = cfg.get('backend-path')

        return BuildSystemConfig(requirements, build_backend, backend_path)


@dataclass(frozen=True, eq=True)
class ContactInfo:
    name: Optional[str] = None
    email: Optional[str] = None

    @classmethod
    def from_config(cls, contact: Dict[str, Any]) -> "ContactInfo":
        return cls(**contact)

    def to_config(self) -> Dict[str, Any]:
        return remove_none_values({
            'name': self.name, 'email': self.email
        })


def _entrypoints_from_config(group: str, ep: Dict[str, str]) -> List[EntryPoint]:
    return [EntryPoint(group, ep_name, ObjectReference.parse(ep_oref)) for ep_name, ep_oref in ep.items()]


def _entrypoints_to_config(entries: List[EntryPoint]) -> Dict[str, str]:
    return {e.name: str(e.ref) for e in entries}


PKM_DIST_CFG_TYPE_LIB = "lib"
PKM_DIST_CFG_TYPE_CAPP = "cnt-app"


@dataclass(frozen=True, eq=True)
class PkmDistributionConfig:
    type: str  # lib, cnt-app

    def to_config(self) -> Dict[str, Any]:
        return {**self.__dict__}

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> PkmDistributionConfig:
        return cls(**cfg)


@dataclass(frozen=True, eq=True)
class PkmApplicationConfig:
    containerized: bool

    dependencies: List[Dependency]
    dependency_overwrites: Dict[str, Dependency]
    exposed_packages: List[str]

    def to_config(self) -> Dict[str, Any]:
        return {
            'containerized': self.containerized,
            'dependencies': strs(self.dependencies),
            'dependency-overwrites': {p: str(d) for p, d in self.dependency_overwrites.items()},
            'exposed-packages': self.exposed_packages
        }

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(
            config.get('containerized', False),
            [Dependency.parse(it) for it in unone(config.get('dependencies'), list)],
            {pk: Dependency.parse(dep) for pk, dep in unone(config.get('dependency-overwrites'), dict).items()},
            unone(config.get('exposed-packages'), list)
        )


@dataclass(frozen=True, eq=True)
class PkmProjectConfig:
    packages: Optional[List[str]] = None
    group: Optional[str] = None  # TODO: remove group and use conventions only?

    def to_config(self) -> Dict[str, Any]:
        return remove_none_values({
            'packages': self.packages,
            'group': self.group
        })

    @classmethod
    def from_config(cls, config: Optional[Dict[str, Any]]) -> Optional["PkmProjectConfig"]:
        if not config:
            return PkmProjectConfig()

        return PkmProjectConfig(**config)


@dataclass(frozen=True, eq=True)
class ProjectConfig:
    """
    the project config as described in
    https://www.python.org/dev/peps/pep-0621/, https://www.python.org/dev/peps/pep-0631/
    """

    # The name of the project.
    name: str
    # The version of the project as supported by PEP 440.
    version: Version
    # The summary description of the project.
    description: Optional[str]
    # The actual text or Path to a text file containing the full description of this project.
    readme: Union[Path, str, None]
    # The Python version requirements of the project.
    requires_python: Optional[Union[StandardVersionRange, AllowAllVersions]]
    # The project licence identifier or path to the actual licence file
    license: Union[str, Path, None]
    # The people or organizations considered to be the "authors" of the project.
    authors: Optional[List[ContactInfo]]
    # similar to "authors", exact meaning is open to interpretation.
    maintainers: Optional[List[ContactInfo]]
    # The keywords for the project.
    keywords: Optional[List[str]]
    # Trove classifiers (https://pypi.org/classifiers/) which apply to the project.
    classifiers: Optional[List[str]]
    # A mapping of URLs where the key is the URL label and the value is the URL itself.
    urls: Optional[Dict[str, str]]
    # list of entry points, following https://packaging.python.org/en/latest/specifications/entry-points/.
    entry_points: Optional[Dict[str, List[EntryPoint]]]
    # The dependencies of the project.
    dependencies: Optional[List[Dependency]]
    # The optional dependencies of the project, grouped by the 'extra' name that provides them.
    optional_dependencies: Dict[str, List[Dependency]]
    # a list of field names (from the above fields), each field name that appears in this list means that the absense of
    # data in the corresponding field means that a user tool provides it dynamically
    dynamic: Optional[List[str]]

    all_fields: Dict[str, Any]

    def all_entrypoints(self) -> List[EntryPoint]:
        if not self.entry_points:
            return []

        return [e for points in self.entry_points.values() for e in points]

    def is_dynamic(self, field: str) -> bool:
        """
        :param field: the field name (as in the configuration, e.g.,
                      optional-dependencies and not optional_dependencies)
        :return: True if the field is marked as dynamic, False otherwise
        """
        return self.all_fields.get(field) is None and bool(d := self.dynamic) and field in d  # noqa

    @cached_property
    def all_dependencies(self) -> List[Dependency]:
        all_deps = [d for d in (self.dependencies or [])]
        optional_deps = self.optional_dependencies or {}
        for od_group, deps in optional_deps.items():
            extra_rx = re.compile(f'extra\\s*==\\s*(\'{od_group}\'|"{od_group}")')
            for dep in deps:
                if not dep.env_marker or not extra_rx.match(str(dep.env_marker)):
                    new_marker = (str(dep.env_marker).rstrip(';') + ';') if dep.env_marker else ''
                    new_marker = f"{new_marker}extra==\'{od_group}\'"
                    all_deps.append(replace(dep, env_marker=EnvironmentMarker.parse_pep508(new_marker)))
                else:
                    all_deps.append(dep)
        return all_deps

    def package_descriptor(self) -> PackageDescriptor:
        return PackageDescriptor(self.name, self.version)

    def readme_content(self) -> str:
        if not self.readme:
            return ""

        if isinstance(self.readme, str):
            return self.readme

        if self.readme.exists():
            return self.readme.read_text()

        return ""

    def script_entrypoints(self) -> Iterator[EntryPoint]:
        """
        :return: iterator over the scripts (and gui scripts) entrypoints
        """
        if scripts := self.entry_points.get(EntryPoint.G_CONSOLE_SCRIPTS):
            yield from scripts

        if gui_scripts := self.entry_points.get(EntryPoint.G_GUI_SCRIPTS):
            yield from gui_scripts

    def readme_content_type(self) -> str:
        if self.readme and isinstance(self.readme, Path):
            readme_suffix = self.readme.suffix
            if readme_suffix == '.md':
                return 'text/markdown'
            elif readme_suffix == '.rst':
                return 'text/x-rst'

        return 'text/plain'

    def license_content(self) -> str:
        if not self.license:
            return ""

        if isinstance(self.license, str):
            return self.license

        return self.license.read_text()

    def to_config(self, project_path: Optional[Path] = None) -> Dict[str, Any]:
        project_path = project_path or Path.cwd()
        readme_value = None
        if self.readme:
            readme_value = self.readme if isinstance(self.readme, str) \
                else {'file': str(path_to(project_path, self.readme))}

        ep: Dict[str, List[EntryPoint]] = self.entry_points or {}
        ep_no_scripts: Dict[str, List[EntryPoint]] = without_keys(
            ep, EntryPoint.G_CONSOLE_SCRIPTS, EntryPoint.G_GUI_SCRIPTS)

        optional_dependencies = {
            extra: [str(d) for d in deps]
            for extra, deps in self.optional_dependencies.items()
        } if self.optional_dependencies else None

        license_ = None
        if self.license:
            license_ = {'file': self.license} if isinstance(self.license, Path) else {'text': self.license}

        project = {
            **self.all_fields,
            'name': self.name, 'version': str(self.version), 'description': self.description,
            'readme': readme_value, 'requires-python': str(self.requires_python) if self.requires_python else None,
            'license': license_, 'authors': [c.to_config() for c in self.authors] if self.authors is not None else None,
            'maintainers': [c.to_config() for c in self.maintainers] if self.maintainers is not None else None,
            'keywords': self.keywords, 'classifiers': self.classifiers, 'urls': self.urls,
            'scripts': _entrypoints_to_config(
                ep[EntryPoint.G_CONSOLE_SCRIPTS]) if EntryPoint.G_CONSOLE_SCRIPTS in ep else None,
            'gui-scripts': _entrypoints_to_config(
                ep[EntryPoint.G_GUI_SCRIPTS]) if EntryPoint.G_GUI_SCRIPTS in ep else None,
            'entry-points': {group: _entrypoints_to_config(entries)
                             for group, entries in ep_no_scripts.items()} if ep_no_scripts else None,
            'dependencies': [str(d) for d in self.dependencies] if self.dependencies else None,
            'optional-dependencies': optional_dependencies, 'dynamic': self.dynamic
        }

        return remove_none_values(project)

    @classmethod
    def from_config(cls, config: Dict[str, Any], project_path: Optional[Path] = None) -> "ProjectConfig":
        project_path = project_path or Path.cwd()

        version = Version.parse(config['version'])

        # decide the readme value
        readme = None
        if readme_entry := config.get('readme'):
            if isinstance(readme_entry, Mapping):
                if readme_file := readme_entry.get('file'):
                    readme = project_path / readme_file
                else:
                    readme = str(readme_entry['text'])
            else:
                readme = str(readme_entry)

        requires_python = VersionSpecifier.parse(config['requires-python']) \
            if 'requires-python' in config else AllowAllVersions

        license_ = None
        if license_table := config.get('license'):
            license_ = (project_path / license_table['file']) if 'file' in license_table else str(license_table['text'])

        authors = None
        if authors_array := config.get('authors'):
            authors = [ContactInfo.from_config(a) for a in authors_array]

        maintainers = None
        if maintainers_array := config.get('maintainers'):
            maintainers = [ContactInfo.from_config(a) for a in maintainers_array]

        entry_points = {}
        if scripts_table := config.get('scripts'):
            entry_points[EntryPoint.G_CONSOLE_SCRIPTS] = _entrypoints_from_config(
                EntryPoint.G_CONSOLE_SCRIPTS, scripts_table)

        if gui_scripts_table := config.get('gui-scripts'):
            entry_points[EntryPoint.G_GUI_SCRIPTS] = _entrypoints_from_config(
                EntryPoint.G_GUI_SCRIPTS, gui_scripts_table)

        if entry_points_tables := config.get('entry-points'):
            entry_points.update({
                group: _entrypoints_from_config(group, entries)
                for group, entries in entry_points_tables.items()
            })

        dependencies = None
        if dependencies_array := config.get('dependencies'):
            dependencies = [Dependency.parse(it) for it in dependencies_array]

        optional_dependencies = {}
        if optional_dependencies_table := config.get('optional-dependencies'):
            optional_dependencies = {
                extra: [Dependency.parse(it) for it in deps]
                for extra, deps in optional_dependencies_table.items()
            }

        return ProjectConfig(
            name=config['name'], version=version, description=config.get('description'), readme=readme,
            requires_python=requires_python, license=license_, authors=authors, maintainers=maintainers,
            keywords=config.get('keywords'), classifiers=config.get('classifiers'), urls=config.get('urls'),
            entry_points=entry_points, dependencies=dependencies, optional_dependencies=optional_dependencies,
            dynamic=config.get('dynamic'), all_fields=config)


_LEGACY_BUILDSYS = {
    'requires': ['setuptools', 'wheel', 'pip', 'cython'],
    'build-backend': 'setuptools.build_meta:__legacy__'
}

_LEGACY_PROJECT = {
    'dynamic': [
        'description', 'readme', 'requires-python', 'license', 'authors', 'maintainers', 'keywords',
        'classifiers', 'urls', 'scripts', 'gui-scripts', 'entry-points', 'dependencies', 'optional-dependencies']}


class PyProjectConfiguration(TomlFileConfiguration):
    # here due to pycharm bug https://youtrack.jetbrains.com/issue/PY-47698
    project: ProjectConfig
    pkm_project: PkmProjectConfig
    build_system: BuildSystemConfig
    pkm_application: PkmApplicationConfig
    pkm_distribution: PkmDistributionConfig

    @computed_based_on("tool.pkm.project")
    def pkm_project(self) -> PkmProjectConfig:
        return PkmProjectConfig.from_config(self['tool.pkm.project'])

    @computed_based_on("tool.pkm.application")
    def pkm_application(self) -> Optional[PkmApplicationConfig]:
        if app_config := self['tool.pkm.application']:
            return PkmApplicationConfig.from_config(app_config)
        return None

    @pkm_application.modifier
    def set_pkm_application(self, app: Optional[PkmApplicationConfig]):
        if app is None:
            del self['tool.pkm.application']
        else:
            self['tool.pkm.application'] = app.to_config()

    @computed_based_on("tool.pkm.distribution")
    def pkm_distribution(self) -> PkmDistributionConfig:
        if dist_config := self['tool.pkm.distribution']:
            return PkmDistributionConfig.from_config(dist_config)

        return PkmDistributionConfig(PKM_DIST_CFG_TYPE_LIB)

    @pkm_distribution.modifier
    def set_pkm_distribution(self, distribution: PkmDistributionConfig):
        self['tool.pkm.distribution'] = distribution.to_config()

    @computed_based_on("project")
    def project(self) -> Optional[ProjectConfig]:
        project_path = self._path.parent if self._path else None

        project: Dict[str, Any] = self['project']
        if project is None:
            return None

        return ProjectConfig.from_config(project, project_path)

    @project.modifier
    def set_project(self, value: ProjectConfig):
        project_path = self.path and self.path.parent
        self['project'] = value.to_config(project_path)

    @computed_based_on("build-system")
    def build_system(self) -> BuildSystemConfig:
        return BuildSystemConfig.from_config(self['build-system'])

    @build_system.modifier
    def set_build_system(self, bs: BuildSystemConfig):
        self['build-system'] = bs.to_config()

    @classmethod
    def load_effective(cls, pyproject_file: Path,
                       package: Optional[PackageDescriptor] = None) -> "PyProjectConfiguration":
        """
        load the effective pyproject file (with missing essential values filled with their legacy values)
        for example, if no build-system is available, this method will fill in the legacy build-system
        :param pyproject_file: the pyproject.toml to load
        :param package: the package that this pyproject belongs to, if given,
                        it will be used in case of missing name and version values
        :return: the loaded pyproject
        """
        pyproject = PyProjectConfiguration.load(pyproject_file)
        source_tree = pyproject_file.parent

        # ensure build-system:
        if pyproject['build-system'] is None:
            if not (source_tree / 'setup.py').exists():
                package_info = str(pyproject_file.parent) if not package else f"{package.name} {package.version}"
                raise MalformedPackageException(f"cannot infer build system for package: {package_info}")

            pyproject['build-system'] = _LEGACY_BUILDSYS

        if pyproject['build-system.requires'] is None:
            pyproject['build-system.requires'] = []

        if pyproject['build-system.build-backend'] is None:
            pyproject['build-system.build-backend'] = _LEGACY_BUILDSYS['build-backend']
            pyproject['build-system.requires'] = list(
                {*_LEGACY_BUILDSYS['requires'], *pyproject['build-system.requires']})

        # ensure project:
        if not pyproject['project']:
            pyproject['project'] = {
                **_LEGACY_PROJECT,
                'name': (package or source_tree).name,
                'version': str(package.version) if package else 'unknown_version'}

        pyproject['project.name'] = PackageDescriptor.normalize_name(pyproject['project.name'])
        return pyproject
