"""Tests for worker and pod classes."""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
from unittest.mock import AsyncMock, MagicMock, Mock, NonCallableMock, create_autospec

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import pandas as pd
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
from requests import HTTPError, RequestException

import bitfount
from bitfount.data.datasources.csv_source import CSVSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.schema import BitfountSchema
from bitfount.data.utils import DatabaseConnection, _generate_dtypes_hash
from bitfount.federated.authorisation_checkers import IdentityVerificationMethod
from bitfount.federated.exceptions import PodNameError
from bitfount.federated.pod import Pod, PodRegistrationError
from bitfount.federated.pod_keys_setup import PodKeys
from bitfount.federated.pod_response_message import _PodResponseMessage
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.task_requests import (
    _EncryptedTaskRequest,
    _SignedEncryptedTaskRequest,
    _TaskRequest,
    _TaskRequestMessage,
)
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _MessageService,
)
from bitfount.federated.transport.pod_transport import _PodMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.federated.types import (
    SerializedAggregator,
    SerializedAlgorithm,
    SerializedModel,
    SerializedProtocol,
    _PodResponseType,
)
from bitfount.hub.api import BitfountAM, BitfountHub
from bitfount.hub.authentication_flow import BitfountSession, _AuthEnv
from bitfount.runners.config_schemas import (
    MessageServiceConfig,
    PodDataConfig,
    PodDetailsConfig,
)
from bitfount.transformations.processor import TransformationProcessor
from tests.utils.helper import (
    create_dataset,
    create_datasource,
    get_arg_from_args_or_kwargs,
    get_debug_logs,
    get_warning_logs,
    unit_test,
)
from tests.utils.mocks import DataclassMock, create_dataclass_mock


