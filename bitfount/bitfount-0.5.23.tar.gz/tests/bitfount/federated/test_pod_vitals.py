"""Unit tests for _PodVitals webserver."""
import time
from unittest.mock import AsyncMock, Mock

from aiohttp.test_utils import TestClient, TestServer
import pytest
from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from bitfount.federated.pod_vitals import _PodVitals, _PodVitalsHandler
from tests.utils.helper import unit_test
from tests.utils.mocks import create_dataclass_mock


@unit_test
class TestPodVitals:
    """Test TestPodVitals."""

    async def test__last_task_execution_time_update(self) -> None:
        """Test last_task_execution_time is updated as expected."""
        pod_vitals = _PodVitals()
        new_time = time.time()
        lock_acquired_mock = Mock()
        lock_released_mock = Mock()
        pod_vitals._last_task_execution_lock = Mock(
            __enter__=lock_acquired_mock, __exit__=lock_released_mock
        )

        pod_vitals.last_task_execution_time = new_time

        # check lock was acquired in updating last_task_execution_time
        lock_acquired_mock.assert_called_once()
        lock_released_mock.assert_called_once()
        assert pod_vitals.last_task_execution_time == new_time
        # check lock was acquired again in above assertion when
        # retrieving last_task_execution_time
        assert lock_acquired_mock.call_count == 2
        assert lock_acquired_mock.call_count == 2


@unit_test
class Test_PodVitalsHandler:
    """Test Test_PodVitalsHandler."""

    @pytest.fixture
    def pod_vitals(self) -> Mock:
        """Pod vitals mock fixture."""
        mock_pod_vitals = create_dataclass_mock(_PodVitals)
        mock_pod_vitals.last_task_execution_time = time.time()
        return mock_pod_vitals

    @pytest.fixture
    def handler(self, pod_vitals: _PodVitals) -> _PodVitalsHandler:
        """Pod vitals handler fixture."""
        handler = _PodVitalsHandler(pod_vitals)
        handler.runner = Mock()
        return handler

    @pytest.fixture
    def server(self, handler: _PodVitalsHandler) -> TestServer:
        """Test server fixture."""
        return TestServer(handler.app)

    @pytest.fixture
    def mock_open_socket(self, mocker: MockerFixture) -> AsyncMock:
        """Mocks out the Modeller.run() method in protocol.py."""
        mock_open_socket_method: AsyncMock = mocker.patch(
            "bitfount.federated.pod_vitals._PodVitalsHandler._open_socket"
        )
        mock_open_socket_method.return_value = 8080
        return mock_open_socket_method

    async def test__status_request(self, server: TestServer) -> None:
        """Test /status endpoint to determines if the webserver is responding."""
        async with TestClient(server) as client:
            resp = await client.request("GET", "/status")
            json_resp = await resp.json()
            assert resp.status == 200
            assert json_resp == {"status": "OK"}

    async def test__health_request(self, server: TestServer) -> None:
        """Test /health endpoint determines if a pod is healthy."""
        async with TestClient(server) as client:
            resp = await client.request("GET", "/health")
            json_resp = await resp.json()
            assert resp.status == 200
            assert json_resp == {"healthy": True}

    async def test__unhealth_request(
        self, mocker: MockerFixture, server: TestServer
    ) -> None:
        """Test /health endpoint determines if a pod is unhealthy.

        If the last time a task was executed is greate than
        MAX_TASK_EXECUTION_TIME, the endpoint should return that
        the pod is unhealthly.
        """
        mocker.patch("bitfount.federated.pod_vitals.MAX_TASK_EXECUTION_TIME", 0)
        async with TestClient(server) as client:
            resp = await client.request("GET", "/health")
            json_resp = await resp.json()
            assert resp.status == 200
            assert json_resp == {"healthy": False}

    async def test__open_socket(
        self, handler: _PodVitalsHandler, mocker: MockerFixture
    ) -> None:
        """Test the socket library is used to get an open port."""
        expected_port = 8080
        mock_socket = mocker.patch("socket.socket")
        mock_socket.return_value.recv.return_value = 1
        mock_socket.return_value.getsockname.return_value = ("host", expected_port)
        port = handler._open_socket()
        assert port == expected_port
        mock_socket.return_value.getsockname.assert_called_once()

    async def test__pod_vitals_port_env_var_set(
        self,
        handler: _PodVitalsHandler,
        mock_open_socket: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test pod health port is set to BITFOUNT_POD_VITALS_PORT env var."""
        pod_vitals_port = 8080
        monkeypatch.setenv("BITFOUNT_POD_VITALS_PORT", str(pod_vitals_port))
        result = handler._get_pod_vitals_port()
        assert result == pod_vitals_port
        assert not mock_open_socket.called

    async def test__pod_vitals_port_no_env_var(
        self, handler: _PodVitalsHandler, mock_open_socket: Mock
    ) -> None:
        """Test pod health port when BITFOUNT_POD_VITALS_PORT not set.

        If BITFOUNT_POD_VITALS_PORT is not set as an environment variable
        the port number should be determined by _open_socket method.
        """
        port = 8080
        result = handler._get_pod_vitals_port()
        assert result == port
        mock_open_socket.assert_called_once()

    async def test__pod_vitals_error_invalid_port(
        self,
        handler: _PodVitalsHandler,
        mock_open_socket: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test exception raised when BITFOUNT_POD_VITALS_PORT is invalid."""
        pod_vitals_port = "abc123"
        expected_error_msg = (
            "BITFOUNT_POD_VITALS_PORT must be an integer. "
            f"BITFOUNT_POD_VITALS_PORT set to '{pod_vitals_port}'"
        )
        monkeypatch.setenv("BITFOUNT_POD_VITALS_PORT", str(pod_vitals_port))
        with pytest.raises(ValueError) as error:
            handler._get_pod_vitals_port()
            assert str(error.value) == expected_error_msg

        assert not mock_open_socket.called

    async def test__pod_vitals_error_invalid_port_range(
        self,
        handler: _PodVitalsHandler,
        mock_open_socket: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test exception raised when BITFOUNT_POD_VITALS_PORT is invalid."""
        pod_vitals_port = "99999"
        monkeypatch.setenv("BITFOUNT_POD_VITALS_PORT", str(pod_vitals_port))
        with pytest.raises(ValueError) as error:
            handler._get_pod_vitals_port()
            assert (
                str(error.value)
                == "Invalid BITFOUNT_POD_VITALS_PORT given. Must be in range [1-65535]"
            )
        assert not mock_open_socket.called

    async def test__start_webserver(
        self,
        handler: _PodVitalsHandler,
        mocker: MockerFixture,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Ensure server is started with expected settings."""
        port = 8080
        monkeypatch.setenv("BITFOUNT_POD_VITALS_PORT", str(port))
        mock_tcp_site = mocker.patch("bitfount.federated.pod_vitals.TCPSite")
        mock_loop = AsyncMock()

        handler.start(mock_loop)

        mock_tcp_site.assert_called_once_with(handler.runner, "0.0.0.0", port)
        mock_tcp_site.return_value.start.assert_called_once()
