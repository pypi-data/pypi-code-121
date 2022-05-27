"""Fixtures related to BitfountSchema."""
from unittest.mock import Mock, NonCallableMock, create_autospec

from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.data.schema import BitfountSchema


@fixture
def mock_bitfount_schema_load(mocker: MockerFixture) -> Mock:
    """Mocks out the BitfountSchema.load() classmethod.

    Mock will simply return the dict passed into the load() method.
    """
    mock_load: Mock = mocker.patch.object(BitfountSchema, "load", autospec=True)
    mock_load.side_effect = lambda data: data
    return mock_load


@fixture
def mock_bitfount_schema() -> NonCallableMock:
    """Mocked BitfountSchema for tests."""
    mock_schema: NonCallableMock = create_autospec(BitfountSchema, instance=True)
    return mock_schema
