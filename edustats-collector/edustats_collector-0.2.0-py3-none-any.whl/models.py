"""
Lesson -> Assignment -> Exercise -> Result
"""
from __future__ import annotations
from datetime import date

from pydantic import BaseModel, conlist
from result_collector_client.collector import CollectorClient


class RequestsMixin:
    def get(self, *, client: CollectorClient, result_class: BaseModel = None):
        URL_PATH = self.get_url_path()

        if self.id is not None:
            if existing := client.get(url_path=f'{URL_PATH}/{self.id}'):
                return self.__class__(**existing)
            return None

        existing_items = client.get(url_path=f'{URL_PATH}')
        search_fields = self.get_search_fields()
        if existing := next(
            (
                a
                for a in existing_items
                if all([getattr(self, sf) == a[sf] for sf in search_fields])
            ),
            False,
        ):
            return (
                self.__class__(**existing)
                if result_class is None
                else result_class(**existing)
            )
        return None

    def create(
        self, *, client: CollectorClient, result_class: BaseModel = None
    ):
        URL_PATH = self.get_url_path()
        # nothing found, create it
        created = client.post(url_path=f'{URL_PATH}', data=self.json())
        return (
            self.__class__(**created)
            if result_class is None
            else result_class(**created)
        )

    def delete(self, *, client: CollectorClient):
        URL_PATH = self.get_url_path()
        # Lesson -> Assignment -> Exercise -> Result
        if self.id is not None:
            client.delete(url_path=f'{URL_PATH}/{self.id}')
            return None

    def update(
        self, *, client: CollectorClient, result_class: BaseModel = None
    ):
        URL_PATH = self.get_url_path()
        # Lesson -> Assignment -> Exercise -> Result
        if self.id is not None:
            item = client.delete(url_path=f'{URL_PATH}/{self.id}')
            return (
                self.__class__(**item)
                if result_class is None
                else result_class(**item)
            )

    def get_or_create(self, *, client: CollectorClient):
        if item := self.get(client=client):
            return item
        return self.create(client=client)


class Lesson(BaseModel, RequestsMixin):
    id: int
    backlink: str = None

    def get_url_path(self):
        return '/lessons'

    def get_search_fields(self):
        return ['description']


class Exercise(BaseModel, RequestsMixin):
    id: int = None
    assignment: int
    description: str
    passing_score: int = None
    max_score: int = None
    optional: bool = None
    backlink: str = None

    def get_url_path(self):
        return '/exercises'

    def get_search_fields(self):
        return ['assignment', 'description']


class Assignment(BaseModel, RequestsMixin):
    id: int = None
    lesson: int
    description: str
    deadline: date = None
    attestation: int = None
    exercises: conlist(Exercise, min_items=0) = None
    backlink: str = None

    def get_url_path(self):
        return '/assignments'

    def get_search_fields(self):
        return ['lesson', 'description']


class Result(BaseModel, RequestsMixin):
    id: int = None
    student: int
    exercise: int
    score: int = None
    artifact: str = ''
    backlink: str = None

    def get_url_path(self):
        return '/results'

    def get_search_fields(self):
        return ['exercise', 'student']


class ResultWithStudentEmail(BaseModel, RequestsMixin):
    id: int = None
    student: str
    exercise: int
    score: int = None
    artifact: str = ''
    backlink: str = None

    def get_url_path(self):
        return '/results'

    def get_search_fields(self):
        return ['exercise', 'student']
