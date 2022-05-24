from datetime import datetime, timedelta
import logging
import os

from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import List, Optional

from cachetools import TTLCache, cached


from ..core.client import Client as CoreClient
from ..core.client import Project, Package, Task

logger = logging.getLogger('factro_client')


CACHE_MAX_SIZE = os.environ.get('FACTRO_CLIENT_CACHE_MAX_SIZE', 100)
CACHE_TTL = os.environ.get('FACTRO_CLIENT_CACHE_TTL', 2 * 60 * 60)  # 2 hours

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ProjectIntro:
    id: str
    number: int
    link: str
    title: str
    project_state: str
    start_date: str
    end_date: str
    custom_fields: Optional[dict]
    billing_cycle: str
    offer_number: str
    order_number: str
    description: Optional[str] = ''

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EffortEstimationTask:
    id: str
    number: str
    link: str
    title: str
    task_state: str
    planned_effort: float
    realized_effort: float
    remaining_effort: float
    custom_fields: Optional[dict]
    role: Optional[str] = ''
    description: Optional[str] = ''

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EffortEstimationPackage:
    id: str
    number: int
    link: str
    title: str
    custom_fields: Optional[dict]
    tasks: List[EffortEstimationTask]
    description: Optional[str] = ''
    realized_effort: Optional[float] = 0.0
    remaining_effort: Optional[float] = 0.0

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EffortEstimationProjekt:
    id: str
    number: int
    link: str
    title: str
    project_state: str
    custom_fields: Optional[dict]
    billing_cycle: str
    offer_number: str
    order_number: str
    packages: List[EffortEstimationPackage]
    description: Optional[str] = ''
    planned_effort: Optional[float] = 0.0
    realized_effort: Optional[float] = 0.0
    remaining_effort: Optional[float] = 0.0

class Client:

    def __init__(self, url: str, api_key: str):
        self._core_client = CoreClient(url, api_key)

    @cached(cache=TTLCache(maxsize=CACHE_MAX_SIZE, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_project_by_id(self, project_id: str) -> Project:
        project = self._core_client.get_project_by_id(project_id)
        return project
        
    @cached(cache=TTLCache(maxsize=100, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_package_by_id(self, package_id: str) -> Package:
        package = self._core_client.get_package_by_id(package_id)
        return package

    @cached(cache=TTLCache(maxsize=CACHE_MAX_SIZE, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_task_by_id(self, task_id: str) -> Task:
        task = self._core_client.get_task_by_id(task_id)
        return task

    def _map_project_to_effort_estimation_projekt(self, project: Project) -> EffortEstimationProjekt:
        effort_estimation_projekt = EffortEstimationProjekt(
            id = project.id,
            number = project.number,
            # https://cloud.factro.com/5681c8b0/?p=task&pi=563227c4-5259-4953-bdea-286f41a8790c
            link = f"{self._core_client._url}/?p=project&pi={project.id}",
            title = project.title,
            project_state = project.project_state,
            custom_fields = project.custom_fields,
            billing_cycle = project.custom_fields.get('abrechnungsart', ''),
            offer_number = project.custom_fields.get('angebotsnummer', ''),
            order_number = project.custom_fields.get('bestellnummer', ''),
            packages = [],
            description = project.description,
            planned_effort = project.planned_effort,
            realized_effort = project.realized_effort,
            remaining_effort = project.remaining_effort
        )

        return effort_estimation_projekt

    def _handle_task(self, structure_task) -> EffortEstimationTask:
        task = self._query_task_by_id(structure_task.id)

        effort_estimation_task = EffortEstimationTask(
            id = task.id,
            number = task.number,
            # https://cloud.factro.com/5681c8b0/?p=task&pi=563227c4-5259-4953-bdea-286f41a8790c
            link = f"{self._core_client._url}/?p=task&pi={task.id}",
            title = task.title,
            task_state = task.task_state,
            planned_effort = task.planned_effort,
            realized_effort = task.realized_effort,
            remaining_effort = task.remaining_effort,
            custom_fields = task.custom_fields,
            role = task.custom_fields.get('rolle', ''),
            description = task.description,
        )

        return effort_estimation_task

    def _find_tasks(self, structure_childs) -> List[EffortEstimationTask]:
        effort_estimation_tasks = []

        for child in structure_childs:
            if child.type == 'task':
                task = self._handle_task(child)
                effort_estimation_tasks.append(task)
            elif child.type == 'package':
                tasks = self._find_tasks(child.children)
                effort_estimation_tasks.extend(tasks)

        return effort_estimation_tasks

    def _handle_package(self, structure_package) -> EffortEstimationPackage:

        package = self._query_package_by_id(structure_package.id)
        tasks = self._find_tasks(structure_package.children)

        effort_estimation_package = EffortEstimationPackage(
            id = package.id,
            number = package.number,
            # https://cloud.factro.com/5681c8b0/?p=task&pi=563227c4-5259-4953-bdea-286f41a8790c
            link = f"{self._core_client._url}/?p=package&pi={package.id}",
            title = package.title,
            custom_fields = package.custom_fields,
            tasks = tasks,
            description = package.description,
            realized_effort = package.realized_effort,
            remaining_effort = package.remaining_effort
        )

        return effort_estimation_package
        

    def query_effort_estimation_projekt(self, project_id: str) -> EffortEstimationProjekt:

        effort_estimation_projekt = None

        structure = self._core_client.get_project_structure(project_id)
        project = self._query_project_by_id(structure.id)
        effort_estimation_projekt = self._map_project_to_effort_estimation_projekt(project)

        for child in structure.children:
            if child.type == 'task':
                logger.warning(f"Cannot handle a task ('{child.id}', '{child.type}') within a project {structure.id}")
            elif child.type == 'package':
                effort_estimation_package = self._handle_package(child)
                effort_estimation_projekt.packages.append(effort_estimation_package)

        return effort_estimation_projekt

    def query_projects(self) -> List[ProjectIntro]:
        
        def _map_project(project: Project) -> ProjectIntro:
            project_intro = ProjectIntro(
                id = project.id,
                number = project.number,
                # https://cloud.factro.com/5681c8b0/?p=task&pi=563227c4-5259-4953-bdea-286f41a8790c
                link = f"{self._core_client._url}/?p=project&pi={project.id}",
                title = project.title,
                project_state = project.project_state,
                start_date = project.start_date,
                end_date = project.end_date,
                custom_fields = project.custom_fields,
                billing_cycle = project.custom_fields.get('abrechnungsart', ''),
                offer_number = project.custom_fields.get('angebotsnummer', ''),
                order_number = project.custom_fields.get('bestellnummer', ''),
                description = project.description
            )

            return project_intro
        
        project_intros = []
        projects = self._core_client.get_projects()

        for project in projects:
            project_intro = _map_project(project)
            project_intros.append(project_intro)

        return project_intros
