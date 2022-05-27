"""Tests federated helper.py."""
import copy
from typing import Optional, cast
from unittest.mock import create_autospec

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
import pytest
from pytest import fixture
from pytest_lazyfixture import lazy_fixture
from pytest_mock import MockerFixture

from bitfount.data.schema import BitfountSchema, BitfountSchemaError
from bitfount.federated.aggregators.aggregator import Aggregator
from bitfount.federated.aggregators.secure import SecureAggregator
from bitfount.federated.exceptions import PodNameError
from bitfount.federated.helper import (
    _check_and_update_pod_ids,
    _create_aggregator,
    _create_and_connect_pod_mailbox,
    _create_message_service,
    _get_idp_url,
    combine_pod_schemas,
)
from bitfount.federated.transport.config import (
    _DEV_MESSAGE_SERVICE_PORT,
    _DEV_MESSAGE_SERVICE_TLS,
    _DEV_MESSAGE_SERVICE_URL,
    _STAGING_MESSAGE_SERVICE_URL,
    PRODUCTION_MESSAGE_SERVICE_URL,
    MessageServiceConfig,
)
from bitfount.federated.transport.message_service import _MessageService
from bitfount.federated.transport.pod_transport import _PodMailbox
from bitfount.hub.api import _DEV_IDP_URL, _PRODUCTION_IDP_URL, _STAGING_IDP_URL
from bitfount.hub.authentication_flow import BitfountSession
from tests.utils.helper import create_schema, get_warning_logs, unit_test


