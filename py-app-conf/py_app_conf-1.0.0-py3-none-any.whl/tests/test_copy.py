from pathlib import Path

from pyappconf import AppConfig


def test_copy_settings():
    app_config = AppConfig(app_name="MyApp")
    orig_location = app_config.config_location
    new_folder = Path("somewhere")
    new_location = new_folder / "config.toml"
    new_config = app_config.copy(custom_config_folder=new_folder)
    assert new_config.config_location == new_location
    assert app_config.config_location == orig_location
