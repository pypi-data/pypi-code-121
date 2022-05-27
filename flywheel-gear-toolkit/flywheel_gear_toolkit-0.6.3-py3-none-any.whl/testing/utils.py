"""Utility fixtures."""
from unittest.mock import Mock

import pytest


@pytest.fixture
def make_concrete(mocker):
    """Make an abstract class concrete by patching its abstract methods

    Args:
        mocker: pytest-mock fixture
    """

    def _gen(cls):
        """Patch out abstract methods

        Args:
            cls: Class to make concrete
        """
        # Patch out abstract methods
        mocker.patch.object(cls, "__abstractmethods__", set())

    return _gen


@pytest.fixture(scope="function")
def get_docker_client(mocker):
    try:
        import docker
    except (ModuleNotFoundError, ImportError):
        raise RuntimeError("Please install the python docker sdk to use this fixture")

    spec = dir(docker.DockerClient)
    docker_client = Mock(spec=spec)

    get_docker_client = mocker.patch("docker.from_env", return_value=docker_client)

    return get_docker_client


@pytest.fixture(scope="function")
def docker_client(get_docker_client):
    return get_docker_client.return_value
