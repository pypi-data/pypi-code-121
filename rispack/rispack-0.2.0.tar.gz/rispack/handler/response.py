import json
from http import HTTPStatus
from typing import Dict, List, Union


class Response:
    def __init__(
        self, status_code: HTTPStatus = HTTPStatus.OK, body: str = "", headers=None
    ) -> None:
        self.statusCode = status_code.value
        self.body = body
        self.headers = {"Access-Control-Allow-Origin": "*"}

        if isinstance(body, (dict, list)):
            self.body = json.dumps(body, ensure_ascii=False)
        else:
            self.body = body

        if headers and isinstance(headers, dict):
            self.headers.update(headers)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def ok(cls, data: dict = {}):
        return cls(HTTPStatus.OK, {"data": data})

    @classmethod
    def forbidden(cls, message: str = None):
        message = message or "You shall not pass!"

        error = {"errors": [{"id": "forbidden", "message": message}]}

        return cls(HTTPStatus.FORBIDDEN, error)

    @classmethod
    def internal_server_error(cls, message: str = None):
        message = message or "An unexpected error has occurred."

        error = {"errors": [{"id": "internal_server_error", "message": message}]}

        return cls(HTTPStatus.INTERNAL_SERVER_ERROR, error)

    @classmethod
    def bad_request(cls, message: Union[Dict[str, str], str] = None) -> Dict[str, List]:
        message = message or "bad request"

        error = {"errors": [{"id": "bad_request", "message": message}]}

        return cls(HTTPStatus.BAD_REQUEST, error)

    @classmethod
    def not_found(cls, message: str = None) -> Dict[str, List]:
        message = message or "Resource not found"

        error = {"errors": [{"id": "not_found", "message": message}]}

        return cls(HTTPStatus.NOT_FOUND, error)
