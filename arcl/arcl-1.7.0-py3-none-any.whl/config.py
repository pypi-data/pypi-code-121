import abc
import os
import time

import requests

USER_HOME_DIR = os.path.expanduser("~")
ARCHIMEDES_CONF_DIR = os.path.join(USER_HOME_DIR, ".archimedes")

if not os.path.exists(ARCHIMEDES_CONF_DIR):
    os.mkdir(ARCHIMEDES_CONF_DIR)

ARCHIMEDES_API_CONFIG_URL = (
    f"https://arcl.optimeering.no/config.json?timestamp={time.time()}"
)


class InvalidEnvironmentException(Exception):
    pass


class ApiConfig(abc.ABC):
    def __init__(self, env):
        config_result = requests.get(
            ARCHIMEDES_API_CONFIG_URL, headers={"Cache-Control": "no-cache"}
        )
        self.config = config_result.json()
        if env not in self.config.keys():
            raise InvalidEnvironmentException(
                f"Invalid environment {env}, "
                f"supported values are {', '.join([str(key) for key in self.config.keys()])}"
            )
        self.environment = env.lower()

    def __getattr__(self, item):
        env_config = self.config[self.environment]
        return env_config[item]


def get_api_config(environment):
    return ApiConfig(environment)


def get_config_path(env):
    return os.path.join(ARCHIMEDES_CONF_DIR, f"arcl-{env}.json")


def get_token_path(env):
    return os.path.join(ARCHIMEDES_CONF_DIR, f"msal-{env}.cache.bin")


def get_legacy_config_path():
    return os.path.join(ARCHIMEDES_CONF_DIR, f"arcl.json")


def get_legacy_token_path():
    return os.path.join(ARCHIMEDES_CONF_DIR, f"msal.cache.bin")
