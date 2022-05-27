"""Pytest configuration for model algorithm tests."""
from unittest.mock import Mock

from _pytest.fixtures import fixture


@fixture
def model() -> Mock:
    """Returns mock model."""
    mod = Mock(steps=10)
    mod.fit = Mock()
    mod.evaluate = Mock()
    mod.evaluate.return_value = ([0.9], [0.8])
    mod.backend_tensor_shim = Mock()
    return mod
