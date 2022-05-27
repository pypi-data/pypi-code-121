from typing import Dict, TypeVar

T = TypeVar("T", bound="ValidationError")


class ValidationError(Exception):
    status_code: int

    def __init__(self, response: Dict[str, str], status_code: int):
        self.status_code = status_code
        super(ValidationError, self).__init__(response)
