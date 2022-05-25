# copyright 2022 Medicines Discovery Catapult
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-
"""
Environment aware config module to auto detect and manage both injected and Environment variable config
"""
import argparse
import json
import logging
import os
import pathlib
import yaml
from pyhocon import ConfigFactory, ConfigTree
from pyhocon.exceptions import ConfigMissingException

LOGGER = logging.getLogger(__name__)
COMMON_ENVVAR_NAME = "PY_ENV_AWARE_COMMON"
CONFIG_ENVVAR_NAME = "PY_ENV_AWARE_CONFIG"


class InvalidConfigError(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="consumer specific configuration file (YAML)")
    parser.add_argument("--common", help="common configuration (YAML)")
    args, _ = parser.parse_known_args()
    return args


def get_config(initial=None):
    args = parse_args()

    # Raise Exeption if both environmental variables and arguments are used
    common_from_args = args.common
    common_from_env = os.environ.get(COMMON_ENVVAR_NAME)
    if common_from_args and common_from_env:
        raise InvalidConfigError('You should use either COMMON_ENVVAR_NAME or --common to set the common file but not both')

    config_from_args = args.config
    config_from_env = os.environ.get(CONFIG_ENVVAR_NAME)
    if config_from_args and config_from_env:
        raise InvalidConfigError(f'You should use either {CONFIG_ENVVAR_NAME} or --config to set the config file but not both')
    # End: Raise Exeption if both environmental variables and arguments are used

    common_file = common_from_args or common_from_env
    config_file = config_from_args or config_from_env

    conf = EnvironmentAwareConfig(filepath=common_file)
    if isinstance(initial, dict):
        ConfigTree.merge_configs(conf, ConfigTree(initial))
    return EnvironmentAwareConfig(filepath=config_file, initial=conf)


class EnvironmentAwareConfig(ConfigTree):
    """
    Config object to allow use of both YAML and HOCON formats
    """

    def __init__(self, filepath=None, initial=None, prefix=None):
        """
        Initialise Config object by building config from
        """
        self.prefix = prefix
        super().__init__()

        def load_file(path):
            if pathlib.Path(path).suffix in [".yml", ".yaml"]:
                with open(path, 'r') as f:
                    return ConfigFactory.from_dict(yaml.load(f, Loader=yaml.FullLoader))

            if pathlib.Path(path).suffix in [".json", ".js"]:
                with open(path, 'r') as f:
                    return ConfigFactory.from_dict(json.load(f))
            return ConfigFactory.parse_file(path)

        def apply(param):
            if not param:
                param = dict()

            c = ConfigFactory.from_dict(param) if (isinstance(param, dict)) else load_file(param)
            ConfigTree.merge_configs(self, c)

        apply(initial)
        apply(filepath)

    @staticmethod
    def _env_key(key, prefix=None):
        if isinstance(prefix, str):
            return ".".join([prefix, key]).upper().replace(".", "_")
        return key.upper().replace(".", "_")

    @staticmethod
    def _as_type(val: str):
        try:
            return int(val)
        except ValueError:
            pass

        try:
            return float(val)
        except ValueError:
            pass

        if val.lower() in ['true', 'yes', 'y']:
            return True

        if val.lower() in ['false', 'no', 'n']:
            return False

        return val

    def get(self, key, default=None):
        env_key = EnvironmentAwareConfig._env_key(key, self.prefix)
        if env_key in os.environ:
            return EnvironmentAwareConfig._as_type(os.getenv(env_key))
        try:
            result = super().get(key)
            if isinstance(result, dict):
                return EnvironmentAwareConfig(initial=result, prefix=key if self.prefix is None else ".".join([self.prefix, key]))
            return result
        except ConfigMissingException as err:
            if default is not None:
                return default
            raise err

    def __getitem__(self, item):
        try:
            return self.get(item)
        except ConfigMissingException as err:
            raise KeyError(item) from err

    def has(self, key):
        try:
            self.get(key)
            return True
        except ConfigMissingException:
            return False