@unit_test
class TestHelperFunctions:
    """Test federated helper functions."""

    @fixture
    def test_url(self) -> str:
        """Test URL."""
        return "not.a.real.url.com"

    @fixture
    def schema(self) -> BitfountSchema:
        """Creates a schema fixture."""
        return create_schema(classification=True)

    def test_create_insecure_aggregator_successfully(self) -> None:
        """Tests create_aggregator function without secure aggregation."""
        aggregator = _create_aggregator(secure_aggregation=False)
        assert isinstance(aggregator, Aggregator)
        assert not isinstance(aggregator, SecureAggregator)

    def test_create_secure_aggregator_successfully(self) -> None:
        """Tests create_aggregator function with secure aggregation."""
        aggregator = _create_aggregator(secure_aggregation=True)
        assert isinstance(aggregator, SecureAggregator)

    @pytest.mark.parametrize(
        "environment, expected_config, input_config",
        [
            (
                "production",
                MessageServiceConfig(url=PRODUCTION_MESSAGE_SERVICE_URL),
                None,
            ),
            ("staging", MessageServiceConfig(url=_STAGING_MESSAGE_SERVICE_URL), None),
            (
                "dev",
                MessageServiceConfig(
                    url=_DEV_MESSAGE_SERVICE_URL,
                    port=_DEV_MESSAGE_SERVICE_PORT,
                    tls=_DEV_MESSAGE_SERVICE_TLS,
                ),
                None,
            ),
            (
                None,
                MessageServiceConfig(url=cast(str, lazy_fixture("test_url"))),
                MessageServiceConfig(url=cast(str, lazy_fixture("test_url"))),
            ),
        ],
        indirect=["environment"],
    )
    def test_create_message_service_successfully(
        self,
        environment: None,
        expected_config: MessageServiceConfig,
        input_config: Optional[MessageServiceConfig],
    ) -> None:
        """Tests create_message_service method works.

        Ensures correct config is passed through to the created message service.
        """
        message_service = _create_message_service(
            session=create_autospec(BitfountSession, instance=True),
            ms_config=input_config,
        )
        assert isinstance(message_service, _MessageService)
        assert message_service.config == expected_config

    def test_create_message_service_issues_warning_for_local_storage(
        self, caplog: LogCaptureFixture
    ) -> None:
        """Tests create_message_service issues warning if using local storage."""
        ms_config = MessageServiceConfig(use_local_storage=True)
        message_service = _create_message_service(
            session=create_autospec(BitfountSession, instance=True),
            ms_config=ms_config,
        )
        assert isinstance(message_service, _MessageService)

        # Check for warning message; should be thing logged
        warning_logs = get_warning_logs(caplog)
        assert (
            "Messages will contain local file references. "
            "Ensure all pods have access to your local file system. "
            "Otherwise your task will hang." in warning_logs
        )

    async def test_create_and_connect_pod_mailbox_successfully(
        self, mocker: MockerFixture
    ) -> None:
        """Tests create_and_connect_pod_mailbox method works."""
        # We know that `create_message_service` is already tested so we mock out
        # its response and check it is called correctly.
        mock_create_message_service = mocker.patch(
            "bitfount.federated.helper._create_message_service"
        )

        # We also need to mock out the PodMailbox.connect_pod() class method.
        mock_connect_pod = mocker.patch.object(
            _PodMailbox, "connect_pod", autospec=True
        )
        mock_connect_pod.return_value = create_autospec(_PodMailbox, instance=True)

        # Create mocks for args we don't care about
        pod_name = "not-a-real-pod"
        mock_session = create_autospec(BitfountSession, instance=True)
        mock_ms_config = create_autospec(MessageServiceConfig, instance=True)

        mailbox = await _create_and_connect_pod_mailbox(
            pod_name=pod_name,
            session=mock_session,
            ms_config=mock_ms_config,
        )

        assert isinstance(mailbox, _PodMailbox)
        mock_connect_pod.assert_called_once_with(
            pod_name=pod_name, message_service=mock_create_message_service()
        )

    def test__check_and_update_pod_ids(self, mocker: MockerFixture) -> None:
        """Tests that the pod identifiers are updated correctly."""
        mock_hub = mocker.patch("bitfount.hub.api.BitfountHub")
        mock_hub.username = "my-username"
        pod_id_1 = "my-pod"
        pod_id_2 = "your-username/your-pod"
        pod_ids = _check_and_update_pod_ids([pod_id_1, pod_id_2], mock_hub)
        assert pod_ids == ["my-username/my-pod", "your-username/your-pod"]

    @pytest.mark.parametrize(
        "invalid_pod_id",
        ["Invalid", "INVALID", "invalid-", "-invalid", "invalid--invalid"],
    )
    def test__check_and_update_pod_ids_errors(
        self, invalid_pod_id: str, mocker: MockerFixture
    ) -> None:
        """Tests that the pod identifiers error correctly."""
        mock_hub = mocker.patch("bitfount.hub.api.BitfountHub")
        mock_hub.username = "my-username"

        with pytest.raises(PodNameError):
            _check_and_update_pod_ids([invalid_pod_id], mock_hub)

    def test_idp_url_gets_staging_url(self, monkeypatch: MonkeyPatch) -> None:
        """Tests that the idp_url is loaded based on staging environment."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "staging")
        idp_url = _get_idp_url()
        assert idp_url == _STAGING_IDP_URL

    def test_idp_url_gets_prod_url(self, monkeypatch: MonkeyPatch) -> None:
        """Tests that the idp_url is loaded based on staging environment."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "production")
        idp_url = _get_idp_url()
        assert idp_url == _PRODUCTION_IDP_URL

    def test_idp_url_gets_dev_url(self, monkeypatch: MonkeyPatch) -> None:
        """Tests that the idp_url is loaded based on dev environment."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "dev")
        idp_url = _get_idp_url()
        assert idp_url == _DEV_IDP_URL

    def test_combine_pod_schemas_raises_error_if_there_are_duplicated_table_names(
        self, mocker: MockerFixture, schema: BitfountSchema
    ) -> None:
        """Tests that schemas can't be combined if they have the same table names."""
        schema_2 = copy.deepcopy(schema)
        mocker.patch(
            "bitfount.federated.helper.get_pod_schema", side_effect=[schema, schema_2]
        )
        with pytest.raises(BitfountSchemaError):
            combine_pod_schemas(["pod_1", "pod_2"])

    def test_combine_pod_schemas_correctly(
        self, mocker: MockerFixture, schema: BitfountSchema
    ) -> None:
        """Tests that schemas can be combined correctly."""
        schema_2 = copy.deepcopy(schema)
        schema_2.tables[0].name = "table_2"
        mocker.patch(
            "bitfount.federated.helper.get_pod_schema", side_effect=[schema, schema_2]
        )
        combined_schema = combine_pod_schemas(["pod_1", "pod_2"])
        assert isinstance(combined_schema, BitfountSchema)
        assert len(combined_schema.tables) == 2
        assert combined_schema.table_names == schema.table_names + schema_2.table_names
