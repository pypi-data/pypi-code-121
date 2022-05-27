import enum

from abc import ABCMeta, abstractmethod
from typing import Callable, TypeVar

from jijzept.client import JijZeptClient

_FuncT = TypeVar("_FuncT", bound=Callable)
_TBaseResponse = TypeVar("_TBaseResponse", bound="BaseResponse")


class APIStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    UNKNOWNERROR = "UNKNOWNERROR"


class BaseResponse(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_json_obj(cls, json_obj) -> None:
        """abstract method for initializing object from JSON data

        Args:
            json_obj: JSON data
        """

    @classmethod
    @abstractmethod
    def empty_data(cls) -> None:
        """abstract method for generating empty data"""

    def _set_config(self, client: JijZeptClient, solution_id: str):
        self._client = client
        self.solution_id = solution_id

    def set_status(self, status: APIStatus):
        self._status = status

    def set_err_dict(self, err_dict: dict):
        self._err_dict = err_dict

    @property
    def status(self):
        if hasattr(self, "_status"):
            return self._status
        else:
            return APIStatus.PENDING

    @property
    def error_message(self):
        if hasattr(self, "_err_dict"):
            return self._err_dict
        else:
            return {}

    @classmethod
    def empty_response(
        cls, status: APIStatus, client: JijZeptClient, solution_id: str, err_dict={}
    ):
        """generate empty_response

        Args:
            status (APIStatus): status
            client (JijZeptClient): client
            solution_id (str): solution_id
            err_dict:
        """
        response: cls = cls.empty_data()
        response._set_config(client, solution_id)
        response.set_status(status)
        response.set_err_dict(err_dict)
        return response

    def get_result(self: _TBaseResponse) -> _TBaseResponse:
        """get result from cloud.

        If status is updated. update self data
        """
        if self.status in {APIStatus.PENDING, APIStatus.RUNNING}:
            response = self._client.fetch_result(self.solution_id)
            if response["status"] == APIStatus.SUCCESS.value:
                temp_obj = self.from_json_obj(response["solution"])
                temp_obj.set_status(APIStatus.SUCCESS)
                # update myself
                self.__dict__.update(temp_obj.__dict__)
                return self

            elif response["status"] == APIStatus.FAILED.value:
                self.set_status(APIStatus.FAILED)
                # store error info
                self.set_err_dict(response["solution"])
                return self

            elif response["status"] == APIStatus.UNKNOWNERROR.value:
                self.set_status(APIStatus.UNKNOWNERROR)
                return self

            else:
                self.set_status(APIStatus(response["status"]))
                return self
        else:
            return self

    def __repr__(self):
        return_str = self.status.__repr__()
        if self.status == APIStatus.FAILED:
            return_str += "\n"
            return_str += str(self.error_message)

        return return_str

    def __str__(self):
        return_str = self.status.__repr__()
        if self.status == APIStatus.FAILED:
            return_str += "\n"
            return_str += str(self.error_message)

        return return_str
