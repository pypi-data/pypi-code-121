from datetime import datetime, timedelta
import logging
import os
from typing import List, Optional

from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from cachetools import cached, TTLCache

from tzlocal import get_localzone


from ..core.client import Client as CoreClient
from ..core.client import WorkRecord, Company, Contact, Project, Package, Task, User

logger = logging.getLogger('factro_client')


CACHE_MAX_SIZE = os.environ.get('FACTRO_CLIENT_CACHE_MAX_SIZE', 100)
CACHE_TTL = os.environ.get('FACTRO_CLIENT_CACHE_TTL', 2 * 60 * 60)  # 2 hours

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ActivityRecording:
    start_date: str
    end_date: str
    title: str
    is_billable: bool
    hours: float
    description: str
    driving_distance_km: Optional[float]
    task_number: str
    company_name: str
    company_shortname: str
    project_name: str
    project_number: str
    project_tags: Optional[str]
    package_id: Optional[str]
    package_number: Optional[str]
    package_title: Optional[str]
    package_custom_fields: Optional[dict]
    email: str
    project_role: str
    is_billable_raw: bool
    billing_cycle: str
    offer_number: str
    order_number: str
    firstname: str
    lastname: str
    cost_center: Optional[str]
    department: Optional[str]


class Client:

    def __init__(self, url: str, api_key: str):
        self._core_client = CoreClient(url, api_key)

    @cached(cache=TTLCache(maxsize=CACHE_MAX_SIZE, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_company_by_id(self, company_id: str) -> Company:
        company = None

        if company_id is not None:
            company = self._core_client.get_company_by_id(company_id)

        return company

    @cached(cache=TTLCache(maxsize=CACHE_MAX_SIZE, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_contact_by_id(self, contact_id: str) -> Contact:
        contact = None

        if contact_id is not None:
            contact = self._core_client.get_contact_by_id(contact_id)

        return contact

    @cached(cache=TTLCache(maxsize=CACHE_MAX_SIZE, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_project_by_id(self, project_id: str) -> Project:
        project = self._core_client.get_project_by_id(project_id)
        return project

    @cached(cache=TTLCache(maxsize=100, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_package_by_id(self, package_id: str) -> Package:
        if package_id is None:
            return None

        package = self._core_client.get_package_by_id(package_id)
        return package

    @cached(cache=TTLCache(maxsize=CACHE_MAX_SIZE, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_task_by_id(self, task_id: str) -> Task:
        task = self._core_client.get_task_by_id(task_id)
        return task

    @cached(cache=TTLCache(maxsize=CACHE_MAX_SIZE, ttl=timedelta(seconds=CACHE_TTL), timer=datetime.now))
    def _query_user_by_id(self, user_id: str) -> User:
        user = self._core_client.get_user_by_id(user_id)
        return user

    def query_controlling_data(self, from_date: str, to_date: str) -> List[ActivityRecording]:

        tz = get_localzone()

        def make_datetime(date_string: str) -> datetime:
            d = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')

            return tz.localize(d).isoformat()

        def mapping(workrecord: WorkRecord, user: User, task: Task, package: Package, project: Project, company: Company) -> ActivityRecording:
            activity_recording = ActivityRecording(
                start_date = make_datetime(f"{workrecord.start_date}T{workrecord.start_time}"),
                end_date = make_datetime(f"{workrecord.end_date}T{workrecord.end_time}"),
                title = workrecord.title,
                is_billable = package.custom_fields.get('abrechenbar', workrecord.is_billable) if package is not None else workrecord.is_billable,
                hours = workrecord.minutes_worked / 60,
                description = workrecord.description,
                driving_distance_km = 0,
                task_number = task.number,
                company_name = company.name if company is not None else '',
                company_shortname = company.short_name if company is not None else '',
                project_name = project.title,
                project_number = project.number,
                project_tags = [], #project.tags,
                package_id = package.id if package is not None else '',
                package_number = package.number if package is not None else '',
                package_title = package.title if package is not None else '',
                package_custom_fields = package.custom_fields if package is not None else {},
                email = user.email_address,
                project_role = task.custom_fields.get('rolle', ''),
                is_billable_raw = workrecord.is_billable,
                billing_cycle = project.custom_fields.get('abrechnungsart', ''),
                offer_number = project.custom_fields.get('angebotsnummer', ''),
                order_number = project.custom_fields.get('bestellnummer', ''),
                firstname = user.first_name,
                lastname = user.last_name,
                cost_center = '', #Optional[str],
                department = '', #Optional[str],
            )

            return activity_recording

        logger.debug(f"query controlling data from {from_date} to {to_date}")
        activity_recordings = []

        workrecords = self._core_client.get_work_records(from_date, to_date)


        for workrecord in workrecords:
            user = self._query_user_by_id(workrecord.work_employee_id)
            task = self._query_task_by_id(workrecord.booked_on_reference_id)
            package = self._query_package_by_id(task.parent_package_id)
            project = self._query_project_by_id(task.project_id)
            contact = self._query_contact_by_id(task.company_contact_id)
            company = self._query_company_by_id(project.company_id) if project is not None else None

            activity_recording = mapping(workrecord, user, task, package, project, company)

            activity_recordings.append(activity_recording)

        return activity_recordings
