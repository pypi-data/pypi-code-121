__all__ = ('Tasks', 'Request')

import abc
import datetime
import json
import re
from contextlib import suppress
from typing import Union

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.http import urlencode
from google.auth.transport.requests import Request as GoogleRequest
from google.cloud import tasks_v2
from google.oauth2 import id_token
from google.protobuf import timestamp_pb2
from rest_framework_simplejwt.tokens import RefreshToken

from expressmoney.utils import status

User = get_user_model()


class HttpClient(abc.ABC):
    """Abstract HTTP client"""

    _client = None
    _project = 'expressmoney' if settings.IS_PROD else 'expressmoney-dev-1'

    def __init__(self,
                 service: str = 'default',
                 path: str = '/',
                 query_params: Union[None, dict] = None,
                 access_token: str = None,
                 ):
        """
        Common params for all http clients
        Args:
            service: 'default'
            path: '/user'
            access_token: 'Bearer DFD4345345D'
        """
        self._service = service
        self._path = path
        self._query_params = query_params
        self._access_token = access_token

    @abc.abstractmethod
    def get(self):
        pass

    @abc.abstractmethod
    def post(self, payload: dict):
        pass

    @abc.abstractmethod
    def put(self, payload: dict):
        pass


class BaseTasks(HttpClient):
    """Base Google Cloud Tasks Client"""

    _client = tasks_v2.CloudTasksClient()

    def __init__(self,
                 service: str = 'default',
                 path: str = '/',
                 access_token: str = None,
                 location: str = 'europe-west1',
                 queue: str = 'attempts-1',
                 in_seconds: int = None):
        """
        Params for CloudTask client
        Args:
            service: 'default'
            path: '/user'
            access_token: 'Bearer DFD4345345D'
            queue: 'my-appengine-queue'
            location: 'europe-west1'
            in_seconds: None
        """
        super().__init__(service=service, path=path, access_token=access_token)
        self._queue_path = self._client.queue_path(self._project, location, queue)
        self._in_seconds = in_seconds

    def get(self):
        task = self._create_task_body(tasks_v2.HttpMethod.GET)
        task = self._remove_empty_headers(task)
        self._client.create_task(parent=self._queue_path, task=task)

    def post(self, payload: dict):
        task = self._create_task_body(tasks_v2.HttpMethod.POST)
        task = self._add_payload(task, payload)
        task = self._remove_empty_headers(task)
        self._client.create_task(parent=self._queue_path, task=task)

    def put(self, payload: dict):
        task = self._create_task_body(tasks_v2.HttpMethod.PUT)
        task = self._add_payload(task, payload)
        task = self._remove_empty_headers(task)
        self._client.create_task(parent=self._queue_path, task=task)

    def _create_task_body(self, http_method: tasks_v2.HttpMethod):
        task = {
            'app_engine_http_request': {
                'http_method': http_method,
                'relative_uri': self._path,
                'headers': {},
                'app_engine_routing': {
                    'service': self._service,
                    'version': '',
                    'instance': '',
                    'host': '',

                }
            },
        }
        task = self.__convert_in_seconds(task)
        task = self.__add_authorization(task)
        return task

    @staticmethod
    def _add_payload(task: dict, payload: dict) -> dict:
        payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        task["app_engine_http_request"]["body"] = payload
        task["app_engine_http_request"]["headers"]['Content-Type'] = 'application/json'
        return task

    @staticmethod
    def _remove_empty_headers(task):
        if len(task['app_engine_http_request']['headers']) == 0:
            del task['app_engine_http_request']['headers']
        return task

    def __add_authorization(self, task):
        if self._access_token:
            task["app_engine_http_request"]["headers"]['X-Forwarded-Authorization'] = f'Bearer {self._access_token}'
        return task

    def __convert_in_seconds(self, task: dict) -> dict:
        if self._in_seconds is not None:
            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._in_seconds)
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)
            task['schedule_time'] = timestamp
        return task


