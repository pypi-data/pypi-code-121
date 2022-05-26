from typing import Dict, TypeVar

T = TypeVar("T", bound="HttpError")


class HttpError(Exception):
    status_code: int

    def __init__(self, response: Dict[str, str], status_code: int):
        self.status_code = status_code
        super(HttpError, self).__init__(response)
