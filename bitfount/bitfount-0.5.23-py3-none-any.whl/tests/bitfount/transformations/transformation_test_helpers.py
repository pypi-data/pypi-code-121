"""Contains helper methods for transformation tests."""
from typing import Any, Type

import pytest

from bitfount.transformations.base_transformation import (
    TRANSFORMATION_REGISTRY,
    Transformation,
)
from bitfount.transformations.exceptions import TransformationRegistryError


def gen_name_fails(cls: Type[Transformation]) -> None:
    """Test that the _gen_name function fails for target Transformation."""
    with pytest.raises(TransformationRegistryError):
        cls._gen_name()


def gen_name_test(cls: Type[Transformation], registry_name: str, **kwargs: Any) -> None:
    """Test that the created cls instance has a correctly generated random name."""
    t = cls(**kwargs)
    assert t.name == f"{registry_name}_FAKE_HEX"


def registration_test(cls: Type[Transformation], registry_name: str) -> None:
    """Test that a class is correctly registered with the desired name."""
    assert registry_name in TRANSFORMATION_REGISTRY
    assert TRANSFORMATION_REGISTRY[registry_name] == cls
