"""
Generate test data for file output
"""
from pyappconf import AppConfig
from tests.config import (
    DATA_NAME,
    INPUT_DATA_DIR,
    JSON_PATH,
    JSON_WITH_SCHEMA_PATH,
    TOML_PATH,
    YAML_PATH,
    YAML_WITH_SCHEMA_PATH,
)
from tests.fixtures.model import get_model_object

if __name__ == "__main__":
    conf = get_model_object()
    conf.to_json(out_path=JSON_PATH, json_kwargs=dict(indent=2))
    conf.to_yaml(out_path=YAML_PATH)
    conf.to_toml(out_path=TOML_PATH)

    settings_with_schema = AppConfig(
        app_name="MyApp", schema_url="https://example.com/schema.json"
    )
    conf_with_schema = get_model_object(settings=settings_with_schema)
    conf_with_schema.to_json(out_path=JSON_WITH_SCHEMA_PATH, json_kwargs=dict(indent=2))
    conf_with_schema.to_yaml(out_path=YAML_WITH_SCHEMA_PATH)
