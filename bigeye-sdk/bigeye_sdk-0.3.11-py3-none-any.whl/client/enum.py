from __future__ import annotations

import enum


class Method(str, enum.Enum):
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    DELETE = 'DELETE'

    def __str__(self):
        return self.name
