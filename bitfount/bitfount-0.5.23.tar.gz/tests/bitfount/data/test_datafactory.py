"""Tests for datafactory.py."""

from _pytest.monkeypatch import MonkeyPatch
import pytest

from bitfount.config import _BASIC_ENGINE, _PYTORCH_ENGINE
from bitfount.data.datafactory import _BasicDataFactory, _get_default_data_factory
from bitfount.exceptions import BitfountEngineError
from tests.utils.helper import unit_test


@unit_test
class TestDefaultDataFactoryLoading:
    """Tests the default factory loading."""

    def test_load_default_data_factory(self, monkeypatch: MonkeyPatch) -> None:
        """Test that the default data factory can load."""
        # Set envvar value
        monkeypatch.setattr("bitfount.data.datafactory.BITFOUNT_ENGINE", _BASIC_ENGINE)
        df = _get_default_data_factory()
        assert isinstance(df, _BasicDataFactory)

    def test_load_default_data_factory_fail_on_import_error(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests handling if the imported library throws an ImportError."""
        # Try with PyTorch backend, even if can't be imported here
        monkeypatch.setattr(
            "bitfount.data.datafactory.BITFOUNT_ENGINE", _PYTORCH_ENGINE
        )
        try:
            monkeypatch.delattr(
                "bitfount.backends.pytorch.data.datafactory._PyTorchDataFactory"
            )
        except ImportError:
            pass

        with pytest.raises(BitfountEngineError, match="pytorch"):
            _get_default_data_factory()

    def test_load_default_data_factory_fails_unknown_engine(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests that if the engine type is unknown, an error is raised."""
        monkeypatch.setattr(
            "bitfount.data.datafactory.BITFOUNT_ENGINE", "NOT_AN_ENGINE"
        )

        with pytest.raises(
            BitfountEngineError, match="Unable to load engine NOT_AN_ENGINE."
        ):
            _get_default_data_factory()
