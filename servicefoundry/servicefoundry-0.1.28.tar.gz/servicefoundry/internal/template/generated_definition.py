from pathlib import Path

import yaml
from jsonschema.exceptions import ValidationError

from ..clients.service_foundry_client import ServiceFoundryServiceClient
from ..const import BUILD_DIR, BUILD_PACK, COMPONENT
from ..exceptions import ConfigurationException
from ..model.build_pack import BuildPack
from ..util import download_file
from .util import load_yaml_from_file, validate_schema

SPEC = "spec"


def get_base_yaml(base_id):
    base_file = f"{BUILD_DIR}/template/{base_id}"

    if not Path(base_file).is_file():
        tfs_client = ServiceFoundryServiceClient.get_client(auth_required=False)
        package_url = tfs_client.get_base_by_id(base_id)["url"]
        download_file(package_url, base_file)

    return load_yaml_from_file(base_file)


class GeneratedDefinition:
    def __init__(self, base_build_id, base_component_id, resolved_overrides):
        self.base_def = {
            BUILD_PACK: get_base_yaml(base_build_id),
            COMPONENT: get_base_yaml(base_component_id),
        }
        for key, value in resolved_overrides:
            self._apply_overwrite(self.base_def, key.split("."), value)

    def write(self, file="servicefoundry.lock.yaml"):
        with open(file, "w") as outfile:
            yaml.dump_all(self.base_def.values(), outfile, default_flow_style=False)

    def get_build_pack(self):
        return BuildPack(**self.base_def[BUILD_PACK][SPEC])

    def get_component(self):
        return self.base_def[COMPONENT]

    def validate(self):
        try:
            validate_schema(self.base_def[BUILD_PACK], "schema/build_pack_schema.json")
        except ValidationError as err:
            raise ConfigurationException(f"Build pack validation failed. {err.message}")

        try:
            validate_schema(self.base_def[COMPONENT], "schema/component_schema.json")
        except ValidationError as err:
            raise ConfigurationException(f"Component validation failed. {err.message}")

    def _apply_overwrite(self, definition, keys, value):
        key = keys[0]
        if len(keys) == 1:
            definition[keys[0]] = value
            return
        if key in definition:
            self._apply_overwrite(definition[key], keys[1:], value)
        else:
            raise ConfigurationException(f"{key} not found in {definition}")
