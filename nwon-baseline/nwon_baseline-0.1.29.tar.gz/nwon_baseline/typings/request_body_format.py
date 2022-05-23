from enum import Enum


class RequestBodyFormat(Enum):
    Multipart = "multipart"
    Json = "json"


__all__ = ["RequestBodyFormat"]
