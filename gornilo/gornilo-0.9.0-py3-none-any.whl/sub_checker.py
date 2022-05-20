import abc
from abc import abstractmethod
from gornilo.models.checksystem_request import PutRequest, GetRequest
from gornilo.models.verdict.verdict import Verdict


class VulnChecker(abc.ABC):
    @staticmethod
    @abstractmethod
    def put(request: PutRequest) -> Verdict:
        pass

    @staticmethod
    @abstractmethod
    def get(request: GetRequest) -> Verdict:
        pass
