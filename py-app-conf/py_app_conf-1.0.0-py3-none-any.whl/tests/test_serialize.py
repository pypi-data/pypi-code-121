from typing import Tuple, Type

from pydantic import BaseModel

from pyappconf.model import BaseConfig
from tests.config import JSON_PATH, TOML_PATH, YAML_PATH
from tests.fixtures.model import model_classes, model_object


def test_to_json(model_object: BaseConfig):
    assert model_object.to_json() == JSON_PATH.read_text()


def test_to_yaml(model_object: BaseConfig):
    assert model_object.to_yaml() == YAML_PATH.read_text()


def test_to_toml(model_object: BaseConfig):
    assert model_object.to_toml() == TOML_PATH.read_text()


def test_from_json(
    model_object: BaseConfig, model_classes: Tuple[Type[BaseConfig], Type[BaseModel]]
):
    MyConfig, SubConfig = model_classes
    loaded_object = MyConfig.parse_json(JSON_PATH)
    assert model_object == loaded_object


def test_from_yaml(
    model_object: BaseConfig, model_classes: Tuple[Type[BaseConfig], Type[BaseModel]]
):
    MyConfig, SubConfig = model_classes
    loaded_object = MyConfig.parse_yaml(YAML_PATH)
    assert model_object == loaded_object


def test_from_toml(
    model_object: BaseConfig, model_classes: Tuple[Type[BaseConfig], Type[BaseModel]]
):
    MyConfig, SubConfig = model_classes
    loaded_object = MyConfig.parse_toml(TOML_PATH)
    assert model_object == loaded_object


def test_json_schema(model_classes: Tuple[Type[BaseConfig], Type[BaseModel]]):
    MyConfig, SubConfig = model_classes
    assert (
        MyConfig.schema_json()
        == '{"title": "MyConfig", "description": "Base class for settings, allowing values to be overridden by environment variables.\\n\\nThis is useful in production for secrets you do not wish to save in code, it plays nicely with docker(-compose),\\nHeroku and any 12 factor app design.", "type": "object", "properties": {"string": {"title": "String", "env_names": ["myapp_string"], "type": "string"}, "integer": {"title": "Integer", "env_names": ["myapp_integer"], "type": "integer"}, "custom": {"title": "Custom", "env_names": ["myapp_custom"], "allOf": [{"$ref": "#/definitions/SubConfig"}]}, "dictionary": {"title": "Dictionary", "env_names": ["myapp_dictionary"], "type": "object", "additionalProperties": {"$ref": "#/definitions/SubConfig"}}, "str_list": {"title": "Str List", "env_names": ["myapp_str_list"], "type": "array", "items": {"type": "string"}}, "int_tuple": {"title": "Int Tuple", "env_names": ["myapp_int_tuple"], "type": "array", "items": {"type": "integer"}}, "default_string": {"title": "Default String", "default": "woo", "env_names": ["myapp_default_string"], "type": "string"}, "default_custom": {"title": "Default Custom", "default": {"a": "yeah", "b": 5.6}, "env_names": ["myapp_default_custom"], "allOf": [{"$ref": "#/definitions/SubConfig"}]}, "default_enum": {"default": "one", "env_names": ["myapp_default_enum"], "allOf": [{"$ref": "#/definitions/MyEnum"}]}, "default_enum_list": {"env_names": ["myapp_default_enum_list"], "type": "array", "items": {"$ref": "#/definitions/MyEnum"}}, "file_path": {"title": "File Path", "default": "/a/b.txt", "env_names": ["myapp_file_path"], "type": "string", "format": "path"}}, "required": ["string", "integer", "custom", "dictionary", "str_list", "int_tuple"], "additionalProperties": false, "definitions": {"SubConfig": {"title": "SubConfig", "type": "object", "properties": {"a": {"title": "A", "type": "string"}, "b": {"title": "B", "type": "number"}}, "required": ["a", "b"]}, "MyEnum": {"title": "MyEnum", "description": "An enumeration.", "enum": ["one", "two"], "type": "string"}}}'
    )
