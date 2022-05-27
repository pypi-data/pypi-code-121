"""Tests config.py."""
import inspect

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
import pytest
from pytest import fixture

from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.transport.protos.messages_pb2_grpc import MessageServiceStub
from tests.utils.helper import unit_test


@unit_test
class TestMessageServiceConfig:
    """Tests for MessageServiceConfig."""

    @fixture
    def test_url(self) -> str:
        """URL for tests."""
        return "not.a.real.url.com"

    def test_ms_config_raises_value_error_if_production_url_and_tls_disabled(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        """Ensure TLS can't be disabled with production hub url."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "production")
        with pytest.raises(ValueError):
            MessageServiceConfig(tls=False)

    def test_ms_config_raises_value_error_if_staging_url_and_tls_disabled(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        """Ensure TLS can't be disabled with staging hub url."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "staging")
        with pytest.raises(ValueError):
            MessageServiceConfig(tls=False)

    def test_ms_config_issues_warning_if_tls_disabled_with_custom_url(
        self, caplog: LogCaptureFixture
    ) -> None:
        """Ensure that warning is issued if tls is disabled with non-bitfount URL.

        NB: There should only be one record in caplog.records.
        """
        MessageServiceConfig(url="custom.ms.url.com")
        for record in caplog.records:
            assert record.levelname == "WARNING"
            assert record.getMessage() == "Message service communication without TLS."

    async def test_creates_message_service_stub_secure(self, test_url: str) -> None:
        """Tests create_message_service_stub with TLS."""
        ms_config = MessageServiceConfig(tls=False, url=test_url)
        stub = await ms_config.stub
        assert isinstance(stub, MessageServiceStub)

    async def test_creates_message_service_stub_insecure(self, test_url: str) -> None:
        """Tests create_message_service_stub without TLS."""
        ms_config = MessageServiceConfig(tls=True, url=test_url)
        stub = await ms_config.stub
        assert isinstance(stub, MessageServiceStub)

    def test_stub_property_is_async(self, test_url: str) -> None:
        """Tests that the MessageServiceConfig.stub property is async."""
        # Check is property (properties exist on the class)
        assert isinstance(MessageServiceConfig.stub, property)

        # Check property getter is async
        assert inspect.iscoroutinefunction(MessageServiceConfig.stub.fget)
