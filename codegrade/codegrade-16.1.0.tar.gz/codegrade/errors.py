"""The exception that is raised if an unknown exception is encountered.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
from httpx import Response


class ApiResponseError(Exception):
    """An exception raised when an unknown response occurs"""

    def __init__(self, *, response: Response):
        super().__init__()
        self.response: Response = response
        try:
            self.json_data = response.json()
        except:
            self.json_data = None

    def __str__(self) -> str:
        return f"{super().__str__()}: {self.response!r} ({self.json_data})"
