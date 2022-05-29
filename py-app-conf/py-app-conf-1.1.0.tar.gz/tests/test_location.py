from pathlib import Path
from unittest.mock import patch

from pyappconf.model import AppConfig, BaseConfig
from tests import os_specific
from tests.fixtures.model import get_model_object, model_object


@os_specific.run_in(os_specific.OSType.LINUX)
def test_config_base_location_linux(model_object: BaseConfig):
    with patch("sys.platform", "linux"):
        assert (
            model_object.settings.config_base_location
            == Path("~").expanduser() / ".config" / "MyApp" / "config"
        )


@os_specific.run_in(os_specific.OSType.LINUX)
def test_config_location_linux(model_object: BaseConfig):
    with patch("sys.platform", "linux"):
        assert (
            model_object.settings.config_location
            == Path("~").expanduser() / ".config" / "MyApp" / "config.toml"
        )


# TODO: Add config location tests for Windows and MacOS


def test_custom_config_folder():
    folder = Path("/woo")
    obj = get_model_object(
        settings=AppConfig(app_name="MyApp", custom_config_folder=folder)
    )
    assert obj.settings.config_base_location == (folder / "config")


def test_custom_config_name():
    folder = Path("/woo")
    obj = get_model_object(
        settings=AppConfig(
            app_name="MyApp", custom_config_folder=folder, config_name="yeah"
        )
    )
    assert obj.settings.config_base_location == (folder / "yeah")
