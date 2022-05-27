"""Tests hub helper.py."""
import logging
from pathlib import Path
from typing import Dict, Optional
from unittest.mock import MagicMock, Mock, create_autospec

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
import pytest
from pytest import fixture
from pytest_lazyfixture import lazy_fixture
from pytest_mock import MockerFixture
import yaml

import bitfount
from bitfount.data.schema import BitfountSchema
from bitfount.federated.encryption import _RSAEncryption
from bitfount.hub.api import (
    _DEV_AM_URL,
    _DEV_HUB_URL,
    _STAGING_AM_URL,
    _STAGING_HUB_URL,
    PRODUCTION_AM_URL,
    PRODUCTION_HUB_URL,
    BitfountAM,
    BitfountHub,
)
from bitfount.hub.authentication_flow import (
    _DEVELOPMENT_CLIENT_ID,
    _PRODUCTION_CLIENT_ID,
    _STAGING_CLIENT_ID,
    BitfountSession,
)
from bitfount.hub.exceptions import PodDoesNotExistError
from bitfount.hub.helper import (
    _check_known_pods,
    _create_access_manager,
    _create_bitfount_session,
    _create_bitfounthub,
    _default_bitfounthub,
    _get_pod_public_key,
    _save_key_to_key_store,
    get_pod_schema,
)
from tests.bitfount import TEST_SECURITY_FILES
from tests.utils.helper import unit_test


