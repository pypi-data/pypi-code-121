from __future__ import annotations

from pathlib import Path
from typing import Iterable, Union, Optional, Tuple, List, TYPE_CHECKING

from pkm.api.pkm import HasAttachedRepository
from pkm.api.projects.environments_config import EnvironmentsConfiguration, ENVIRONMENT_CONFIGURATION_PATH
from pkm.api.projects.project import Project
from pkm.config.configuration import TomlFileConfiguration, computed_based_on
from pkm.utils.files import path_to, ensure_exists, resolve_relativity
from pkm.utils.iterators import single_or_raise
from pkm.utils.properties import cached_property

if TYPE_CHECKING:
    from pkm.api.repositories.repository_management import RepositoryManagement


class ProjectGroup(HasAttachedRepository):
    """
    project group, like the name implies, is a group of projects
    the projects are related to themselves in a parent/children manner,
    a parent is always a group and children may be projects or another project groups

    the project group is configured by the pyproject-group.toml configuration file
    """

    def __init__(self, config: "PyProjectGroupConfiguration", parent: Optional[ProjectGroup] = None):
        self._config = config
        self.path = self._config.path.parent
        if parent:
            self.parent = parent  # noqa

    @property
    def config(self) -> "PyProjectGroupConfiguration":
        return self._config

    @cached_property
    def environments_config(self) -> EnvironmentsConfiguration:
        return EnvironmentsConfiguration.load(self.path / ENVIRONMENT_CONFIGURATION_PATH)

    @cached_property
    def repository_management(self) -> "RepositoryManagement":
        from pkm.api.repositories.repository_management import ProjectGroupRepositoryManagement
        return ProjectGroupRepositoryManagement(self)

    @cached_property
    def parent(self) -> Optional["ProjectGroup"]:
        """
        :return: the parent of this project group (if such exists)
        """
        if not (parent := self._config.parent):
            return ProjectGroup._find_parent(self.path.resolve())
        else:
            return ProjectGroup(PyProjectGroupConfiguration.load(
                ensure_exists(parent, lambda: f"{self.path}'s parent path {parent} doesn't exists")
            ))

    @cached_property
    def root(self) -> Optional["ProjectGroup"]:
        """
        :return: the top most parent of this project group
        """
        return parent.root if (parent := self.parent) else None

    @cached_property
    def children(self) -> Iterable[Union[Project, "ProjectGroup"]]:
        """
        :return: the child projects (or project groups) defined in this group
        """
        result = []
        for child in self._config.children:
            if (child / 'pyproject.toml').exists():
                result.append(Project.load(child, group=self))
            elif (child / 'pyproject-group.toml').exists:
                result.append(
                    ProjectGroup(PyProjectGroupConfiguration.load(child / 'pyproject-group.toml'), parent=self))

        return result

    @cached_property
    def project_children_recursive(self) -> List[Project]:
        """
        :return: the child projects defined in this group and
        recursively the child projects of the project groups defined in this group
        """
        result = []
        for child in self.children:
            if isinstance(child, Project):
                result.append(child)
            else:
                result.extend(child.project_children_recursive)

        return result

    def add(self, project: Union[Project, Path]):
        """
        add project to this group, saving the modification in the configuration file
        :param project: the project to add
        """

        project_path = project if isinstance(project, Path) else project.path
        self._config.children = (*self._config.children, project_path)
        self._config.save()

    def remove(self, project: Union[str, Path]):
        """
        remove project from this group, saving the modification in the configuration file
        :param project: the project name or path to remove
        """
        if isinstance(project, str):
            project = single_or_raise(p for p in self.children if p.name == project).path

        project = project.resolve()

        self._config.children = tuple(p for p in self._config.children if p != project)
        self._config.save()

    def build_all(self):
        """
        recursively run the build operation on all projects and subprojects in this group
        """
        # with monitor.on_build_all(self):
        for project in self.children:
            if isinstance(project, Project):
                project.build()
            else:
                project.build_all()

    @classmethod
    def _find_parent(cls, path: Path) -> Optional["ProjectGroup"]:
        for path_parent in path.parents:
            if (parent_config_file := (path_parent / 'pyproject-group.toml')).exists():
                parent_config = PyProjectGroupConfiguration.load(parent_config_file)
                if any(child == path for child in parent_config.children):
                    return ProjectGroup(parent_config)
        return None

    @classmethod
    def of(cls, project: Project) -> Optional["ProjectGroup"]:
        """
        :param project: the project to get the project group for
        :return: the project group if such defined
        """
        if group := project.config.pkm_project.group:
            return ProjectGroup(PyProjectGroupConfiguration.load(resolve_relativity(Path(group), project.path)))
        return cls._find_parent(project.path)

    @classmethod
    def load(cls, path: Path) -> "ProjectGroup":
        """
        load the project group from a specific path
        :param path: the path to the project group directory
        :return: the loaded project group
        """
        return ProjectGroup(PyProjectGroupConfiguration.load(path / 'pyproject-group.toml'))

    @staticmethod
    def is_valid(path: Path) -> bool:
        """
        :param path: the path to check
        :return: True if the path contain project group, False otherwise
        """
        return (path / 'pyproject-group.toml').exists()


class PyProjectGroupConfiguration(TomlFileConfiguration):

    @computed_based_on("name")
    def name(self) -> str:
        return self['name'] or self._path.parent.name

    @property
    def path(self) -> Path:
        return self._path

    @computed_based_on("project-group.children")
    def children(self) -> Tuple[Path, ...]:
        if not (children := self["project-group.children"]):
            return tuple()

        root = self.path.parent
        result = []
        for path in children:
            path = Path(path)
            if path.is_absolute():
                result.append(path.resolve())
            else:
                result.append((root / path).resolve())

        return tuple(result)

    @children.modifier
    def set_children(self, new: Iterable[Path]):
        root = self.path.parent
        result = []
        for path in new:
            if path.is_absolute():
                result.append(str(path_to(root, path)))
            else:
                result.append(str(path))

        self["project-group.children"] = result

    @computed_based_on("project-group.parent")
    def parent(self) -> Optional[Path]:
        if parent := self["project-group.parent"]:
            path = Path(parent)
            if path.is_absolute():
                return path.resolve()
            return (self.path.parent / path).resolve()
        return None
