from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Union, Optional, Type, Sequence
from functools import wraps

from ..reqeust import Response, BaseRequest


__all__ = (
    "HTTPClient",
    "ResourceData",
    "ErrorData",
    "SemesterData",
    "APIResponseType",
    "IParser",
    "ILoginFetcher",
    "IGeneralFetcher",
    "ISemesterFetcher",
    "ParserPrecondition",
)


class HTTPClient:
    connector: Optional[Type[BaseRequest]] = None

    @classmethod
    def set_auto(cls):
        http: Type[BaseRequest]
        for http in BaseRequest.__subclasses__():
            cls.connector = http

    @classmethod
    def set(cls, connector: Type[BaseRequest]):
        cls.connector = connector


@dataclass
class ResourceData:
    data: Dict[str, Any]
    link: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorData:
    error: Dict[str, Any]
    link: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemesterData:
    selected: str
    selectable: Sequence[str]


APIResponseType = Union[ResourceData, ErrorData]


class IParser(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def parse(cls, response: Response) -> APIResponseType:
        """ html 또는 raw_data 를 사용가능한 데이터로 변환

        ParsingError: 의도되지 않은 parse 실패
        """
        pass


class ILoginFetcher(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    async def fetch(
        cls,
        user_id: str,
        user_pw: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        pass


class IGeneralFetcher(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        pass


class ISemesterFetcher(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        semester: Optional[str] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        pass


class ParserPrecondition:
    def __init__(self, baseclass):
        self.baseclass = baseclass

    def __call__(self, func):
        @wraps(func)
        def wrapper(cls, response: Response):
            for subclass in self.baseclass.__subclasses__():
                error = subclass.is_blocking(response)
                if error:
                    return error
            return func(cls, response)

        return wrapper


HTTPClient.set_auto()
