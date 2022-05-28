from enum import unique, IntEnum
from multiprocessing import Lock
from typing import Optional

from hbutils.model import get_repr_info

from .process import ProcessResult
from .resource import ResourceLimit


@unique
class RunResultStatus(IntEnum):
    NOT_COMPLETED = -1
    SUCCESS = 0
    CPU_TIME_LIMIT_EXCEED = 1
    REAL_TIME_LIMIT_EXCEED = 2
    MEMORY_LIMIT_EXCEED = 3
    RUNTIME_ERROR = 4
    SYSTEM_ERROR = 5

    @property
    def ok(self):
        """
        :return: run success or not
        """
        return self == RunResultStatus.SUCCESS

    @property
    def completed(self):
        """
        :return: process completed or not
        """
        return self != RunResultStatus.NOT_COMPLETED


class RunResult:
    def __init__(self, limit: ResourceLimit, result: Optional[ProcessResult]):
        """
        :param limit: resource limit
        :param result: process running result
        """
        self.__limit = limit
        self.__result = result
        self.__lock = Lock()

    def __get_status(self) -> RunResultStatus:
        """
        Get status information
        :return: status information
        """
        if self.__result is None:
            return RunResultStatus.NOT_COMPLETED
        elif self.__limit.max_cpu_time is not None and self.__result.cpu_time > self.__limit.max_cpu_time:
            return RunResultStatus.CPU_TIME_LIMIT_EXCEED
        elif self.__limit.max_real_time is not None and self.__result.real_time > self.__limit.max_real_time:
            return RunResultStatus.REAL_TIME_LIMIT_EXCEED
        elif self.__limit.max_memory is not None and self.__result.max_memory > self.__limit.max_memory:
            return RunResultStatus.MEMORY_LIMIT_EXCEED
        elif self.__result.exitcode != 0:
            return RunResultStatus.RUNTIME_ERROR
        elif not self.__result.ok:
            return RunResultStatus.SYSTEM_ERROR
        else:
            return RunResultStatus.SUCCESS

    @property
    def limit(self) -> ResourceLimit:
        """
        :return: resource limit
        """
        return self.__limit

    @property
    def result(self) -> ProcessResult:
        """
        :return: process running result
        """
        with self.__lock:
            return self.__result

    @property
    def status(self) -> RunResultStatus:
        """
        :return: current status
        """
        with self.__lock:
            return self.__get_status()

    @property
    def ok(self) -> bool:
        """
        :return: process run success or not
        """
        with self.__lock:
            return self.__result is not None and self.__result.ok and self.__get_status().ok

    @property
    def completed(self) -> bool:
        """
        :return: process run completed or not
        """
        with self.__lock:
            return self.__get_status().completed

    def __repr__(self):
        """
        :return: string representation format
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('status', lambda: self.status.name),
                ('exitcode', (lambda: self.result.exitcode, lambda: self.result.exitcode != 0)),
                ('signal', (lambda: self.result.signal.name, lambda: self.result.signal is not None)),
            ],
        )

    @property
    def json(self):
        """
        :return: get run result information
        """
        return {
            'limit': self.limit.json,
            'result': self.result.json if self.result else None,
            'status': self.status.name,
            'ok': self.ok,
            'completed': self.completed,
        }
