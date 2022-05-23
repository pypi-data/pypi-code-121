""" 패키지에서 사용되는 예외

- RootError
    - RequestError
        - RequestTimeoutError
        - StatusError
            - ClientError
            - ServerError
    - ResponseError (paramter에 response 가 추가됨)
        - ParsingError
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .reqeust import Response

__all__ = (
    "RootError",
    "RequestError",
    "ResponseError",
    "RequestTimeoutError",
    "ClientError",
    "ServerError",
    "ParsingError",
)


class RootError(Exception):
    """ 모듈 최상위 에러 """


class RequestError(RootError):
    """ 요청과 관련된 top-level 에러 """


class ResponseError(RootError):
    """ 응답과 관련된 top-level 에러 """

    def __init__(self, message, response: "Response"):
        super().__init__(message)
        self.response = response


class RequestTimeoutError(RequestError):
    """ 요청 타임아웃 """


class StatusError(RequestError):
    """ HTTP 응답 코드가 400 이상인 경우 """


class ClientError(StatusError):
    """ 클라이언트 요청이 서버에서 처리할 수 없는 경우 (4xx) """


class ServerError(StatusError):
    """ 서버의 에러로 정상적인 반환이 불가한 경우 (5xx) """


class ParsingError(ResponseError):
    """ 구문 문석 에러 """
