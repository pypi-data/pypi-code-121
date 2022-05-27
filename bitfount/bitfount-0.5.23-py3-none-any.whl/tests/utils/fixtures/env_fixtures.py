"""Fixtures related to environment setup, envvars, etc."""
from typing import Iterator

from _pytest.monkeypatch import MonkeyPatch
from pytest import fixture

import bitfount
from tests.utils import PytestRequest


@fixture(autouse=True)
def env_fix(monkeypatch: MonkeyPatch) -> None:
    """Fix the environment into a known state for tests."""
    # Sets the environment and engine to use the BasicDataFactory. If a specific
    # engine is needed (aka PyTorch), this must be overridden in a fixture of the
    # same name in a conftest.py file closer to the test.
    monkeypatch.setenv("BITFOUNT_ENGINE", bitfount.config._BASIC_ENGINE)
    monkeypatch.setattr(
        "bitfount.config.BITFOUNT_ENGINE", bitfount.config._BASIC_ENGINE
    )


@fixture
def environment(monkeypatch: MonkeyPatch, request: PytestRequest) -> None:
    """Sets up the BITFOUNT_ENVIRONMENT environment variable."""
    environment = request.param
    if environment:
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", environment)


@fixture(autouse=True)
def cache_clear() -> Iterator[None]:
    """Clears the cache of get_environment before and after each test."""
    bitfount.config._get_environment.cache_clear()
    yield
    bitfount.config._get_environment.cache_clear()
