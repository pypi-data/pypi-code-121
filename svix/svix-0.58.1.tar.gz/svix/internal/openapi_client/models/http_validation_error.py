from typing import Dict, TypeVar

T = TypeVar("T", bound="HTTPValidationError")


class HTTPValidationError(Exception):
    status_code: int

    def __init__(self, response: Dict[str, str], status_code: int):
        self.status_code = status_code
        super(HTTPValidationError, self).__init__(response)
