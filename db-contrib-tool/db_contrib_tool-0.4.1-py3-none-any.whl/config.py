"""Common config module."""
from __future__ import annotations

import os
from enum import Enum
from typing import List, NamedTuple, Optional, Set

from evergreen import Task
from pydantic import BaseModel

from db_contrib_tool.utils.filesystem import read_yaml_file

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
SETUP_REPRO_ENV_CONFIG_FILE = os.path.join(CONFIG_DIR, "setup_repro_env_config.yml")
# Records the paths of installed multiversion binaries on Windows.
WINDOWS_BIN_PATHS_FILE = "windows_binary_paths.txt"
DEFAULT_VERSION_LABEL = "default"


class SegmentWriteKey(Enum):
    DEV = "RmMosrk1bf025xLRbZUxF2osVzGLPpL3"
    PROD = "jrHGRmtQBO8HYU1CyCfnB279SnktLgGH"


SEGMENT_WRITE_KEY = SegmentWriteKey.PROD.value
if os.environ.get("ENV") == "DEV":
    SEGMENT_WRITE_KEY = SegmentWriteKey.DEV.value


class DownloadTarget(NamedTuple):
    """
    Build variant attributes to target for download.

    :param edition: Edition of mongo (e.g. enterprise).
    :param platform: Platform mongo was built for (e.g. ubuntu1804).
    :param architecture: CPU architecture mongo was built for (e.g. x86).
    """

    edition: str
    platform: Optional[str]
    architecture: str

    def is_complete(self) -> bool:
        """Determine if this target has all the details it needs."""
        return self.platform is not None


class Tasks(BaseModel):
    """
    Important evergreen tasks for setup repro env config.

    * projects: Evergreen projects that these tasks apply to.
    * binary: Set of tasks that create mongo binaries.
    * symbols: Set of tasks that publish debug symbols.
    * push: Set of tasks that push artifacts.
    """

    projects: Set[str]
    binary: Set[str]
    symbols: Set[str]
    push: Set[str]

    def is_task_binary(self, evg_task: Task) -> bool:
        """Determine if the given evergreen task generates mongo binaries."""
        return evg_task.display_name in self.binary

    def is_task_symbols(self, evg_task: Task) -> bool:
        """Determine if the given evergreen task generates debug symbols."""
        return evg_task.display_name in self.symbols

    def is_task_push(self, evg_task: Task) -> bool:
        """Determine if the given evergreen task pushes artifacts."""
        return evg_task.display_name in self.push


class Buildvariant(BaseModel):
    """Class represents evergreen buildvariant in setup repro env config."""

    name: str
    edition: str
    platform: str
    architecture: str
    versions: Optional[Set[str]] = None

    def is_match(self, target: DownloadTarget) -> bool:
        """
        Determine if this build variant matches the given criteria.

        :param target: Criteria to match build variant.
        :returns: True if all the criteria match.
        """
        return all(
            [
                target.edition == self.edition,
                target.platform == self.platform,
                target.architecture == self.architecture,
            ]
        )

    def targets_version(self, version: str) -> bool:
        """
        Determine if this build variant targets the given version.

        :param version: Version to check against.
        :returns: True if the given version is targeted.
        """
        return self.versions is not None and version in self.versions


class SetupReproEnvConfig(BaseModel):
    """Class represents setup repro env config."""

    evergreen_tasks: List[Tasks]
    evergreen_buildvariants: List[Buildvariant]

    @classmethod
    def from_yaml_file(cls, filename: str) -> SetupReproEnvConfig:
        """Create an instance of the class from the given filename."""
        return cls(**read_yaml_file(filename))

    @classmethod
    def empty_config(cls) -> SetupReproEnvConfig:
        """Create an empty instance of the configuration."""
        return cls(
            evergreen_tasks=[
                Tasks(
                    projects=set(),
                    binary=set(),
                    symbols=set(),
                    push=set(),
                )
            ],
            evergreen_buildvariants=[],
        )

    def find_matching_build_variant(
        self, target: DownloadTarget, target_version: str
    ) -> Optional[str]:
        """
        Find a build variant that matches the given criteria.

        :param target: Criteria of build variant to target.
        :param target_version: Version to target.
        :return: Name of build variant matching given criteria.
        """
        last_found_name = None
        evergreen_buildvariants = self.evergreen_buildvariants

        for buildvariant in evergreen_buildvariants:
            if buildvariant.is_match(target):
                if buildvariant.targets_version(target_version):
                    return buildvariant.name
                elif not buildvariant.versions:
                    last_found_name = buildvariant.name

        return last_found_name

    def get_evergreen_tasks(self, evg_project: str) -> Tasks:
        """
        Find the set of required tasks that match the given evg_project.

        :param evg_project: Evergreen project to search for.
        :return: Required tasks for the evergreen project.
        """
        default_tasks = None
        for tasks in self.evergreen_tasks:
            if evg_project in tasks.projects:
                return tasks
            if DEFAULT_VERSION_LABEL in tasks.projects:
                default_tasks = tasks

        if default_tasks is None:
            raise ValueError("Default tasks not found in config.")
        return default_tasks


SETUP_REPRO_ENV_CONFIG = SetupReproEnvConfig.from_yaml_file(SETUP_REPRO_ENV_CONFIG_FILE)
