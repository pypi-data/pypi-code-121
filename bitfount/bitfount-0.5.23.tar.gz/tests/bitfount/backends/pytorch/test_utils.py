"""Tests for PyTorch-specific utils."""
from typing import Callable

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from bitfount.backends.pytorch.utils import _autodetect_gpu
import bitfount.config
from bitfount.data.datafactory import _get_default_data_factory
from tests.utils.helper import backend_test, unit_test


def mock_device_count(count: int = 0) -> Callable[[], int]:
    """Mock device counter for CUDA."""

    def f() -> int:
        return count

    return f


@backend_test
@unit_test
class TestUtils:
    """Tests for util functions."""

    def test_autodetect_gpu_cpu_only(
        self, caplog: LogCaptureFixture, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests auto-detecting GPU count when only CPU."""
        # Mock out CUDA device count
        caplog.set_level("INFO")
        monkeypatch.setattr("torch.cuda.device_count", mock_device_count(0))

        count = _autodetect_gpu()

        assert count == 0
        assert (
            caplog.records[0].msg == "No supported GPU detected. Running model on CPU."
        )

    def test_autodetect_1_gpu(
        self, caplog: LogCaptureFixture, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests auto-detecting GPU when only one GPU."""
        # Mock out CUDA device count
        caplog.set_level("INFO")
        monkeypatch.setattr("torch.cuda.device_count", mock_device_count(1))
        monkeypatch.setattr("torch.cuda.get_device_name", lambda x: f"GPU_{x}")

        count = _autodetect_gpu()

        assert count == 1
        assert (
            caplog.records[0].msg == "CUDA support detected. GPU (GPU_0) will be used."
        )

    def test_autodetect_multiple_gpu(
        self, caplog: LogCaptureFixture, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests auto-detecting GPU when multiple GPUs."""
        # Mock out CUDA device count
        caplog.set_level("INFO")
        monkeypatch.setattr("torch.cuda.device_count", mock_device_count(2))
        monkeypatch.setattr("torch.cuda.get_device_name", lambda x: f"GPU_{x}")

        count = _autodetect_gpu()

        assert count == 1
        assert caplog.records[0].levelname == "WARNING"
        assert (
            caplog.records[0].msg
            == "Bitfount model currently only supports one GPU. Will use GPU 0 (GPU_0)."
        )
        assert (
            caplog.records[1].msg == "CUDA support detected. GPU (GPU_0) will be used."
        )


@backend_test
@unit_test
class TestDefaultDataFactoryLoading:
    """Tests for loading the default data factory when PyTorch installed."""

    def test_load_pytorch_default_data_factory(self, monkeypatch: MonkeyPatch) -> None:
        """Test that the default data factory can load."""
        # Ensure PyTorch is set as the engine variable
        monkeypatch.setattr(
            "bitfount.config.BITFOUNT_ENGINE", bitfount.config._PYTORCH_ENGINE
        )

        # Create a fake class and set that as the PyTorch data factory
        class FakeDataFactory:
            pass

        monkeypatch.setattr(
            "bitfount.backends.pytorch.data.datafactory._PyTorchDataFactory",
            FakeDataFactory,
        )

        df = _get_default_data_factory()
        assert isinstance(df, FakeDataFactory)
