from dataclasses import dataclass

__all__ = [
    'Error',
]


@dataclass
class Error(Exception):
    error_code: int
    description: str
