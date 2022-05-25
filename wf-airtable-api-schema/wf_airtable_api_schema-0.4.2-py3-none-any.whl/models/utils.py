from typing import Type

from pydantic import BaseModel


def copy_field(from_model: Type[BaseModel], fname: str, to_annotations: dict):
    from_annotations = getattr(from_model, "__annotations__", {})
    to_annotations[fname] = from_annotations[fname]