@unit_test
class TestHelperFunctions:
    """Test hub helper functions."""

    @fixture
    def username(self) -> str:
        """Username for tests."""
        return "test_username"

    @fixture
    def public_key_path(self) -> Path:
        """Path to test public key file."""
        return TEST_SECURITY_FILES / "test_public.testkey"

    @fixture
    def mock_key_store(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
        """A mock keystore for use with modeller."""
        key_store_path = tmp_path / "known_workers.yml"
        monkeypatch.setattr(bitfount.hub.helper, "BITFOUNT_KEY_STORE", key_store_path)
        return key_store_path.expanduser()

    @fixture
    def mock_input(self, monkeypatch: MonkeyPatch) -> MagicMock:
        """Mock `builtins.input`."""
        my_mock = MagicMock()
        monkeypatch.setattr("builtins.input", my_mock)
        return my_mock

    @fixture
    def test_url(self) -> str:
        """Test URL."""
        return "not.a.real.url.com"

    @pytest.mark.parametrize(
        "input_url, expected_client_id",
        [
            (PRODUCTION_HUB_URL, _PRODUCTION_CLIENT_ID),
            (_STAGING_HUB_URL, _STAGING_CLIENT_ID),
            ("localhost:8888", _DEVELOPMENT_CLIENT_ID),
        ],
    )
    def test_create_bitfount_session_with_different_urls(
        self, expected_client_id: str, input_url: str, username: str
    ) -> None:
        """Tests private _create_bitfount_session function with different urls."""
        session = _create_bitfount_session(url=input_url, username=username)
        assert isinstance(session, BitfountSession)
        assert session.client_id == expected_client_id
        assert session.user_storage_path.stem == username

    @pytest.mark.parametrize(
        "environment, input_url, expected_url",
        [
            ("production", None, PRODUCTION_HUB_URL),
            ("staging", None, _STAGING_HUB_URL),
            ("dev", None, _DEV_HUB_URL),
            (None, lazy_fixture("test_url"), lazy_fixture("test_url")),
        ],
        indirect=["environment"],
    )
    def test_create_bitfounthub_with_different_environments(
        self,
        environment: None,
        expected_url: str,
        input_url: Optional[str],
        mock_bitfount_session: Mock,
        monkeypatch: MonkeyPatch,
        username: str,
    ) -> None:
        """Tests create_bitfounthub with production, staging and local urls.

        We mock BitfountSession to avoid authenticating.
        """
        hub = _create_bitfounthub(username=username, url=input_url)
        assert isinstance(hub, BitfountHub)
        assert hub.url == expected_url

    @pytest.mark.parametrize(
        "environment, input_url, expected_url",
        [
            ("production", None, PRODUCTION_AM_URL),
            ("staging", None, _STAGING_AM_URL),
            ("dev", None, _DEV_AM_URL),
            (None, lazy_fixture("test_url"), lazy_fixture("test_url")),
        ],
        indirect=["environment"],
    )
    def test_create_access_manager_with_different_environments(
        self,
        environment: None,
        expected_url: str,
        input_url: Optional[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Tests create_access_manager with production, staging and local urls."""
        session = Mock()

        am = _create_access_manager(session, input_url)
        assert isinstance(am, BitfountAM)
        assert am.access_manager_url == expected_url
        assert am.session == session

    def test__get_pod_public_key(
        self,
        caplog: LogCaptureFixture,
        mock_key_store: Path,
        mocker: MockerFixture,
        public_key_path: Path,
    ) -> None:
        """Tests _get_pod_public_key helper function."""
        # Mock out the hub and RSA key loading components
        mock_load_public_key = mocker.patch.object(_RSAEncryption, "load_public_key")
        mock_public_key: str = "this-is-a-pod-public-key"
        hub = create_autospec(BitfountHub, instance=True)
        hub.get_pod_key.return_value = mock_public_key

        # Mock out the _check_known_pods() function
        mock_check_known_pods = mocker.patch(
            "bitfount.hub.helper._check_known_pods", autospec=True
        )

        # Mock out the _save_keys_to_key_store() function
        mock_save_keys_to_key_store = mocker.patch(
            "bitfount.hub.helper._save_key_to_key_store", autospec=True
        )

        mock_mkdir = mocker.patch("bitfount.hub.helper.Path.mkdir")
        # BITFOUNTHUB KEY
        # Correct return value
        public_key = _get_pod_public_key("blah/worker_1", hub)
        mock_load_public_key.assert_called_once_with(mock_public_key.encode())
        mock_save_keys_to_key_store.assert_called_once()
        mock_mkdir.assert_called_once()
        assert public_key == mock_load_public_key()

        # KEY FROM FILE
        # Key already exists in file, returns it
        mock_load_public_key.reset_mock()
        # Mock out the scenario of _check_known_pods() returning the existing key
        mock_check_known_pods.side_effect = lambda _pod_id, key, mock_key_store: key
        public_key = _get_pod_public_key(
            "blah/worker_2", hub, {"blah/worker_2": public_key_path}
        )
        mock_load_public_key.assert_called_once_with(public_key_path)
        mock_check_known_pods.assert_called_once_with(
            "blah/worker_2", mock_load_public_key(), mock_key_store
        )
        assert public_key == mock_load_public_key()
        # mkdir shouldnt be called on second call to _get_pod_public_key
        mock_mkdir.assert_called_once()

        # Key files exist, but not for specific user, retrieves from hub
        with caplog.at_level(logging.DEBUG):
            hub.get_pod_key.return_value = mock_public_key
            mock_load_public_key.reset_mock()
            public_key = _get_pod_public_key(
                "blah/worker_3", hub, {"blah/worker_2": public_key_path}
            )
            mock_load_public_key.assert_called_once_with(mock_public_key.encode())
            assert public_key == mock_load_public_key()
            assert "No existing public key file for blah/worker_3" in caplog.text
            # mkdir shouldnt be called on third call to _get_pod_public_key
            mock_mkdir.assert_called_once()

    def test__check_known_pods(
        self, mock_input: MagicMock, mock_key_store: Path
    ) -> None:
        """Tests _check_known_pods helper function.

        Checks that various states (no key exists, key already exists, wrong
        input detected) all get the correct key and that the key store is updated
        each time.
        """

        def _gen_new_public_key() -> RSAPublicKey:
            """Creates a new RSA public key."""
            return _RSAEncryption.generate_key_pair()[1]

        def _key_to_str(key: RSAPublicKey) -> str:
            """Converts RSA public key to string."""
            return _RSAEncryption.serialize_public_key(key).decode()

        orig_key: RSAPublicKey = _gen_new_public_key()
        known_workers: Dict[str, str]
        worker_name = "test-worker"
        mock_key_store.parent.mkdir(parents=True, exist_ok=True)
        mock_key_store.touch()

        # No key in yaml, should not require `input()` call
        new_key: RSAPublicKey = _check_known_pods(worker_name, orig_key, mock_key_store)
        mock_input.assert_not_called()
        assert new_key == orig_key
        with open(mock_key_store, "r") as known_workers_file:
            known_workers = yaml.safe_load(known_workers_file)
        assert known_workers[worker_name] == _key_to_str(orig_key)

        # Accept new key, input should be "Y"
        mock_input.reset_mock(return_value=True, side_effect=True)
        mock_input.return_value = "Y"
        diff_key: RSAPublicKey = _gen_new_public_key()
        new_key = _check_known_pods(worker_name, diff_key, mock_key_store)
        mock_input.assert_called_once()
        assert new_key == diff_key
        with open(mock_key_store, "r") as known_workers_file:
            known_workers = yaml.safe_load(known_workers_file)
        assert known_workers[worker_name] == _key_to_str(diff_key)

        # Wrong input (not "Y" or "N") then reject ("N") new key
        mock_input.reset_mock(return_value=True, side_effect=True)
        mock_input.side_effect = ["INCORRECT_INPUT", "N"]
        key_to_reject: RSAPublicKey = _gen_new_public_key()
        new_key = _check_known_pods(worker_name, key_to_reject, mock_key_store)
        assert mock_input.call_count == 2
        assert new_key != key_to_reject
        # have to do str compare here as direct key compare relies on python id(),
        # but we've actually reloaded the key from file.
        assert _key_to_str(new_key) == _key_to_str(diff_key)  # i.e. hasn't changed
        with open(mock_key_store, "r") as known_workers_file:
            known_workers = yaml.safe_load(known_workers_file)
        assert known_workers[worker_name] != _key_to_str(key_to_reject)
        assert (
            known_workers[worker_name] == _key_to_str(new_key) == _key_to_str(diff_key)
        )  # i.e. hasn't changed

        # Return to original key, input should be "Y"
        mock_input.reset_mock(return_value=True, side_effect=True)
        mock_input.return_value = "Y"
        new_key = _check_known_pods(worker_name, orig_key, mock_key_store)
        mock_input.assert_called_once()
        assert new_key == orig_key
        with open(mock_key_store, "r") as known_workers_file:
            known_workers = yaml.safe_load(known_workers_file)
        assert known_workers[worker_name] == _key_to_str(orig_key)

    def test_default_bitfounthub(self, mocker: MockerFixture) -> None:
        """Tests default bitfounthub calls create only if not None."""
        mock = Mock()
        mocker.patch("bitfount.hub.helper._create_bitfounthub", mock)
        _default_bitfounthub(hub=Mock())
        mock.assert_not_called()
        _default_bitfounthub()
        mock.assert_called_once()

    def test_get_pod_schema(self, mocker: MockerFixture) -> None:
        """Test get_pod_schema downloads schema.

        Tests it with save file specified.
        """
        pod_identifier = "fake/pod"
        save_file_path = "save_file/path.txt"

        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_create_hub = mocker.patch(
            "bitfount.hub.helper._create_bitfounthub", return_value=mock_hub
        )

        # Mock out schema download
        mock_schema = create_autospec(BitfountSchema, instance=True)
        mock_hub.get_pod_schema.return_value = mock_schema

        schema = get_pod_schema(pod_identifier, save_file_path=save_file_path)

        # Check hub was created
        mock_create_hub.assert_called_once()

        # Check schema download called
        mock_hub.get_pod_schema.assert_called_once_with(pod_identifier)

        # Check file saved out
        mock_schema.dump.assert_called_once_with(Path(save_file_path))

        # Check return
        assert schema == mock_schema

    def test_get_pod_schema_with_name_only(self, mocker: MockerFixture) -> None:
        """Test get_pod_schema downloads schema.

        Tests it with save file specified.
        """
        username = "username"
        pod_name = "pod_name"

        # Mock out hub creation, set username
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.username = username
        mock_create_hub = mocker.patch(
            "bitfount.hub.helper._create_bitfounthub", return_value=mock_hub
        )

        # Mock out schema download
        mock_schema = create_autospec(BitfountSchema, instance=True)
        mock_hub.get_pod_schema.return_value = mock_schema

        # Call get_pod_schema with name only
        schema = get_pod_schema(pod_name)

        # Check hub was created
        mock_create_hub.assert_called_once()

        # Check schema download called with constructed pod_identifier
        mock_hub.get_pod_schema.assert_called_once_with(f"{username}/{pod_name}")

        # Check return
        assert schema == mock_schema

    def test_get_pod_schema_with_hub_and_username(
        self, caplog: LogCaptureFixture
    ) -> None:
        """Test get_pod_schema with hub and username provided."""
        username = "username"
        hub_username = "hub_username"

        # Mock out hub creation, set username
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.username = hub_username

        # Mock out schema download
        mock_schema = create_autospec(BitfountSchema, instance=True)
        mock_hub.get_pod_schema.return_value = mock_schema

        # Call get_pod_schema
        get_pod_schema("pod_name", hub=mock_hub, username=username)

        # Check that provided username is ignored
        assert "Ignoring username argument as hub was provided." in [
            i.message for i in caplog.records
        ]
        assert mock_hub.username != username

    def test__save_keys_to_key_store(
        self, mock_key_store: Path, mocker: MockerFixture
    ) -> None:
        """Tests saving keys to key store."""
        pod_identifier = "fake/pod"
        orig_key: RSAPublicKey = _RSAEncryption.generate_key_pair()[1]
        serialized_key = _RSAEncryption.serialize_public_key(orig_key).decode()
        mock_open = mocker.mock_open(read_data="")
        mocker.patch("builtins.open", mock_open)

        _save_key_to_key_store(mock_key_store, pod_identifier, serialized_key)

        assert mock_open.call_count == 2
        mock_open.assert_any_call(mock_key_store, "r")
        mock_open.assert_any_call(mock_key_store, "w")

    def test__error_thrown_no_pod_key(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Tests _get_pod_public_key helper function."""
        # Mock out the hub and RSA key loading components
        hub = create_autospec(BitfountHub, instance=True)
        hub.get_pod_key.return_value = None
        pod_id = "pod_id"
        err_msg = f"No public key found for pod: {pod_id}"

        # Mock out the _save_keys_to_key_store() function
        mock_save_keys_to_key_store = mocker.patch(
            "bitfount.hub.helper._save_key_to_key_store", autospec=True
        )

        with pytest.raises(PodDoesNotExistError) as error:
            _get_pod_public_key(pod_id, hub)
            assert str(error.value) == err_msg

        assert mock_save_keys_to_key_store.call_count == 0
