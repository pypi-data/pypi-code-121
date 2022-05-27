"""Fixtures related to {federated,hub} helper.py functions."""
from typing import Any, Callable, Dict, Iterable
from unittest.mock import Mock, create_autospec

from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.config import BITFOUNT_STORAGE_PATH
from bitfount.hub.authentication_flow import BitfountSession


@fixture
def mock_bitfount_session(mocker: MockerFixture) -> Mock:
    """Mock out BitfountSession in the helper module."""
    # BitfountSession is used in hub creation, need to mock it out
    mock_bitfount_session: Mock = mocker.patch(
        "bitfount.hub.helper.BitfountSession",
    )
    mock_bitfount_session.return_value = create_autospec(
        BitfountSession,
        instance=True,
        # attribute needed in mock
        user_storage_path=BITFOUNT_STORAGE_PATH / "test_username",
        username="test_username",
    )
    return mock_bitfount_session


@fixture
def apply_mock_get_pod_public_keys(mocker: MockerFixture) -> Callable[[str], Mock]:
    """Allows mocking out the get_pod_public_keys function.

    Replaces it with a function that will return a dict of mock public keys.

    Returns a callable that can be used to apply the patch to the right location.
    e.g. apply_mock_get_pod_public_keys("bitfount.federated.modeller._get_pod_public_keys")  # noqa: B950
    """

    def _get_mocker_public_keys(
        pod_identifiers: Iterable[str],
        *_args: Any,
        **_kwargs: Any,
    ) -> Dict[str, Mock]:
        """Return a dict of pod identifiers to mock public keys.

        *_args and **_kwargs allows the signature to match that of the existing
        function.
        """
        return {pod_identifier: Mock() for pod_identifier in pod_identifiers}

    def apply_patch(patch_location: str) -> Mock:
        """Applies the patched method to the location specified."""
        return mocker.patch(
            patch_location,
            autospec=True,
            side_effect=_get_mocker_public_keys,
        )

    return apply_patch
