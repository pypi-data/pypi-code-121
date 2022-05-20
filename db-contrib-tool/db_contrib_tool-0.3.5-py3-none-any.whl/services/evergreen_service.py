"""A service for working with evergreen."""
from __future__ import annotations

from typing import Dict, Iterator, List, NamedTuple, Optional

import inject
import structlog
from evergreen import EvergreenApi, Task, Version
from requests.exceptions import HTTPError

from db_contrib_tool.config import SetupReproEnvConfig, Tasks

MONGO_PROJECT_PREFIX = "mongodb-mongo-"

LOGGER = structlog.get_logger(__name__)


class ArtifactUrls(NamedTuple):
    """
    Collection of URL containing build artifacts associated with a build.

    * urls: Dictionary of named artifacts to artifact URLs.
    * project_identifier: ID of evergreen project artifacts belong to.
    """

    urls: Dict[str, str]
    project_identifier: str


class RequiredTasks(NamedTuple):
    """Tasks relevant for multiversion setup."""

    symbols_task: Task
    binary_task: Task
    push_task: Optional[Task]

    @classmethod
    def from_task_list(
        cls, task_list: List[Task], targeted_tasks: Tasks, require_push: bool
    ) -> Optional[RequiredTasks]:
        """
        Collect the required tasks from the given task list.

        :param task_list: List of all tasks.
        :param targeted_tasks: Configuration of which tasks to collect.
        :param require_push: If True, require the push task be found.
        :return: Collection of tasks that fulfill the required task criteria.
        """
        binary_task = None
        symbols_task = None
        push_task = None

        for evg_task in task_list:
            if binary_task is None and targeted_tasks.is_task_binary(evg_task):
                binary_task = evg_task

            if push_task is None and targeted_tasks.is_task_push(evg_task):
                push_task = evg_task

            if symbols_task is None and targeted_tasks.is_task_symbols(evg_task):
                symbols_task = evg_task

            if binary_task and symbols_task:
                if require_push and push_task is None:
                    continue

                return cls(
                    binary_task=binary_task,
                    symbols_task=symbols_task,
                    push_task=push_task,
                )

        LOGGER.debug(
            "Missing required tasks",
            binary_task=binary_task,
            symbols_task=symbols_task,
            push_task=push_task,
            require_push=require_push,
        )

        return None

    def get_artifact_urls(self) -> Optional[ArtifactUrls]:
        """
        Get a collection of the relevant artifact URLs form the targeted tasks.

        :return: Artifact URLs for targeted tasks.
        """
        if not self.binary_task.is_success():
            LOGGER.warning(
                "binary task was not successful",
                task_id=self.binary_task.task_id,
                status=self.binary_task.status,
            )
            return None

        if self.push_task is not None and not self.push_task.is_success():
            LOGGER.warning(
                "push task was not successful",
                task_id=self.push_task.task_id,
                status=self.push_task.status,
            )
            return None

        LOGGER.info(
            "Required evergreen task(s) were successful.",
            push_task_required=self.push_task is not None,
            binary_task_id=self.binary_task.task_id,
        )

        artifact_urls = {artifact.name: artifact.url for artifact in self.binary_task.artifacts}

        if self.symbols_task.is_success():
            for artifact in self.symbols_task.artifacts:
                artifact_urls[artifact.name] = artifact.url
        else:
            LOGGER.warning(
                "debug symbol task was unsuccessful",
                archive_symbols_task=self.symbols_task.task_id,
            )

        return ArtifactUrls(
            urls=artifact_urls, project_identifier=self.binary_task.project_identifier
        )


class EvergreenService:
    """A service for working with evergreen."""

    @inject.autoparams()
    def __init__(self, evg_api: EvergreenApi, setup_repro_config: SetupReproEnvConfig) -> None:
        """
        Initialize the service.

        :param evg_api: Evergreen API client.
        """
        self.evg_api = evg_api
        self.setup_repro_config = setup_repro_config

    def get_task(self, task_id: str) -> Task:
        """Get evergreen task by task id."""
        return self.evg_api.task_by_id(task_id)

    def query_task_existence(self, task_id: str) -> bool:
        """
        Query if the given evergreen task exists.

        :param task_id: ID of evergreen task to query.
        :returns: True if the task exists.
        """
        try:
            task = self.evg_api.task_by_id(task_id)
            return task is not None
        except HTTPError as err:
            if err.response.status_code == 404:
                return False
            LOGGER.warning("Unexpected error returned by Evergreen.", exc_info=True)
            raise err

    def get_version(self, version_id: str) -> Version:
        """
        Get the requested evergreen version.

        :param version_id: ID of version to get.
        :return: Version object for given version id.
        """
        return self.evg_api.version_by_id(version_id)

    def query_version_existence(self, version_id: str) -> bool:
        """
        Query if the given evergreen version exists.

        :param version_id: ID of evergreen version to query.
        :returns: True if the version exists.
        """
        try:
            version = self.evg_api.version_by_id(version_id)
            return version is not None
        except HTTPError as err:
            if err.response.status_code == 404:
                return False
            LOGGER.warning("Unexpected error returned by Evergreen.", exc_info=True)
            raise err

    def get_mongo_projects(self) -> List[str]:
        """Return the list of mongodb/mongo evergreen project identifiers."""
        evg_projects = [
            proj
            for proj in self.evg_api.all_projects()
            if proj.enabled and MONGO_PROJECT_PREFIX in proj.identifier
        ]
        return [proj.identifier for proj in evg_projects]

    def get_evergreen_version(
        self, evergreen_projects: List[str], evg_ref: str
    ) -> Optional[Version]:
        """Return evergreen version by reference (commit_hash or evergreen_version_id)."""
        # Evergreen reference as evergreen_version_id
        evg_refs = [evg_ref]
        # Evergreen reference as {project_name}_{commit_hash}
        evg_refs.extend(f"{proj.replace('-', '_')}_{evg_ref}" for proj in evergreen_projects)

        for ref in evg_refs:
            try:
                evg_version = self.evg_api.version_by_id(ref)
            except HTTPError:
                continue
            else:
                LOGGER.debug(
                    "Found evergreen version.",
                    evergreen_version=evg_version.version_id,
                )
                return evg_version

        return None

    def get_version_iterator(self, evg_project: str) -> Iterator[Version]:
        """
        Get an iterator over evergreen versions for the given project.

        :param evg_project: Evergreen project to query.
        :return: Iterator over the versions of the given evergreen project.
        """
        return self.evg_api.versions_by_project(evg_project)

    def get_compile_artifact_urls(
        self, evg_version: Version, buildvariant_name: str, ignore_failed_push: bool = False
    ) -> Optional[ArtifactUrls]:
        """
        Find the artifact URLs for the given build variant.

        :param evg_version: Evergreen version to search.
        :param buildvariant_name: Name of build variant to query.
        :param ignore_failed_push: Return URLs even if the push task failed.
        :return: URLs to artifacts in build variant.
        """
        build_id = evg_version.build_variants_map[buildvariant_name]
        evg_build = self.evg_api.build_by_id(build_id)
        LOGGER.debug("Checking build", build_id=evg_build.id)

        evg_tasks = evg_build.get_tasks()
        required_tasks = RequiredTasks.from_task_list(
            evg_tasks,
            self.setup_repro_config.get_evergreen_tasks(evg_version.project_identifier),
            not ignore_failed_push,
        )
        if required_tasks is not None:
            return required_tasks.get_artifact_urls()
        return None
