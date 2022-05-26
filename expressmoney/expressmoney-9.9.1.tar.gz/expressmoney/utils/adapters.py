from abc import ABC
from typing import Union

from django.contrib.auth import get_user_model

from expressmoney.api import PointClientError, PointServerError

User = get_user_model()


class AdapterError(Exception):
    pass


class BaseAdapter(ABC):
    _point_class = None
    _client_error_codes: tuple = ()
    _client_error_messages: dict = {}

    def create(self, payload: dict = None):
        try:
            self._point.create(payload=payload if payload is not None else self.payload)
        except PointClientError as e:
            self._raise_exception(e.detail.get(next(iter(e.detail)))[-1])

    def __init__(self, user: Union[int, User], timeout=(30, 30)):
        self._validate_client_error_messages()
        if self._point_class is None:
            raise AdapterError('Point class not set.')
        user = user if isinstance(user, User) else User.objects.get(id=user)
        self._point = self._point_class(user=user, timeout=timeout)
        self.__payload = {}
        super().__init__()

    def _raise_exception(self, error_message: str = None, is_server_error=False):
        if not is_server_error and error_message is None:
            raise AdapterError('Set error message for client error.')
        if is_server_error:
            raise PointServerError('server_error' if error_message is None else error_message[:1024])
        else:
            raise PointClientError(self._get_error_code(error_message=error_message))

    def _get_error_code(self, error_message: str):
        if not isinstance(error_message, str):
            raise AdapterError('Only string error message accepted.')
        for key, value in self._client_error_messages.items():
            if error_message in value:
                return key
        return 'unknown_client_error'

    def _validate_client_error_messages(self):
        for error_code in self._client_error_codes:
            if error_code not in self._client_error_messages.keys():
                raise AdapterError(f'Error message not set for error code {error_code}.')

    @property
    def payload(self):
        return self.__payload

    @payload.setter
    def payload(self, value: dict):
        if not isinstance(value, dict):
            raise AdapterError('Only dict payload.')
        self.__payload = value


class FactoryError(Exception):
    pass


class BaseFactory:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
