"""Tests for config.py."""
import importlib
import sys
from typing import Generator, List, Optional, Tuple

import GPUtil
from _pytest.monkeypatch import MonkeyPatch
import pytest
from pytest import fixture
from pytest_mock import MockerFixture

import bitfount.config
from bitfount.config import (
    _DEVELOPMENT_ENVIRONMENT,
    _PRODUCTION_ENVIRONMENT,
    _STAGING_ENVIRONMENT,
    _get_environment,
)
from tests.utils.helper import unit_test


@unit_test
class TestConfigLoading:
    """Tests for loading variables during config.py import."""

    @fixture
    def config_unimport(self) -> Generator[None, None, None]:
        """Ensures the config module can be freshly imported in the test."""
        # Retrieve and store the old reference to config
        old_ref = sys.modules.pop("bitfount.config")

        yield

        # Restore sys.modules mapping and local namespace
        sys.modules["bitfount.config"] = old_ref
        bitfount.config = old_ref

    def test_config_loading_no_env_var(
        self, config_unimport: None, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests default value assignment if no envvar."""
        monkeypatch.delenv("BITFOUNT_ENGINE", raising=False)
        config = importlib.import_module("bitfount.config")
        assert config.BITFOUNT_ENGINE == "pytorch"

    def test_config_loading_invalid_envvar(
        self, config_unimport: None, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests exception raised if invalid envvar for BITFOUNT_ENGINE."""
        monkeypatch.setenv("BITFOUNT_ENGINE", "not_a_backend")
        with pytest.raises(ValueError, match=".*(not_a_backend).*"):
            importlib.import_module("bitfount.config")

    def test_config_loading_valid_envvar(
        self, config_unimport: None, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests BITFOUNT_ENGINE setting from environment with valid value."""
        monkeypatch.setenv("BITFOUNT_ENGINE", bitfount.config._PYTORCH_ENGINE)
        config = importlib.import_module("bitfount.config")
        assert config.BITFOUNT_ENGINE == bitfount.config._PYTORCH_ENGINE


@unit_test
class TestGetGPUMetadata:
    """Tests retrieving GPU Metadata."""

    @pytest.mark.parametrize(
        "gpu_info,expected_result",
        [
            ([], (None, 0)),  # getGPUs returns empty list
            (
                [
                    GPUtil.GPU(
                        x,
                        f"uuid-{x}",
                        0.5,
                        5.3,
                        0.2,
                        5.0,
                        "NVIDIA xyz",
                        "BitfountGPU",
                        f"123{x}",
                        "None",
                        False,
                        36,
                    )
                    for x in range(3)
                ],
                ("BitfountGPU", 3),
            ),
        ],
    )
    def test_get_gpu_metadata_with_basic_engine(
        self,
        expected_result: Tuple[Optional[str], int],
        gpu_info: List[GPUtil.GPU],
        mocker: MockerFixture,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test that GPUUtil can is used to retrieve GPU info."""
        # Set envvar value
        monkeypatch.setattr(
            "bitfount.config.BITFOUNT_ENGINE", bitfount.config._BASIC_ENGINE
        )

        getGPUs = mocker.patch("bitfount.config.GPUtil.getGPUs")
        getGPUs.return_value = gpu_info

        gpu_metadata = bitfount.config.get_gpu_metadata()

        assert gpu_metadata == expected_result

    def test_get_gpu_metadata_with_basic_engine_throws_exception(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        """Test that GPUUtil is used to retrieve GPU info."""
        # Set envvar value
        monkeypatch.setattr(
            "bitfount.config.BITFOUNT_ENGINE", bitfount.config._BASIC_ENGINE
        )

        getGPUs = mocker.patch("bitfount.config.GPUtil.getGPUs")
        getGPUs.side_effect = Exception(
            "Pretend bad thing happened inside imported library"
        )

        gpu_metadata = bitfount.config.get_gpu_metadata()

        assert gpu_metadata == (None, 0)

    @pytest.mark.parametrize(
        "device_name,device_count,expected_result",
        [(None, 0, (None, 0)), ("BitfountGPU", 3, ("BitfountGPU", 3))],
    )
    def test_get_gpu_metadata_with_pytorch_engine(
        self,
        device_count: int,
        device_name: Optional[str],
        expected_result: Tuple[Optional[str], int],
        mocker: MockerFixture,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test that CUDA is used to retrieve GPU info."""
        # Set envvar value
        monkeypatch.setattr(
            "bitfount.config.BITFOUNT_ENGINE", bitfount.config._PYTORCH_ENGINE
        )

        cuda = mocker.patch("bitfount.config.torch.cuda")
        cuda.get_device_name.return_value = device_name
        cuda.device_count.return_value = device_count

        gpu_metadata = bitfount.config.get_gpu_metadata()

        assert gpu_metadata == expected_result

    def test_get_gpu_metadata_with_pytorch_engine_throws_exception(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        """Test that GPUUtil is used to retrieve GPU info."""
        # Set envvar value
        monkeypatch.setattr(
            "bitfount.config.BITFOUNT_ENGINE", bitfount.config._PYTORCH_ENGINE
        )

        cuda = mocker.patch("bitfount.config.torch.cuda")
        cuda.get_device_name.side_effect = Exception(
            "Pretend bad thing happened inside imported library"
        )
        cuda.device_count.return_value = 0

        gpu_metadata = bitfount.config.get_gpu_metadata()

        assert gpu_metadata == (None, 0)


class TestBitfountEnvironment:
    """Tests that the BITFOUNT_ENVIRONMENT environment variable is read correctly."""

    @unit_test
    def test_get_environment_dev(self, monkeypatch: MonkeyPatch) -> None:
        """Tests dev environment is read correctly."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "dev")
        env = _get_environment()
        assert env == _DEVELOPMENT_ENVIRONMENT

    @unit_test
    def test_get_environment_staging(self, monkeypatch: MonkeyPatch) -> None:
        """Tests staging environment is read correctly."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "staging")
        env = _get_environment()
        assert env == _STAGING_ENVIRONMENT

    @unit_test
    def test_get_environment_production(self, monkeypatch: MonkeyPatch) -> None:
        """Tests production environment is read correctly."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "production")
        env = _get_environment()
        assert env == _PRODUCTION_ENVIRONMENT

    @unit_test
    def test_get_environment_variable_not_set(self, monkeypatch: MonkeyPatch) -> None:
        """Tests that environment defaults to production variable has not been set."""
        monkeypatch.delenv("BITFOUNT_ENVIRONMENT", raising=False)
        env = _get_environment()
        assert env == _PRODUCTION_ENVIRONMENT

    @unit_test
    def test_get_environment_unknown_variable_raises_environment_error(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests that error is raised if environment is not recognised."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "not-a-real-env")
        with pytest.raises(ValueError):
            _get_environment()
