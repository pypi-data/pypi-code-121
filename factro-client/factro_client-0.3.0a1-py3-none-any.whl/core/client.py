from typing import List

from .helpers.work_record_handler import WorkRecordHandler, WorkRecord
from .helpers.user_handler import UserHandler, User
from .helpers.task_handler import TaskHandler, Task
from .helpers.package_handler import PackageHandler, Package
from .helpers.project_handler import ProjectHandler, Project, ProjectStructure
from .helpers.contact_handler import ContactHandler, Contact
from .helpers.company_handler import CompanyHandler, Company


class Client(object):

    def __init__(self, url:str, api_key:str):
        self._url = url
        self._api_key = api_key

    def get_work_records(self, from_date, to_date) -> List[WorkRecord]:
        handler = WorkRecordHandler(self._url, self._api_key)
        work_records = handler.get_work_records(from_date, to_date)

        return work_records

    def get_user_by_id(self, user_id: str) -> User:
        handler = UserHandler(self._url, self._api_key)

        user = handler.get_user_by_id(user_id)

        return user

    def get_task_by_id(self, task_id: str) -> Task:
        handler = TaskHandler(self._url, self._api_key)

        task = handler.get_task_by_id(task_id)

        return task

    def get_packages_by_project_id(self, project_id: str) -> List[Package]:
        handler = PackageHandler(self._url, self._api_key)

        packages = handler.get_packages_by_project_id(project_id)

        return packages

    def get_package_by_id(self, package_id: str) -> Package:
        handler = PackageHandler(self._url, self._api_key)

        package = handler.get_package_by_id(package_id)

        return package

    def get_project_by_id(self, project_id: str) -> Project:
        handler = ProjectHandler(self._url, self._api_key)

        project = handler.get_project_by_id(project_id)

        return project

    def get_project_structure(self, project_id: str) -> ProjectStructure:
        handler = ProjectHandler(self._url, self._api_key)

        structure = handler.get_project_structure(project_id)

        return structure

    def get_projects(self) -> List[Project]:
        handler = ProjectHandler(self._url, self._api_key)

        projects = handler.get_projects()

        return projects

    def get_contact_by_id(self, contact_id: str) -> Contact:
        handler = ContactHandler(self._url, self._api_key)

        contact = handler.get_contact_by_id(contact_id)

        return contact

    def get_company_by_id(self, company_id: str) -> Company:
        handler = CompanyHandler(self._url, self._api_key)

        company = handler.get_company_by_id(company_id)

        return company
