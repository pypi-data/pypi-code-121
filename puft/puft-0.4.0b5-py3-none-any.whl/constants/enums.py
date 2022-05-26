"""Module with constants and typehints."""
from typing import Any, List, Dict, Tuple, Union, Callable, Literal, get_args
from enum import Enum


class AppModeEnum(Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class CLIDatabaseEnum(Enum):
    INIT = "init"
    MIGRATE = "migrate"
    UPGRADE = "upgrade"


class CLIRunEnum(Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class CLIHelperEnum(Enum):
    SHELL = "shell"
    DEPLOY = "deploy"
    CUSTOM_CMD = "custom_cmd"


class HTTPMethodEnum(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class TurboActionEnum(Enum):
    APPEND = "append"
    PREPEND = "prepend"
    REPLACE = "replace"
    UPDATE = "update"
    REMOVE = "remove"


class DatabaseTypeEnum(Enum):
    SQLITE = "sqlite"
    PSQL = "psql"


class ConfigExtensionEnum(Enum):
    YAML = "yaml"
    JSON = "json"