class BaseRequest(HttpClient):
    """Base HTTP Client"""

    def __init__(self,
                 service: str = None,
                 path: str = '/',
                 query_params: Union[None, dict] = None,
                 access_token: str = None,
                 timeout: tuple = (30, 30)):
        super().__init__(service=service,
                         path=path,
                         query_params=query_params,
                         access_token=access_token,
                         )
        self._timeout = timeout

    def get(self, url=None):
        response = requests.get(url if url else self.url, headers=self._headers, timeout=self._timeout)
        return response

    def post(self, payload: dict):
        response = requests.post(self.url, json=payload, headers=self._headers, timeout=self._timeout)
        return response

    def put(self, payload: dict = None):
        payload = {} if payload is None else payload
        response = requests.put(self.url, json=payload, headers=self._headers, timeout=self._timeout)
        return response

    def post_file(self, file, file_name: str, type_: int = 1, is_public=False):
        """
        Save file in Google Storage
        Args:
            file: BytesIO file
            file_name: "name_file.pdf"
            type_: 1 - other files. All types see in storage service
            is_public: True - access to file without auth.

        Returns:

        """
        if len(file_name.split('.')) == 0:
            raise Exception('File name in format "name_file.pdf"')

        name, ext = file_name.split('.')
        name = f'{name}_{datetime.datetime.now().timestamp()}'
        name = re.sub('[^0-9a-zA-Z_]', '', name)
        new_file_name = f'{name}.{ext}'

        if re.match('^_[0-9]{16}$', name):
            raise Exception('File name incorrect. Example correct "name_file.pdf"')

        data = {
            'name': name,
            'type': type_,
            'is_public': is_public,

        }

        with suppress(Exception):
            file = getattr(file, 'file')

        response = requests.post(
            url=self.url,
            data=data,
            files={"file": (new_file_name, file)},
            headers=self._headers,
            timeout=self._timeout
        )
        if not any((status.is_success(response.status_code), status.is_client_error(response.status_code))):
            try:
                raise Exception(f'{response.status_code}:{response.url}:{response.json()}')
            except Exception:
                raise Exception(f'{response.status_code}:{response.url}:{response.text}')
        return response

    @property
    def url(self):
        local_url = 'http://127.0.0.1:8000'
        domain = f'https://{self._service}-dot-{self._project}.appspot.com' if self._service else local_url
        url = f'{domain}{self._path}'
        url_with_params = url if self._query_params is None else f'{url}?{urlencode(self._query_params)}'
        return url_with_params

    @property
    def _headers(self):
        headers = dict()
        headers.update(self._get_authorization())
        return headers

    def _get_authorization(self) -> dict:
        return {'X-Forwarded-Authorization': f'Bearer {self._access_token}'} if self._access_token else {}


class Tasks(BaseTasks):
    """Google Cloud Tasks Client for Django user"""

    def __init__(self,
                 service: str = 'default',
                 path: str = '/',
                 user: Union[None, int, User] = None,
                 location: str = 'europe-west1',
                 queue: str = 'attempts-1',
                 in_seconds: int = None):
        user = None if user is None else user if isinstance(user, User) else User.objects.get(pk=user)
        access_token = RefreshToken.for_user(user).access_token if user is not None else None
        super().__init__(service=service,
                         path=path,
                         access_token=access_token,
                         location=location,
                         queue=queue,
                         in_seconds=in_seconds
                         )


class Request(BaseRequest):
    """HTTP Client for Django user"""

    def __init__(self,
                 service: str = None,
                 path: str = '/',
                 query_params: Union[None, dict] = None,
                 user: Union[None, int, User] = None,
                 timeout: tuple = (30, 30),
                 ):
        user = None if user is None else user if isinstance(user, User) else User.objects.get(pk=user)
        access_token = RefreshToken.for_user(user).access_token if user is not None else None
        super().__init__(service=service,
                         path=path,
                         query_params=query_params,
                         access_token=access_token,
                         timeout=timeout
                         )

    def _get_authorization(self) -> dict:
        authorization = super()._get_authorization()
        open_id_connect_token = id_token.fetch_id_token(GoogleRequest(), settings.IAP_CLIENT_ID)
        iap_token = {'Authorization': f'Bearer {open_id_connect_token}'}
        authorization.update(iap_token)
        return authorization
