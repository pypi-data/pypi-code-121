""" HTTP Request/Response 추상화를 위한 클래스 """
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Awaitable, Any, Callable, Type
from functools import wraps
import enum

from bs4 import BeautifulSoup

from ..exceptions import ClientError, ServerError

__all__ = (
    "Response",
    "HTTPRequestMethod",
    "BodyFormatter",
    "IRequestPostCondition",
    "BaseRequest",
    "DEFAULT_REQUEST_TIMEOUT",
)

DEFAULT_REQUEST_TIMEOUT: float = 30.0


@dataclass
class Response:
    """ HTTP Response 데이터 클래스 """

    status: int
    url: str
    reason: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    raw: bytes = b""
    text: str = ""
    cookies: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.headers = {key.lower(): value for key, value in self.headers.items()}

    def __bool__(self):
        return bool(self.status)

    @property
    def soup(self):
        try:
            return self._soup
        except AttributeError:
            self._soup = BeautifulSoup(self.text, features="html.parser")
            return self._soup

    @property
    def etc(self):
        try:
            return self._etc
        except AttributeError:
            self._etc: Dict[str, Any] = {}
            return self._etc


@enum.unique
class HTTPRequestMethod(enum.Enum):
    GET = "GET"
    POST = "POST"


@enum.unique
class BodyFormatter(enum.Enum):
    URL_ENCODE: str = "data"
    JSON: str = "json"


class IRequestPostCondition(metaclass=ABCMeta):
    """ HTTP request post-condition interface

    이 인터페이스를 상속한 모든 파생 클래스는 HTTP 응답 수신 이후 사후조건으로 실행됨
    """

    @staticmethod
    @abstractmethod
    def check(response: Response) -> None:
        pass


class _StatusCheck(IRequestPostCondition):
    """ Check HTTP response status code

    400번 이상의 상태 코드는 예외를 발생시킴
    4xx: ClientError
    5xx: ServerError
    """

    @staticmethod
    def check(response: Response) -> None:
        status = response.status
        n = status % 100
        if n == 4:
            raise ClientError(f"클라이언트 요청 오류입니다. -> 응답코드: {status}", response)
        elif n == 5:
            raise ServerError(f"서버 응답 오입니다. -> 응답코드: {status}", response)


class PostCondition:
    """ HTTP Request 요청의 사전/사후조건 처리를 위한 데코레이터

    사전조건: 타임아웃 설정
    사후조건: 응답 객체에 대한 사후조건 처리 (heckConditionBase 의 파생 클래스 실행)
    """

    def __init__(self, method: HTTPRequestMethod):
        self.method = method

    def __call__(
        self, request: Callable[..., Awaitable[Response]],
    ) -> Callable[..., Awaitable[Response]]:
        @wraps(request)
        async def check_condition(
            cls: Type["BaseRequest"], *args: Any, **kwargs: Any
        ) -> Response:
            response = await cls._request(self.method, *args, **kwargs)

            subclass: Type[IRequestPostCondition]
            for subclass in IRequestPostCondition.__subclasses__():
                subclass.check(response)
            return response

        return check_condition


class BaseRequest(metaclass=ABCMeta):
    """ HTTP Request abstract class

    파생 클래스는 _request 추상 메서드만 구현
    """

    @classmethod
    @PostCondition(HTTPRequestMethod.GET)
    async def get(
        cls,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        cookies: Dict[str, str] = None,
        verify: bool = True,
        allow_redirects: bool = False,
        timeout: Optional[float] = None,
        proxies: Optional[str] = None,
    ) -> Response:
        pass

    @classmethod
    @PostCondition(HTTPRequestMethod.POST)
    async def post(
        cls,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, str]] = None,
        body_encoding: BodyFormatter = BodyFormatter.URL_ENCODE,
        cookies: Dict[str, str] = None,
        verify: bool = True,
        allow_redirects: bool = False,
        timeout: Optional[float] = None,
        proxies: Optional[str] = None,
    ) -> Response:
        pass

    @classmethod
    @abstractmethod
    async def _request(
        cls,
        method: HTTPRequestMethod,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, str]] = None,
        body_encoding: BodyFormatter = BodyFormatter.URL_ENCODE,
        cookies: Dict[str, str] = None,
        verify: bool = True,
        allow_redirects: bool = False,
        timeout: Optional[float] = None,
        proxies: Optional[str] = None,
    ) -> Response:
        pass
