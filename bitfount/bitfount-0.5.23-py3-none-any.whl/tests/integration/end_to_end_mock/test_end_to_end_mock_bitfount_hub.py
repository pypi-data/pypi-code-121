"""Test end-to-end but mock out Bitfount Hub API (as well as message service)."""
import asyncio
import copy
import logging
import multiprocessing
from multiprocessing import current_process
from multiprocessing.managers import SyncManager
import os
from pathlib import Path
from queue import Queue
import time
from typing import Any, Callable, Dict, Generator, Iterable, Union, cast
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from flask import Flask, url_for
import pytest
from pytest import fixture
from pytest_flask.live_server import LiveServer
from pytest_mock import MockerFixture
from pytorch_lightning.loggers import TensorBoardLogger

from bitfount.federated.exceptions import PodRegistrationError
from bitfount.federated.modeller import _Modeller
from bitfount.federated.transport.base_transport import _run_func_and_listen_to_mailbox
from bitfount.federated.transport.message_service import _LargeObjectRequestHandler
from bitfount.hub.authentication_flow import BitfountSession
from bitfount.runners.config_schemas import ModellerConfig, PodConfig
from bitfount.runners.modeller_runner import setup_modeller_from_config
from bitfount.runners.pod_runner import setup_pod_from_config
from bitfount.types import (
    _JSONDict,
    _S3PresignedPOSTFields,
    _S3PresignedPOSTURL,
    _S3PresignedURL,
)
from tests.integration import CONFIG_DIR
from tests.integration.utils import (
    get_caplog_records,
    load_modeller_config,
    load_pod_config,
    pod_start,
    run_modeller_process,
)
from tests.utils.helper import backend_test, end_to_end_mocks_test
from tests.utils.mocks import GRPCStubMock

STD_TIMEOUT: int = 3 * 60  # 3 minutes
EXT_TIMEOUT: int = 8 * 60  # 8 minutes

PROCESS_TIMEOUT: int = 6 * 60  # 6 minutes


logger = logging.getLogger(__name__)


class MockBitfountSession(BitfountSession):
    """A mock implementation of BitfountSession which avoids authentication."""

    def __init__(self, access_token: str, username: str, **kwargs: Any):
        self._faked_access_token = access_token
        self._username = username
        super().__init__(**kwargs)

    @property
    def access_token(self) -> str:
        """The supplied access token to provide to the message service."""
        return self._faked_access_token

    def authenticate(self) -> None:
        """Same as BitfountSession but doesn't authenticate anything."""
        pass

    @property
    def username(self) -> str:
        """Returns the username the authenticated user would have."""
        return self._username