@fixture
def logging_mock(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock replacement for `logging`."""
    my_mock = MagicMock()
    monkeypatch.setattr(bitfount.federated.pod, "logger", my_mock)
    return my_mock


@unit_test
class TestPod:
    """Tests for Pod class."""

    # TODO: [BIT-983] Add tests that include aggregation

    @fixture
    def pod_name(self) -> str:
        """Pod name."""
        return "some-pod-name"

    @fixture
    def mock_datasource(self) -> DataFrameSource:
        """Mock of a pandas dataframe."""
        mock_dataframe: Mock = create_autospec(pd.DataFrame, instance=True)

        # Setup details for hash generation
        mock_dataframe.dtypes.to_string.return_value = "COLUMN INFO FOR MOCK DATAFRAME"

        mock_datasource = DataFrameSource(mock_dataframe)

        return mock_datasource

    @fixture
    def username(self) -> str:
        """Name of user hosting pod."""
        return "test_username"

    @fixture
    def pod_mailbox_id(self, pod_name: str) -> str:
        """The pod's mailbox ID."""
        # TODO: [BIT-960] Currently this is just hardcoded to return the pod_name
        #       (which is what the mailbox ID will actually be). [BIT-960] will have
        #       the PodConnect method actually return the generated mailbox ID so
        #       that if the approach changes in future it only needs to change on
        #       the message service side. At that point this should return the
        #       generated mailbox ID instead.
        return pod_name

    @fixture
    def pod_identifier(self, pod_mailbox_id: str, username: str) -> str:
        """Pod identifier for the pod."""
        return f"{username}/{pod_mailbox_id}"

    @fixture
    def mock_pod_data_config(self) -> DataclassMock:
        """A dataclass mock of PodDataConfig."""
        mock_pod_data_config = create_dataclass_mock(PodDataConfig)
        # So the following can be used in dict unpacking
        mock_pod_data_config.data_split.args = dict()
        mock_pod_data_config.datasource_args = dict()
        mock_pod_data_config.ignore_cols = None
        return mock_pod_data_config

    @fixture
    def mock_pod_details_config(self) -> DataclassMock:
        """A dataclass mock of PodDetailsConfig."""
        return create_dataclass_mock(PodDetailsConfig)

    @fixture
    def mock_bitfount_hub(self, username: str) -> Mock:
        """A mock of BitfountHub."""
        mock_hub: Mock = create_autospec(BitfountHub, instance=True)
        mock_hub.session = create_autospec(BitfountSession, instance=True)
        mock_hub.session.username = username
        return mock_hub

    @fixture
    def mock_access_manager(self) -> Mock:
        """A mock of BitfountAM."""
        mock_access_manager: Mock = create_autospec(BitfountAM, instance=True)
        return mock_access_manager

    @fixture
    def mock_message_service_config(self) -> DataclassMock:
        """A dataclass mock of MessageServiceConfig."""
        return create_dataclass_mock(MessageServiceConfig)

    @fixture
    def mock_access_manager_public_key(self) -> Mock:
        """A mock of the access managers public key."""
        mock_access_manager_public_key: Mock = create_autospec(
            RSAPublicKey, instance=True
        )
        return mock_access_manager_public_key

    @fixture
    def mock_pod_keys(self) -> DataclassMock:
        """A dataclass mock of PodKeys."""
        return create_dataclass_mock(PodKeys)

    @fixture
    def approved_pods(self) -> List[str]:
        """A list of pod identifiers for approved pods to work with."""
        return [
            "blah/worker_1",
            "blah/worker_2",
            "blah/worker_3",
            "blah/worker_4",
            "blah/worker_name",
        ]

    @fixture
    def mock_pod_mailbox(self) -> Mock:
        """Mock PodMailbox."""
        mailbox: Mock = create_autospec(_PodMailbox, instance=True)
        mailbox.message_service = create_autospec(_MessageService, instance=True)
        return mailbox

    @fixture
    def mock_pod_vitals(self) -> Mock:
        """Mock _PodVitals."""
        mock_pod_vitals = create_dataclass_mock(_PodVitals)
        return mock_pod_vitals

    @fixture
    def mock_pod_mailbox_create_helper(
        self, mock_pod_mailbox: Mock, mocker: MockerFixture
    ) -> Mock:
        """Mocks out create_and_connect_pod_mailbox."""
        mock_create_function = mocker.patch(
            "bitfount.federated.pod._create_and_connect_pod_mailbox", autospec=True
        )
        mock_create_function.return_value = mock_pod_mailbox
        return mock_create_function

    @fixture
    def pod(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> Pod:
        """Pod instance with mocked components."""
        pod_mock = Pod(
            name=pod_name,
            datasource=mock_datasource,
            username=username,
            data_config=mock_pod_data_config,
            pod_details_config=mock_pod_details_config,
            bitfounthub=mock_bitfount_hub,
            ms_config=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        # Pod.mailbox is usually set in Pod.start() but as that might not be being
        # called, we set it here manually.
        pod_mock._mailbox = mock_pod_mailbox
        pod_mock._pod_vitals = mock_pod_vitals

        return pod_mock

    @fixture
    def modeller_name(self) -> str:
        """Modeller name."""
        return "someModellerName"

    @fixture
    def modeller_mailbox_id(self) -> str:
        """Modeller Mailbox ID."""
        return "someModellerMailboxID"

    class _MakeBitfountMessageCallable(Protocol):
        """Callback protocol to describe make_bitfount_message fixture return."""

        def __call__(
            self,
            body: Any,
            other_pods_in_task: Optional[Dict[str, str]] = None,
        ) -> _BitfountMessage:
            ...

    @fixture
    def make_bitfount_message(
        self,
        modeller_mailbox_id: str,
        modeller_name: str,
        pod_identifier: str,
        pod_mailbox_id: str,
    ) -> _MakeBitfountMessageCallable:
        """Returns a function to generate a Bitfount message with fixtures in place."""

        def _make_bitfount_message(
            body: Any, other_pods_in_task: Optional[Dict[str, str]] = None
        ) -> _BitfountMessage:
            """Makes the BitfountMessage."""
            pod_mailbox_ids = {pod_identifier: pod_mailbox_id}

            if other_pods_in_task:
                pod_mailbox_ids.update(other_pods_in_task)

            return _BitfountMessage(
                message_type=_BitfountMessageType.JOB_REQUEST,
                body=body,
                recipient=pod_identifier,
                recipient_mailbox_id=pod_mailbox_id,
                sender=modeller_name,
                sender_mailbox_id=modeller_mailbox_id,
                pod_mailbox_ids=pod_mailbox_ids,
            )

        return _make_bitfount_message

    @fixture
    def aes_key(self) -> bytes:
        """An AES key."""
        return b"someAesKey"

    @pytest.mark.parametrize(
        "invalid_pod_name",
        ["Invalid", "INVALID", "invalid-", "-invalid", "invalid--invalid"],
    )
    def test_invalid_pod_name(
        self,
        approved_pods: List[str],
        invalid_pod_name: str,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        username: str,
    ) -> None:
        """Test PodNameError raised for invalid pod name."""
        with pytest.raises(PodNameError):
            Pod(
                name=invalid_pod_name,
                datasource=mock_datasource,
                username=username,
                data_config=mock_pod_data_config,
                pod_details_config=mock_pod_details_config,
                bitfounthub=mock_bitfount_hub,
                ms_config=mock_message_service_config,
                access_manager=mock_access_manager,
                pod_keys=mock_pod_keys,
                approved_pods=approved_pods,
            )

    async def test__check_for_unapproved_pods_without_secure_aggregation(
        self, pod: Pod, pod_identifier: str
    ) -> None:
        """Tests authorisation check passes not using secure aggregation."""
        training_request = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="some aggregator"),
        )
        pods_involved_in_task = [pod_identifier]

        assert (
            pod._check_for_unapproved_pods(pods_involved_in_task, training_request)
            is None
        )

    async def test__check_for_unapproved_pods_with_secure_aggregation_unapproved(
        self, pod: Pod, pod_identifier: str
    ) -> None:
        """Tests unapproved workers are returned when using secure aggregation."""
        training_request = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
        )
        unapproved_pods = ["some/unapproved-pod", "another/unapproved_pod"]
        pods_involved_in_task = [pod_identifier, *unapproved_pods]

        assert (
            pod._check_for_unapproved_pods(pods_involved_in_task, training_request)
            == unapproved_pods
        )

    @pytest.mark.asyncio
    async def test__check_for_unapproved_pods_with_secure_aggregation_approved(
        self, approved_pods: List[str], pod: Pod, pod_identifier: str
    ) -> None:
        """Tests all workers approved when using secure aggregation."""
        training_request = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
        )
        pods_involved_in_task = [pod_identifier, *approved_pods]

        assert (
            pod._check_for_unapproved_pods(pods_involved_in_task, training_request)
            is None
        )

    async def test__new_task_request_handler_rejects(
        self,
        aes_key: bytes,
        caplog: LogCaptureFixture,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_mailbox: Mock,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Tests new job callback fails when access request rejected."""
        caplog.set_level(logging.INFO)

        mock_worker_mailbox = mocker.patch(
            "bitfount.federated.pod._WorkerMailbox", autospec=True
        )

        # Mock out Pod._check_for_unapproved_pods() as that's not under test here.
        mock__check_for_unapproved_pods = mocker.patch.object(
            pod, "_check_for_unapproved_pods", autospec=True
        )
        # Testing rejection, so there are unapproved pods
        expected_unapproved_pods = ["some/unapproved-pod"]
        mock__check_for_unapproved_pods.return_value = expected_unapproved_pods

        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="some aggregator"),
        )
        task_request = _TaskRequest(task_protocol_details, ["pods"], aes_key)
        message = make_bitfount_message(
            _TaskRequestMessage(
                serialized_protocol=task_protocol_details,
                auth_type=IdentityVerificationMethod.SAML.value,
                request=_EncryptedTaskRequest(
                    # We don't actually encrypt this due to the mocked decryption
                    encrypted_request=task_request.serialize(),
                ).serialize(),
            ).serialize()
        )

        result = await pod._new_task_request_handler(message)

        # returns None if rejected
        assert result is None
        # We expect this log on rejection
        assert f"Task from '{modeller_name}' rejected." in caplog.text
        # Check accept_task() not called (happens in _new_task_request_handler)
        mock_worker_mailbox.accept_task.assert_not_called()

        mock_worker_mailbox.assert_called_once_with(
            pod_identifier=pod.pod_identifier,
            modeller_mailbox_id=message.sender_mailbox_id,
            modeller_name=message.sender,
            aes_encryption_key=aes_key,
            message_service=mock_pod_mailbox.message_service,
            pod_mailbox_ids=message.pod_mailbox_ids,
        )

        # Ensure reject task was called
        mock_worker_mailbox.return_value.reject_task.assert_called_once_with(
            {
                _PodResponseType.SECURE_AGGREGATION_WORKERS_NOT_AUTHORISED.name: [
                    *expected_unapproved_pods,
                ]
            }
        )

    async def test__new_task_request_handler_creates_worker(
        self,
        aes_key: bytes,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_mailbox: Mock,
        mocker: MockerFixture,
        modeller_mailbox_id: str,
        modeller_name: str,
        pod: Pod,
        pod_identifier: str,
        pod_mailbox_id: str,
    ) -> None:
        """Tests the simple wrapper.

        This is just ensuring that the creation of the worker
        has been called as expected.
        """
        # Mock out _create_and_run_worker as that's not under test here.
        mock__create_and_run_worker = mocker.patch.object(
            pod, "_create_and_run_worker", autospec=True
        )
        message = make_bitfount_message(Mock())

        await pod._new_task_request_handler(
            # body only used in _is_authorised so can mock out
            message
        )

        # Check that worker is created and run
        mock__create_and_run_worker.assert_called_once_with(message)

    async def test__create_and_run_worker_runs_worker(
        self,
        aes_key: bytes,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        pod: Pod,
    ) -> None:
        """Test that worker is created with SAML authorisation.

        Verification type is explicitly set to SAML.
        """
        mock_worker_mailbox = mocker.patch(
            "bitfount.federated.pod._WorkerMailbox", autospec=True
        )
        mock_worker = mocker.patch("bitfount.federated.pod._Worker", autospec=True)
        mock__create_authorisation_checker = mocker.patch.object(
            Pod, "_create_authorisation_checker", autospec=True
        )

        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="some aggregator"),
        )
        task_request = _TaskRequest(task_protocol_details, [], aes_key)
        encrypted_message = make_bitfount_message(
            _TaskRequestMessage(
                serialized_protocol=task_protocol_details,
                auth_type=IdentityVerificationMethod.SAML.value,
                request=_EncryptedTaskRequest(
                    # We don't actually encrypt this due to the mocked decryption
                    encrypted_request=task_request.serialize(),
                ).serialize(),
            ).serialize()
        )

        await pod._create_and_run_worker(encrypted_message)

        # Ensure worker mailbox created based on task
        mock_worker_mailbox.assert_called_once_with(
            pod_identifier=pod.pod_identifier,
            modeller_mailbox_id=encrypted_message.sender_mailbox_id,
            modeller_name=encrypted_message.sender,
            aes_encryption_key=aes_key,
            message_service=mock_pod_mailbox.message_service,
            pod_mailbox_ids=encrypted_message.pod_mailbox_ids,
        )
        # Ensure worker was created with the created SAML based authoriser
        mock_worker.assert_called_once_with(
            datasource=pod.datasource,
            mailbox=mock_worker_mailbox.return_value,
            bitfounthub=pod._hub,
            authorisation=mock__create_authorisation_checker.return_value,
            pod_dp=pod._pod_dp,
            pod_vitals=mock_pod_vitals,
            pod_identifier=pod.pod_identifier,
            serialized_protocol=task_protocol_details,
        )

    async def test__create_and_run_worker_with_secure_aggregation_unapproved_pods(
        self,
        aes_key: bytes,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_mailbox: Mock,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        pod: Pod,
    ) -> None:
        """Test that the Pod rejects a task if there are unapproved pods in the task.

        SAML identity verification is explicitly used.
        """
        mock_worker_mailbox = AsyncMock(spec=_WorkerMailbox)
        mocker.patch(
            "bitfount.federated.pod._WorkerMailbox", return_value=mock_worker_mailbox
        )

        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
        )
        task_request = _TaskRequest(task_protocol_details, [], aes_key)
        encrypted_message = make_bitfount_message(
            _TaskRequestMessage(
                serialized_protocol=task_protocol_details,
                auth_type=IdentityVerificationMethod.SAML.value,
                request=_EncryptedTaskRequest(
                    # We don't actually encrypt this due to the mocked decryption
                    encrypted_request=task_request.serialize(),
                ).serialize(),
            ).serialize(),
            {"unapproved_pod_name": "unapproved_mailbox_id"},
        )

        await pod._create_and_run_worker(encrypted_message)

        # Ensure worker mailbox has rejected the task
        mock_worker_mailbox.reject_task.assert_awaited_once_with(
            {
                "SECURE_AGGREGATION_WORKERS_NOT_AUTHORISED": [
                    "unapproved_pod_name",
                ]
            }
        )

    async def test__create_and_run_worker_with_secure_aggregation(
        self,
        aes_key: bytes,
        caplog: LogCaptureFixture,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        pod: Pod,
    ) -> None:
        """Test that expected mailbox is created for secure aggregator."""
        # Mock out constructors
        mock_interpod_worker_mailbox = mocker.patch(
            "bitfount.federated.pod._InterPodWorkerMailbox", autospec=True
        )
        mock_worker = mocker.patch("bitfount.federated.pod._Worker", autospec=True)

        # Mock out other methods
        mock__create_authorisation_checker = mocker.patch.object(
            Pod, "_create_authorisation_checker", autospec=True
        )

        # Mock out other pod public key retrieval
        mock__get_pod_public_keys = mocker.patch(
            "bitfount.federated.pod._get_pod_public_keys", autospec=True
        )

        # Create appropriate task request
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(
                class_name="some algorithm",
                model=SerializedModel(class_name="some model"),
            ),
            aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
        )
        task_request = _TaskRequest(task_protocol_details, [], aes_key)
        encrypted_message = make_bitfount_message(
            _TaskRequestMessage(
                serialized_protocol=task_protocol_details,
                auth_type=IdentityVerificationMethod.SAML.value,
                request=_EncryptedTaskRequest(
                    # We don't actually encrypt this due to the mocked decryption
                    encrypted_request=task_request.serialize(),
                ).serialize(),
            ).serialize()
        )

        # Call method under test
        with caplog.at_level(logging.DEBUG):
            await pod._create_and_run_worker(encrypted_message)

        # Ensure interpod worker mailbox created based on task
        mock_interpod_worker_mailbox.assert_called_once_with(
            pod_identifier=pod.pod_identifier,
            modeller_mailbox_id=encrypted_message.sender_mailbox_id,
            modeller_name=encrypted_message.sender,
            aes_encryption_key=aes_key,
            message_service=mock_pod_mailbox.message_service,
            pod_mailbox_ids=encrypted_message.pod_mailbox_ids,
            pod_public_keys=mock__get_pod_public_keys.return_value,
            private_key=mock_pod_keys.private,
        )

        # Ensure worker was created correctly
        mock_worker.assert_called_once_with(
            datasource=pod.datasource,
            mailbox=mock_interpod_worker_mailbox.return_value,
            bitfounthub=pod._hub,
            authorisation=mock__create_authorisation_checker.return_value,
            pod_dp=pod._pod_dp,
            pod_vitals=mock_pod_vitals,
            pod_identifier=pod.pod_identifier,
            serialized_protocol=task_protocol_details,
        )

        # Ensure interpod mailbox creation logged
        debug_logs = get_debug_logs(caplog)
        assert "Creating mailbox with inter-pod support." in debug_logs

    def test__create_authorisation_checker_creates_saml_checker(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test SAML Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.SAML.value,
            _EncryptedTaskRequest(
                # no need to actually encrypt
                task_request.serialize()
            ).serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)

        mock_saml_authorisation = mocker.patch(
            "bitfount.federated.pod._SAMLAuthorisation", autospec=True
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_saml_authorisation.return_value

        mock_saml_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            access_manager=pod._access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=task_protocol_details,
        )

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    def test__create_authorisation_checker_creates_signature_checker(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test Signature Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        packed_request = _SignedEncryptedTaskRequest(
            # no need to actually encrypt
            task_request.serialize(),
            signature=b"signature",
        )
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.KEYS.value,  # type: ignore[attr-defined] # Reason: Disabled until [BIT-1291] resolved # noqa: B950
            packed_request.serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)

        mock_signature_authorisation = mocker.patch(
            "bitfount.federated.pod._SignatureBasedAuthorisation", autospec=True
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_signature_authorisation.return_value

        mock_signature_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            encrypted_task_request=packed_request.encrypted_request,
            signature=packed_request.signature,
            serialized_protocol=task_protocol_details,
        )

    def test__create_authorisation_checker_creates_oidc_auth_code_checker(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test OIDC Authorization Code Flow Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        packed_request = _EncryptedTaskRequest(
            # no need to actually encrypt
            task_request.serialize(),
        )
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.OIDC_ACF_PKCE.value,
            packed_request.serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)

        # Mock authorisation checker class import
        mock_oidc_authorisation = mocker.patch(
            "bitfount.federated.pod._OIDCAuthorisationCode", autospec=True
        )

        # Mock _get_auth_environment() function
        mocker.patch(
            "bitfount.federated.pod._get_auth_environment",
            autospec=True,
            return_value=_AuthEnv(
                name="auth_env_name",
                auth_domain="auth_env_auth_domain",
                client_id="auth_env_client_id",
            ),
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_oidc_authorisation.return_value
        mock_oidc_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            access_manager=pod._access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=task_protocol_details,
            _auth_domain="auth_env_auth_domain",
            _client_id="auth_env_client_id",
        )

    def test__create_authorisation_checker_creates_oidc_device_code_checker(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test OIDC Device Code Flow Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        packed_request = _EncryptedTaskRequest(
            # no need to actually encrypt
            task_request.serialize(),
        )
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.OIDC_DEVICE_CODE.value,
            packed_request.serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)

        # Mock authorisation checker class import
        mock_oidc_device_code_authorisation = mocker.patch(
            "bitfount.federated.pod._OIDCDeviceCode", autospec=True
        )

        # Mock _get_auth_environment() function
        mocker.patch(
            "bitfount.federated.pod._get_auth_environment",
            autospec=True,
            return_value=_AuthEnv(
                name="auth_env_name",
                auth_domain="auth_env_auth_domain",
                client_id="auth_env_client_id",
            ),
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_oidc_device_code_authorisation.return_value
        mock_oidc_device_code_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            access_manager=pod._access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=task_protocol_details,
            _auth_domain="auth_env_auth_domain",
            _client_id="auth_env_client_id",
        )

    async def test__pod_heartbeat_handles_RequestException(
        self, caplog: LogCaptureFixture, mock_bitfount_hub: Mock, pod: Pod
    ) -> None:
        """Tests _pod_heartbeat handles RequestException from hub."""
        mock_bitfount_hub.do_pod_heartbeat.side_effect = RequestException
        await pod._pod_heartbeat()
        assert "Could not connect to hub for status:" in caplog.text

    async def test__pod_heartbeat_handles_HTTPError(
        self, caplog: LogCaptureFixture, mock_bitfount_hub: Mock, pod: Pod
    ) -> None:
        """Tests _pod_heartbeat handles HTTPError from hub."""
        mock_bitfount_hub.do_pod_heartbeat.side_effect = HTTPError
        await pod._pod_heartbeat()
        assert "Failed to reach hub for status:" in caplog.text

    def test__register_pod_handles_HTTPError(
        self, caplog: LogCaptureFixture, mock_bitfount_hub: Mock, pod: Pod
    ) -> None:
        """Tests _register_pod handles HTTPError from hub."""
        mock_bitfount_hub.register_pod.side_effect = HTTPError
        with pytest.raises(PodRegistrationError, match="Failed to register with hub"):
            pod._register_pod()
        assert "Failed to register with hub" in caplog.text

    def test__register_pod_handles_RequestException(
        self, caplog: LogCaptureFixture, mock_bitfount_hub: Mock, pod: Pod
    ) -> None:
        """Tests _register_pod handles RequestException from hub."""
        mock_bitfount_hub.register_pod.side_effect = RequestException
        with pytest.raises(PodRegistrationError, match="Could not connect to hub"):
            pod._register_pod()
        assert "Could not connect to hub" in caplog.text

    def test__get_default_pod_keys_with_keys(
        self, mock_pod_keys: DataclassMock, pod: Pod
    ) -> None:
        """Tests that the default pod keys are loaded correctly with keys."""
        # Check that the keys are simply extracted and returned
        private_key, public_key = pod._get_default_pod_keys(mock_pod_keys)
        assert private_key == mock_pod_keys.private
        assert public_key == mock_pod_keys.public

    def test__get_default_pod_keys_with_None(
        self, mocker: MockerFixture, pod: Pod
    ) -> None:
        """Tests that the default pod keys are loaded correctly with no keys."""
        # Mock out get_pod_keys() function
        mock_get_pod_keys = mocker.patch(
            "bitfount.federated.pod._get_pod_keys", autospec=True
        )
        mock_private_key = create_autospec(RSAPrivateKey, instance=True)
        mock_get_pod_keys.return_value.private = mock_private_key
        mock_public_key = create_autospec(RSAPublicKey, instance=True)
        mock_get_pod_keys.return_value.public = mock_public_key

        # Explicitly call this with None
        private_key, public_key = pod._get_default_pod_keys(None)

        assert private_key == mock_private_key
        assert public_key == mock_public_key

    def test_pod_init_no_am_key(
        self,
        approved_pods: List[str],
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that the default access manager key is loaded."""
        # Mock out get_access_manager_key() function.
        mock_bitfount_am_key = mocker.patch.object(
            bitfount.federated.pod.BitfountAM, "get_access_manager_key"
        )
        Pod(
            name=pod_name,
            datasource=mock_datasource,
            username=username,
            data_config=mock_pod_data_config,
            pod_details_config=mock_pod_details_config,
            bitfounthub=mock_bitfount_hub,
            ms_config=mock_message_service_config,
            access_manager=None,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        mock_bitfount_am_key.assert_called_once()

    def test_pod_no_approved_pods(
        self,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that the default approved workers ([]) are loaded correctly."""
        pod = Pod(
            name=pod_name,
            datasource=mock_datasource,
            username=username,
            data_config=mock_pod_data_config,
            pod_details_config=mock_pod_details_config,
            bitfounthub=mock_bitfount_hub,
            ms_config=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=None,
        )
        assert pod.approved_pods == []

    def test_pod_fails_no_csv_path(
        self, mock_pod_data_config: DataclassMock, pod: Pod
    ) -> None:
        """Tests that the pod does not load data with non-csv extension."""
        with pytest.raises(
            TypeError, match="Please provide a Path or URL to a CSV file."
        ):
            pod.datasource = CSVSource(Path("mock.pdf"))
            pod._setup_schema(data_config=mock_pod_data_config)

    def test_pod_auto_tidy_is_not_applied_with_multi_table_datasource(
        self,
        caplog: LogCaptureFixture,
        mock_engine: Mock,
        mock_pod_data_config: DataclassMock,
        pod: Pod,
    ) -> None:
        """Tests that the pod does not auto tidy multi-table datasource."""
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        pod.datasource = DatabaseSource(db_conn)
        mock_pod_data_config.auto_tidy = True
        mock_schema = Mock()
        pod._setup_schema(data_config=mock_pod_data_config, schema=mock_schema)
        mock_schema.add_datasource_tables.assert_called_once()
        assert "Can't autotidy multi-table data." in caplog.text

    def test_pod_fails_wrong_data(
        self, mock_pod_data_config: DataclassMock, pod: Pod
    ) -> None:
        """Tests that the pod does not load data in an unaccepted data format."""
        with pytest.raises(
            TypeError,
            match=(
                "Invalid data attribute. Expected pandas dataframe "
                "but received :<class 'unittest.mock.Mock'>"
            ),
        ):
            pod.datasource = DataFrameSource(Mock())
            pod._setup_schema(data_config=mock_pod_data_config)

    def test_read_sql_tabular(self, mocker: MockerFixture, pod: Pod) -> None:
        """Tests that the pod reads tabular sql data with one table."""
        # Mock out pandas interaction
        dataset = create_dataset()
        dtypes = dataset.convert_dtypes().dtypes.to_dict()
        mocker.patch.object(pd, "read_sql_query", return_value=dataset)
        mocker.patch.object(pd, "read_sql", return_value=dataset)
        db_conn = Mock(
            spec=DatabaseConnection,
            table_names=["table1"],
            multi_table=False,
            query=None,
            con=Mock(),
            db_schema="test",
        )
        datasource = DatabaseSource(db_conn=db_conn)
        datasource._table_hashes.add(_generate_dtypes_hash(dtypes))
        mocker.patch.object(datasource, "get_dtypes", return_value=dtypes)

        pod.datasource = datasource

        mock_pod_config = PodDataConfig(force_stypes={})
        schema = pod._setup_schema(data_config=mock_pod_config)

        assert schema is not None
        assert isinstance(schema, BitfountSchema)

    def test__setup_schema(
        self, mock_pod_data_config: DataclassMock, mocker: MockerFixture, pod: Pod
    ) -> None:
        """Tests that the pod schema works as expected."""
        # Mock out _BaseSource/BitfountSchema constructor as not under test here.
        mock_datasource: Mock = mocker.patch(
            "bitfount.federated.pod._BaseSource", autospec=True, multi_table=False
        )
        pod.datasource = mock_datasource
        mock_schema = Mock(spec=BitfountSchema)
        mocker.patch("bitfount.federated.pod.BitfountSchema", return_value=mock_schema)
        mock_pod_data_config.auto_tidy = False
        schema = pod._setup_schema(data_config=mock_pod_data_config)

        # Assert that bitfount schema is constructed with the datasource
        assert (
            get_arg_from_args_or_kwargs(
                mock_schema.add_datasource_tables.call_args,
                args_idx=0,
                kwarg_name="datasource",
            )
            == mock_datasource
        )
        assert isinstance(schema, BitfountSchema)

    def test__setup_schema_applies_transformation_to_floats_only(
        self, pod: Pod
    ) -> None:
        """Tests that pod auto-tidy applies normalization to float columns only."""
        datasource = create_datasource(classification=True)
        pod.datasource = datasource
        data_config = PodDataConfig(auto_tidy=True)
        pod._setup_schema(data_config=data_config)
        # Check float dtypes
        assert round(pod.datasource.data["E"].mean()) == 0
        assert round(pod.datasource.data["E"].std()) == 1
        assert round(pod.datasource.data["F"].mean()) == 0
        assert round(pod.datasource.data["F"].std()) == 1
        assert round(pod.datasource.data["G"].mean()) == 0
        assert round(pod.datasource.data["G"].std()) == 1
        assert round(pod.datasource.data["H"].mean()) == 0
        assert round(pod.datasource.data["H"].std()) == 1
        # Check int types are unchanged
        assert round(pod.datasource.data["A"].mean()) != 0
        assert round(pod.datasource.data["A"].std()) != 1
        assert round(pod.datasource.data["B"].mean()) != 0
        assert round(pod.datasource.data["B"].std()) != 1
        assert round(pod.datasource.data["C"].mean()) != 0
        assert round(pod.datasource.data["C"].std()) != 1
        assert round(pod.datasource.data["C"].mean()) != 0
        assert round(pod.datasource.data["C"].std()) != 1

    def test_default_pod_details_generation(self, pod: Pod) -> None:
        """Tests the default pod details generation."""
        assert pod._get_default_pod_details_config() == PodDetailsConfig(
            display_name=pod.name,
            description=pod.name,
        )

    async def test__initialise_creates_mailbox(
        self, mock_pod_mailbox: Mock, mock_pod_mailbox_create_helper: Mock, pod: Pod
    ) -> None:
        """Tests that _initialise() creates a mailbox for the pod."""
        # Set the mailbox on generated pod to None to mimic no initialization.
        pod._mailbox = None
        assert pod._mailbox is None
        assert not pod._initialised

        await pod._initialise()

        # Check mailbox is present and what we expect
        assert pod._mailbox is not None
        assert pod._mailbox == mock_pod_mailbox

        # Check marked as initialized
        assert pod._initialised

    async def test__initialise_warns_when_called_multiple(
        self,
        caplog: LogCaptureFixture,
        mock_pod_mailbox: Mock,
        mock_pod_mailbox_create_helper: Mock,
        pod: Pod,
    ) -> None:
        """Tests that _initialise() creates a mailbox for the pod."""
        # Set the mailbox on generated pod to None to mimic no initialization.
        pod._mailbox = None
        assert pod._mailbox is None
        assert not pod._initialised

        await pod._initialise()

        # Check mailbox is present and what we expect
        assert pod._mailbox is not None
        assert pod._mailbox == mock_pod_mailbox
        assert pod._initialised

        # Check no log yet
        assert (
            "Pod._initialise() called twice. This is not allowed."
            not in get_warning_logs(caplog)
        )

        # Call second time
        await pod._initialise()

        # Check unchanged
        assert pod._mailbox is not None
        assert pod._mailbox == mock_pod_mailbox
        assert pod._initialised

        # Check warning issued
        assert (
            "Pod._initialise() called twice. This is not allowed."
            in get_warning_logs(caplog)
        )

    def test_start_calls__initialise(
        self, mock_pod_mailbox: Mock, mocker: MockerFixture, pod: Pod
    ) -> None:
        """Tests that Pod._initialise() is inherently called in Pod.start()."""
        # Patch out _initialise() so we can assert it is called
        mock_initialise = mocker.patch.object(pod, "_initialise", autospec=True)

        # Patch mailbox so we can avoid the listen_for_messages() looping forever
        pod._mailbox = mock_pod_mailbox

        pod.start()

        # Check _initialise() was called
        mock_initialise.assert_called_once()

    def test_init_works_with_existing_schema_file(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_bitfount_schema: NonCallableMock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that Pod.__init__ works with existing schema files."""
        # Mock out actual schema loading
        mock_load_from_file = mocker.patch.object(
            BitfountSchema,
            "load_from_file",
            autospec=True,
            return_value=mock_bitfount_schema,
        )

        # Load pod with fake schema path
        schema_path = "not_a_real_path"
        pod = Pod(
            name=pod_name,
            datasource=mock_datasource,
            username=username,
            data_config=mock_pod_data_config,
            schema=schema_path,
            pod_details_config=mock_pod_details_config,
            bitfounthub=mock_bitfount_hub,
            ms_config=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        # Check correct calls made to schema loading
        mock_load_from_file.assert_called_once_with(schema_path)
        # This is where and how the schema is stored
        assert pod.public_metadata.schema == mock_bitfount_schema.to_json()

    def test__setup_data_works_with_existing_schema(
        self,
        mock_bitfount_schema: NonCallableMock,
        mock_pod_data_config: DataclassMock,
        mocker: MockerFixture,
        pod: Pod,
        pod_name: str,
    ) -> None:
        """Tests that Pod._setup_schema() works with an existing schema."""
        # Mock out datasource import and creation
        mock_datasource = mocker.patch(
            "bitfount.federated.pod._BaseSource",
            autospec=True,
            multi_table=False,
        )
        mock_pod_data_config.auto_tidy = False

        # Mock out transformation application
        mocker.patch.object(TransformationProcessor, "transform")
        pod.datasource = mock_datasource
        schema = pod._setup_schema(
            data_config=mock_pod_data_config,
            schema=mock_bitfount_schema,
        )

        # Check datasource added to schema
        mock_bitfount_schema.add_datasource_tables.assert_called_once_with(
            datasource=mock_datasource,
            table_name=pod_name,
            force_stypes=mock_pod_data_config.force_stypes,
        )
        # Check expected schema is returned
        assert schema == mock_bitfount_schema

    @pytest.mark.parametrize("use_existing_schema", [True, False])
    def test_schema_frozen_after_pod_init(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_bitfount_schema: NonCallableMock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        pod_name: str,
        use_existing_schema: bool,
        username: str,
    ) -> None:
        """Tests that Pod._setup_schema() freezes the schema."""
        schema_path = "not_a_real_path"

        # Mock out actual schema loading
        if use_existing_schema:
            # Mock out loading from file
            mocker.patch.object(
                BitfountSchema,
                "load_from_file",
                autospec=True,
                return_value=mock_bitfount_schema,
            )
        else:
            # Mock out init call
            mocker.patch(
                "bitfount.federated.pod.BitfountSchema",
                autospec=True,
                return_value=mock_bitfount_schema,
            )
        mock_pod_data_config.auto_tidy = False

        # Load pod
        Pod(
            name=pod_name,
            datasource=mock_datasource,
            username=username,
            data_config=mock_pod_data_config,
            schema=schema_path if use_existing_schema else None,
            pod_details_config=mock_pod_details_config,
            bitfounthub=mock_bitfount_hub,
            ms_config=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        # Check schema was frozen
        mock_bitfount_schema.freeze.assert_called_once()
        mock_bitfount_schema.unfreeze.assert_not_called()

    @pytest.mark.parametrize("is_notebook", [True, False])
    def test__run_pod_vitals_server(
        self, is_notebook: bool, mocker: MockerFixture, pod: Pod
    ) -> None:
        """Test whether pod vitals server is ran.

        The pod vitals webserver should not be ran when
        executed from a notebook.
        """
        mock_is_notebook = mocker.patch(
            "bitfount.federated.pod._is_notebook", return_value=is_notebook
        )
        mock_handler = mocker.patch("bitfount.federated.pod._PodVitalsHandler")
        pod._run_pod_vitals_server()
        mock_is_notebook.assert_called_once()
        if is_notebook:
            mock_handler.assert_not_called()
        else:
            mock_handler.assert_called_once()

    def test_pod_schema_table_takes_pod_name_as_table_name(
        self, pod: Pod, pod_name: str
    ) -> None:
        """Tests that the schema table name is the pod name."""
        assert pod.schema.table_names == [pod_name]
