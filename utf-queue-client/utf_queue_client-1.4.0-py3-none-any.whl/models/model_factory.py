from . import (
    BaseModelWithValidation,
)
from typing import Type, Dict, TypeVar

T = TypeVar("T")


"""
Maps a model type to a set of defaults
"""
DEFAULTS_MAP: Dict[Type[BaseModelWithValidation], dict] = {
}


def create_model_with_defaults(model_type: Type[T], **kwargs) -> T:
    if model_type in DEFAULTS_MAP:
        return model_type(DEFAULTS_MAP[model_type], **kwargs)

    return model_type(**kwargs)
