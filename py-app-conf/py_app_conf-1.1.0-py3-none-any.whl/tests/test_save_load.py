import shutil
from pathlib import Path
from typing import Optional, Tuple, Type

import pytest
from pydantic import BaseModel

from pyappconf.model import AppConfig, BaseConfig, ConfigFormats
from tests.config import (
    DATA_NAME,
    GENERATED_DATA_DIR,
    INPUT_DATA_DIR,
    JSON_PATH,
    NON_EXISTENT_INPUT_JSON_PATH,
    NON_EXISTENT_NAME,
    RECURSIVE_INPUT_FOLDER,
    TOML_PATH,
    YAML_PATH,
)
from tests.fixtures.model import (
    get_model_classes,
    get_model_object,
    model_class_with_defaults,
    model_classes,
    model_object,
    model_object_with_defaults,
)


def _save_load_test(custom_settings: AppConfig) -> Tuple[BaseConfig, Type[BaseConfig]]:
    mod = get_model_object(settings=custom_settings)
    mod.save()
    assert str(mod.settings.config_location).endswith(
        custom_settings.default_format.value
    )

    OrigConfig, SubConfig = get_model_classes()

    class MyConfig(OrigConfig):
        _settings = custom_settings

    assert str(MyConfig._settings.config_location).endswith(
        custom_settings.default_format.value
    )
    obj = MyConfig.load()
    assert mod == obj
    return obj, MyConfig


def test_save_load_toml():
    custom_settings = AppConfig(
        app_name="MyApp", custom_config_folder=GENERATED_DATA_DIR
    )
    _save_load_test(custom_settings)


def test_save_load_yaml():
    custom_settings = AppConfig(
        app_name="MyApp",
        custom_config_folder=GENERATED_DATA_DIR,
        default_format=ConfigFormats.YAML,
    )
    _save_load_test(custom_settings)


def test_save_load_json():
    custom_settings = AppConfig(
        app_name="MyApp",
        custom_config_folder=GENERATED_DATA_DIR,
        default_format=ConfigFormats.JSON,
    )
    _save_load_test(custom_settings)


def test_save_load_yaml_with_schema():
    expect_schema_url = "https://example.com/schema.json"
    custom_settings = AppConfig(
        app_name="MyApp",
        custom_config_folder=GENERATED_DATA_DIR,
        default_format=ConfigFormats.YAML,
        schema_url=expect_schema_url,
    )
    obj, MyConfig = _save_load_test(custom_settings)
    assert MyConfig._settings.schema_url == expect_schema_url
    yaml_str = obj.to_yaml()
    assert expect_schema_url in yaml_str
    yaml_str_no_schema = obj.to_yaml(include_schema_url=False)
    assert expect_schema_url not in yaml_str_no_schema


def test_save_load_json_with_schema():
    expect_schema_url = "https://example.com/schema.json"
    custom_settings = AppConfig(
        app_name="MyApp",
        custom_config_folder=GENERATED_DATA_DIR,
        default_format=ConfigFormats.JSON,
        schema_url=expect_schema_url,
    )
    obj, MyConfig = _save_load_test(custom_settings)
    assert MyConfig._settings.schema_url == expect_schema_url
    json_str = obj.to_json()
    assert expect_schema_url in json_str
    json_str_no_schema = obj.to_json(include_schema_url=False)
    assert expect_schema_url not in json_str_no_schema


def assert_model_loaded_with_extension(
    mod: BaseConfig, model_object: BaseConfig, config_format: ConfigFormats
):
    assert mod.settings.custom_config_folder == INPUT_DATA_DIR
    assert mod.settings.default_format == config_format
    assert mod.settings.config_name == DATA_NAME

    mod.settings = model_object.settings
    assert mod == model_object


def test_load_toml_with_custom_path(
    model_object: BaseConfig, model_classes: Tuple[Type[BaseConfig], Type[BaseModel]]
):
    MyConfig, _ = model_classes
    orig_config_location = MyConfig._settings.config_location
    mod = MyConfig.load(TOML_PATH)
    assert mod._settings.config_location == orig_config_location
    assert_model_loaded_with_extension(mod, model_object, ConfigFormats.TOML)


def test_load_yaml_with_custom_path(
    model_object: BaseConfig, model_classes: Tuple[Type[BaseConfig], Type[BaseModel]]
):
    MyConfig, _ = model_classes
    orig_config_location = MyConfig._settings.config_location
    mod = MyConfig.load(YAML_PATH)
    assert mod._settings.config_location == orig_config_location
    assert_model_loaded_with_extension(mod, model_object, ConfigFormats.YAML)


def test_load_json_with_custom_path(
    model_object: BaseConfig, model_classes: Tuple[Type[BaseConfig], Type[BaseModel]]
):
    MyConfig, _ = model_classes
    orig_config_location = MyConfig._settings.config_location
    mod = MyConfig.load(JSON_PATH)
    assert mod._settings.config_location == orig_config_location
    assert_model_loaded_with_extension(mod, model_object, ConfigFormats.JSON)


def test_load_or_create_with_path_exists(
    model_object: BaseConfig, model_classes: Tuple[Type[BaseConfig], Type[BaseModel]]
):
    MyConfig, _ = model_classes
    orig_config_location = MyConfig._settings.config_location
    mod = MyConfig.load_or_create(JSON_PATH)
    assert mod._settings.config_location == orig_config_location
    assert_model_loaded_with_extension(mod, model_object, ConfigFormats.JSON)


def test_load_or_create_with_path_does_not_exist(
    model_object_with_defaults: BaseConfig, model_class_with_defaults: Type[BaseConfig]
):
    MyConfig = model_class_with_defaults
    model_object = model_object_with_defaults
    orig_config_location = MyConfig._settings.config_location
    mod = MyConfig.load_or_create(NON_EXISTENT_INPUT_JSON_PATH)
    assert mod._settings.config_location == orig_config_location
    assert mod.settings.custom_config_folder == INPUT_DATA_DIR
    assert mod.settings.default_format == ConfigFormats.JSON
    assert mod.settings.config_name == NON_EXISTENT_NAME

    mod.settings = model_object.settings
    assert mod == model_object


@pytest.mark.parametrize(
    "path, expect_string",
    [
        (RECURSIVE_INPUT_FOLDER / "1", "loaded from 1"),
        (RECURSIVE_INPUT_FOLDER / "2", "loaded from recursive"),
        # Third and fourth cases - didn't find recursive, go to default location
        (INPUT_DATA_DIR, "a"),
        (None, "a"),
    ],
)
def test_load_recursive(path: Optional[Path], expect_string: str):
    OrigConfig, SubConfig = get_model_classes()

    shutil.copy(
        INPUT_DATA_DIR / "data.toml", GENERATED_DATA_DIR / "recursive-config.toml"
    )

    custom_settings = AppConfig(
        app_name="MyApp",
        custom_config_folder=GENERATED_DATA_DIR,
        config_name="recursive-config",
    )

    class MyConfig(OrigConfig):
        _settings = custom_settings

    orig_config_location = MyConfig._settings.config_location
    mod = MyConfig.load_recursive(path)
    assert mod._settings.config_location == orig_config_location

    assert mod.string == expect_string