@end_to_end_mocks_test
class TestEndToEnd:
    """Tests end-to-end functionality using mocks."""

    @fixture(autouse=True)
    def mock_am(
        self, monkeypatch: MonkeyPatch, access_manager_public_key: RSAPublicKey
    ) -> None:
        """Mock get_access_manager_key."""
        import bitfount.hub.api as api_

        monkeypatch.setattr(
            api_.BitfountAM,
            "get_access_manager_key",
            lambda x: access_manager_public_key,
        )

    @fixture(autouse=True)
    def mock_logger_save_dir(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        """Mock pytorch logger."""
        from bitfount.backends.pytorch.models.base_models import BasePyTorchModel

        monkeypatch.setattr(
            BasePyTorchModel,
            "_get_logger_from_config",
            lambda *args, **kwargs: TensorBoardLogger(
                str(tmp_path),
                name="mock_e2e_tests_model_name",
            ),
        )

    @fixture
    def pod_config(self, adult_data: Path) -> PodConfig:
        """Pod config to use for tests."""
        pod_config = load_pod_config(CONFIG_DIR / "pod_1.yaml", adult_data)
        pod_config.other_pods = [f"{pod_config.pod_id}2"]
        pod_config.hub.url = url_for("index", _external=True)
        return pod_config

    @fixture
    def modeller_config(
        self, modeller_private_key: RSAPrivateKey
    ) -> Generator[ModellerConfig, None, None]:
        """Modeller config to use for tests."""
        try:
            modeller_config = load_modeller_config(
                CONFIG_DIR / "modeller.yaml",
                private_key=modeller_private_key,
            )
            modeller_config.message_service.url = "http://hub.bitfount.notarealms.com"
            modeller_config.pods.identifiers = ["e2e_provider_1/pod"]
            modeller_config.hub.url = url_for("index", _external=True)

            yield modeller_config
        finally:
            try:
                # The unbound variable issue is handled by the NameError catching below.
                # noinspection PyUnboundLocalVariable
                private_key_file: Path = cast(
                    Path, modeller_config.modeller.private_key_file
                )
                os.remove(private_key_file)
            except FileNotFoundError:
                pass
            except NameError:
                # Means the modeller_config variable didn't even get created;
                # another exception has occurred that has booted us out of the
                # `try` block before it even got to there. We pass on NameError
                # to avoid masking whatever that underlying exception was.
                pass

    @fixture
    def bitfount_session_factory(
        self, tmp_path: Path
    ) -> Callable[[str, str], MockBitfountSession]:
        """Mock bitfount session factory."""

        def _create_mock_bitfount_session(
            username: str, access_token: str
        ) -> MockBitfountSession:
            return MockBitfountSession(
                access_token=access_token, username=username, user_storage_path=tmp_path
            )

        return _create_mock_bitfount_session

    @fixture
    def apply_mock_large_object_interactions(
        self, mocker: MockerFixture
    ) -> Callable[[SyncManager], None]:
        """Returns a function to apply a mock to LargeObjectRequestHandler.

        A function is needed due to the involved Manager.dict() call; the manager
        must be provided at runtime.
        """

        def _mock_large_object_interactions(manager: SyncManager) -> None:
            """Mock out LargeObjectRequestHandler methods.

            Mocks out LargeObjectRequestHandler.upload_large_object() and
            LargeObjectRequestHandler.get_large_object_from_url() to use local storage.
            """
            # Mock out message service functions
            large_object_storage: Dict[
                Union[_S3PresignedURL, _S3PresignedPOSTURL], bytes
            ] = manager.dict()

            # upload_fields is unused below
            # noinspection PyUnusedLocal
            def store_large_object(
                upload_url: _S3PresignedPOSTURL,
                upload_fields: _S3PresignedPOSTFields,
                large_object: bytes,
            ) -> None:
                """Mocks uploading to the URL.

                Args:
                    upload_url: URL to "upload" to.
                    upload_fields: Unused. Fields to upload with.
                    large_object: Object to store.
                """
                large_object_storage[upload_url] = large_object

            def get_large_object(url: _S3PresignedURL) -> bytes:
                """Mock downloading the object from the download URL.

                Args:
                    url: The download URL provided.

                Returns: The retrieved object/message
                """
                # This is just to simulate the fact that
                # the uploader and the downloader have used different URLs,
                # so we have to tweak one of them to find the object
                fixed_url: _S3PresignedPOSTURL = cast(
                    _S3PresignedPOSTURL, url.replace("download", "upload")
                )
                retrieved_object = large_object_storage[fixed_url]
                return retrieved_object

            mocker.patch.object(
                _LargeObjectRequestHandler,
                "upload_large_object",
                new=store_large_object,
            )
            mocker.patch.object(
                _LargeObjectRequestHandler,
                "get_large_object_from_url",
                new=get_large_object,
            )

        return _mock_large_object_interactions

    @staticmethod
    def _modeller_send_task_requests(
        modeller: _Modeller,
        pod_identifiers: Iterable[str],
    ) -> None:
        """Helper for sending Modeller task requests in a separate process.

        Fails tests if there are any errors.
        """
        # As this is used in multiprocessing, _modeller_send_task_requests() has
        # to be a def function. So we wrap the desired methods in an async def
        # and use asyncio.run() to simulate async def.
        async def _run_modeller() -> None:
            """Asyncronous modeller runner to process and run task requests."""
            modeller_mailbox = await modeller._send_task_requests(pod_identifiers)
            await _run_func_and_listen_to_mailbox(
                modeller_mailbox.process_task_request_responses(), modeller_mailbox
            )

        try:
            asyncio.run(_run_modeller())
        except Exception as e:
            print(f"Caught exception in {current_process().name} process: {e}")
            raise e

    @pytest.mark.parametrize("app", [(True, False, False)], indirect=True)
    @pytest.mark.timeout(STD_TIMEOUT)
    def test_pod_setup_raises_pod_registration_error(
        self,
        app: Flask,
        bitfount_session_factory: Callable[[str, str], MockBitfountSession],
        live_server: LiveServer,
        mock_bitfount_session: Mock,
        pod_config: PodConfig,
    ) -> None:
        """Tests handling when pod raises registration error."""
        username = pod_config.username
        # Override default return_value with bitfount_session_factory() one
        mock_bitfount_session.return_value = bitfount_session_factory(username, "pod")

        with pytest.raises(PodRegistrationError):
            setup_pod_from_config(pod_config)

    @pytest.mark.timeout(STD_TIMEOUT)
    def test_pod_starts_successfully(
        self,
        bitfount_session_factory: Callable[[str, str], MockBitfountSession],
        caplog_queue: Queue,
        live_server: LiveServer,  # automatically finds app fixture
        mock_bitfount_session: Mock,
        mock_grpc_insecure_channel: Mock,
        mock_message_service_stub: Mock,
        mock_s3_data_upload_in_api_module: Mock,
        pod_config: PodConfig,
    ) -> None:
        """Starts Pod listening in a subprocess.

        Sends SIGINT to the Pod after 10s to stop listening
        (Otherwise this test will hang indefinitely)
        """
        with multiprocessing.Manager() as manager:
            pod_token = "pod"
            username = pod_config.username
            mock_message_service_stub.return_value = GRPCStubMock(
                {pod_token: pod_config.pod_id}, manager
            )
            # Override default return_value with bitfount_session_factory() one
            mock_bitfount_session.return_value = bitfount_session_factory(
                username, pod_token
            )
            pod = setup_pod_from_config(pod_config)

            p = multiprocessing.Process(
                target=pod_start, name="Pod_Runner", args=(pod,)
            )
            p.start()
            time.sleep(10)
            p.terminate()
            p.join()

            caplog_records = get_caplog_records(caplog_queue)

            assert "INFO" in caplog_records
            assert "ERROR" not in caplog_records
            assert "CRITICAL" not in caplog_records

            assert p.exitcode is not None and p.exitcode <= 0

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    @backend_test
    @pytest.mark.parametrize("app", [(False, True, False)], indirect=True)
    @pytest.mark.timeout(STD_TIMEOUT)
    async def test_modeller_send_task_request_rejected_by_pod(
        self,
        app: Flask,
        bitfount_session_factory: Callable[[str, str], MockBitfountSession],
        caplog_queue: Queue,
        live_server: LiveServer,
        mock_bitfount_session: Mock,
        mock_grpc_insecure_channel: Mock,
        mock_message_service_stub: Mock,
        mock_s3_data_upload_in_api_module: Mock,
        mocker: MockerFixture,
        modeller_config: ModellerConfig,
        pod_config: PodConfig,
    ) -> None:
        """Tests Modeller handling if task requests are rejected by pods."""
        try:
            with multiprocessing.Manager() as manager:
                modeller_token = "modeller_token"
                pod_token = "pod_token"

                # Mock out GRPC interactions
                mock_stub = GRPCStubMock(
                    {
                        modeller_token: modeller_config.modeller.username,
                        pod_token: pod_config.pod_id,
                    },
                    manager,
                )
                mock_message_service_stub.return_value = mock_stub

                # Ensure only testing against one pod
                modeller_config.pods.identifiers = [pod_config.pod_id]

                # Mock out the sessions used for authentication
                pod_username = pod_config.username
                modeller_username = modeller_config.modeller.username
                # Override default return_value with side_effect
                # bitfount_session_factory() one. side_effect takes precedence
                # over return_value.
                mock_bitfount_session.side_effect = [
                    bitfount_session_factory(pod_username, pod_token),
                    bitfount_session_factory(modeller_username, modeller_token),
                ]
                # Setup pod and modeller
                pod = setup_pod_from_config(pod_config)
                mocker.patch(
                    "bitfount.runners.modeller_runner.get_pod_schema",
                    return_value=pod.schema,
                )

                modeller, pod_identifiers = setup_modeller_from_config(modeller_config)
                print(f"{modeller._identity_verification_method}")

                # Start pod, give time to spin up
                pod_process = multiprocessing.Process(
                    target=pod_start, name="Pod_Runner", args=(pod,)
                )
                pod_process.start()
                time.sleep(2)

                # Start modeller
                mocker.patch("bitfount.hub.helper._save_key_to_key_store")
                modeller_process = multiprocessing.Process(
                    target=self._modeller_send_task_requests,
                    name="Modeller_Runner",
                    args=(modeller, pod_identifiers),
                )
                modeller_process.start()

                # Give time for processing to happen then stop processes
                time.sleep(20)
                for proc in [pod_process, modeller_process]:
                    proc.terminate()
                    proc.join()

                # Check conditions in log messages match rejection of task
                caplog_records = get_caplog_records(caplog_queue)
                assert "INFO" in caplog_records
                assert (
                    "Task request from e2e_modeller rejected. "
                    "Protocol not approved" in caplog_records["INFO"]
                )
                assert "ERROR" in caplog_records
                assert (
                    f"Received rejection from {pod_config.pod_id}. "
                    f"Protocol not approved" in caplog_records["ERROR"]
                )
                assert "CRITICAL" not in caplog_records

                # Check that things shutdown correctly
                assert (
                    modeller_process.exitcode is not None
                    and modeller_process.exitcode <= 0
                )
                assert pod_process.exitcode is not None and pod_process.exitcode <= 0
        finally:
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                modeller_process.terminate()
            except Exception:
                pass

            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                pod_process.terminate()
            except Exception:
                pass

    @fixture
    def mock_schema_upload_download(self, mocker: MockerFixture) -> None:
        """Mocks out schema upload and download in the api module."""
        schema_store: Dict[str, _JSONDict] = {}

        def _upload(
            upload_url: _S3PresignedPOSTURL,
            presigned_fields: _S3PresignedPOSTFields,
            data: _JSONDict,
        ) -> None:
            pod_name = upload_url.split("/")[-1]
            # Error out if upload already used
            if pod_name in schema_store:
                raise ValueError("Cannot reuse schema upload URL")
            schema_store[pod_name] = data
            logger.info(f"Schema uploaded for {pod_name}")

        def _download(download_url: _S3PresignedURL) -> _JSONDict:
            pod_name = download_url.split("/")[-1]
            logger.info(f"Schema downloaded for {pod_name}")
            return schema_store[pod_name]

        mocker.patch(
            "bitfount.hub.api._upload_data_to_s3", autospec=True, side_effect=_upload
        )
        mocker.patch(
            "bitfount.hub.api._download_data_from_s3",
            autospec=True,
            side_effect=_download,
        )

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    @backend_test
    @pytest.mark.timeout(EXT_TIMEOUT)
    @pytest.mark.parametrize("use_local_storage", [True, False])
    async def test_full_training_end_to_end_successfully(
        self,
        apply_mock_large_object_interactions: Callable[[SyncManager], None],
        bitfount_session_factory: Callable[[str, str], MockBitfountSession],
        caplog_queue: Queue,
        live_server: LiveServer,  # automatically finds app fixture
        mock_bitfount_session: Mock,
        mock_grpc_insecure_channel: Mock,
        mock_message_service_stub: Mock,
        mock_schema_upload_download: None,
        mocker: MockerFixture,
        modeller_config: ModellerConfig,
        pod_config: PodConfig,
        tmp_path: Path,
        use_local_storage: bool,
    ) -> None:
        """Tests that training works end to end.

        Parameterised to run by sending messages directly, and then sending messages
        as file paths.
        """
        try:
            with multiprocessing.Manager() as manager:
                pod1_config = pod_config

                # Determine if we are using file paths for messages and set it up
                if use_local_storage:
                    pod1_config.message_service.use_local_storage = True
                    modeller_config.message_service.use_local_storage = True

                # Create second pod config from first
                second_pod_owner = "e2e_provider_2"
                pod2_config = copy.deepcopy(pod1_config)
                pod2_config.pod_name += "2"
                pod2_config.username = second_pod_owner

                # Patch out GRPC interactions
                pod1_token = "pod1"
                modeller_token = "modeller_token"
                pod2_token = "pod2"
                mock_stub = GRPCStubMock(
                    {
                        modeller_token: modeller_config.modeller.username,
                        pod1_token: pod1_config.pod_id,
                        pod2_token: pod2_config.pod_id,
                    },
                    manager,
                    get_message_timeout=5,
                )
                mock_message_service_stub.return_value = mock_stub

                # Mock out large object handling in message service
                apply_mock_large_object_interactions(manager)

                # Tie pod configs together
                pod1_config.other_pods = [pod2_config.pod_id]
                pod2_config.other_pods = [pod1_config.pod_id]
                modeller_config.pods.identifiers = [
                    pod1_config.pod_id,
                    pod2_config.pod_id,
                ]

                # Generate mocked sessions for modeller and pods
                modeller_username = modeller_config.modeller.username
                pod1_username = pod1_config.username
                pod2_username = second_pod_owner
                # Override default return_value with side_effect
                # bitfount_session_factory() one. side_effect takes precedence
                # over return_value.
                mock_bitfount_session.side_effect = [
                    # NOTE: Order is important; this is the order they will be
                    # setup in below.
                    bitfount_session_factory(pod1_username, pod1_token),
                    bitfount_session_factory(pod2_username, pod2_token),
                    bitfount_session_factory(modeller_username, modeller_token),
                ]

                # Setup pods and modeller (Note: order is important)
                pod1 = setup_pod_from_config(pod1_config)
                pod2 = setup_pod_from_config(pod2_config)

                modeller, pod_identifiers = setup_modeller_from_config(modeller_config)
                model_out = tmp_path / "model.out"

                # Start pods and wait to spin up
                pod_1_process = multiprocessing.Process(
                    target=pod_start, name="Pod_1_Runner", args=(pod1,)
                )
                pod_1_process.start()
                time.sleep(0.5)
                pod_2_process = multiprocessing.Process(
                    target=pod_start, name="Pod_2_Runner", args=(pod2,)
                )
                pod_2_process.start()
                time.sleep(0.5)

                # Start modeller
                mocker.patch("bitfount.hub.helper._save_key_to_key_store")
                modeller_process = multiprocessing.Process(
                    target=run_modeller_process,
                    name="MM_1",
                    args=(
                        modeller,
                        pod_identifiers,
                        model_out,
                    ),
                )
                modeller_process.start()

                # TODO: [BIT-350] instead of relying on a timeout - replace this
                #       with a call that waits for the process to finish before
                #       terminating. multiprocessing join() method currently hangs
                #       when using tox (but not pytest individually).
                # Wait for at most PROCESS_TIMEOUT seconds, checking every 30 seconds.
                for i in range(int(PROCESS_TIMEOUT / 30)):
                    time.sleep(30)
                    logger.info(f"{(i+1)*30} seconds...")
                    # the modeller is the only one that will terminate freely
                    # so check that.
                    if not modeller_process.is_alive():
                        break

                # End all processes, regardless of state
                for proc in [modeller_process, pod_1_process, pod_2_process]:
                    proc.terminate()
                    proc.join()

                caplog_records = get_caplog_records(caplog_queue)
                assert "INFO" in caplog_records
                assert "CRITICAL" not in caplog_records
                assert "ERROR" not in caplog_records

                info_logs = " ".join(caplog_records["INFO"])
                assert "Task complete" in info_logs
                assert "Validation Metrics" in info_logs

                assert (
                    modeller_process.exitcode is not None
                    and modeller_process.exitcode <= 0
                )
                assert (
                    pod_1_process.exitcode is not None and pod_1_process.exitcode <= 0
                )
                assert (
                    pod_2_process.exitcode is not None and pod_2_process.exitcode <= 0
                )
        finally:
            # Stop all processes
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                modeller_process.terminate()
            except Exception:
                pass
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                pod_1_process.terminate()
            except Exception:
                pass
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                pod_2_process.terminate()
            except Exception:
                pass
