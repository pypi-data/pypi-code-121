"""Pytest configuration for protocols tests."""
from unittest.mock import Mock, create_autospec

from pytest import fixture

from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.hub.api import BitfountHub
from bitfount.hub.authentication_flow import BitfountSession


@fixture
def mock_algorithm() -> Mock:
    """Returns mock untyped algorithm."""
    return Mock()


@fixture
def mock_modeller_mailbox() -> Mock:
    """Returns mock mailbox."""
    mock_modeller_mailbox: Mock = create_autospec(_ModellerMailbox, instance=True)
    return mock_modeller_mailbox


@fixture
def mock_worker_mailbox() -> Mock:
    """Returns mock mailbox."""
    mock_worker_mailbox: Mock = create_autospec(_WorkerMailbox, instance=True)
    return mock_worker_mailbox


@fixture
def mock_hub() -> Mock:
    """Returns mock BitfountHub."""
    mock_hub: Mock = create_autospec(BitfountHub, instance=True)
    mock_hub.session = create_autospec(BitfountSession, instance=True)
    return mock_hub
