import json
from urllib.request import urlopen
import yaml

from jsonschema import validate

from pydmt.utils.filesystem import mkdir_touch

from pydmt.api.one_source_one_target import OneSourceOneTarget

METADATA = "metadata"
SCHEMA_URL_JSON = "schema_url_json"
SCHEMA_URL_YAML = "schema_url_yaml"


class BuilderYaml(OneSourceOneTarget):
    def build(self):
        with open(self.source) as yaml_stream:
            data = yaml.safe_load(yaml_stream)
            if isinstance(data, dict):
                if METADATA in data:
                    metadata = data[METADATA]
                    if SCHEMA_URL_JSON in metadata:
                        schema_url = data[METADATA][SCHEMA_URL_JSON]
                        with urlopen(schema_url) as f:
                            schema = json.loads(f.read())
                            validate(data, schema)
                    if SCHEMA_URL_YAML in metadata:
                        schema_url = data[METADATA][SCHEMA_URL_YAML]
                        with urlopen(schema_url) as f:
                            schema = yaml.safe_load(f.read())
                            validate(data, schema)
            mkdir_touch(self.target)
