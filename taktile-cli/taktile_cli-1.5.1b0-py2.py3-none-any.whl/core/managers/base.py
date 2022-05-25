import logging
import pathlib
from typing import Optional, Union

import yaml

from tktl import __version__
from tktl.core.config import Settings, settings
from tktl.core.managers.constants import CONFIG_FILE_TEMPLATE

log = logging.getLogger("root")


class BaseConfigManager(object):
    """Base class for managing a configuration file.
    Based on the amazing github.com/polyaxon/polyaxon config manager setup
    """

    TKTL_DIR: Optional[str]
    CONFIG_FILE_NAME: str
    CONFIG: Optional[dict]
    SETTINGS: Settings = settings

    @staticmethod
    def create_dir(dir_path: str) -> None:
        try:
            pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Except permission denied and potential race conditions
            # in multi-threaded environments.
            log.error(f"Could not create config directory {dir_path}: {repr(e)}")

    @classmethod
    def get_config_file_path(cls) -> pathlib.Path:
        if not cls.TKTL_DIR:
            # local to this directory
            base_path = pathlib.Path.cwd()
        else:
            base_path = pathlib.Path(cls.TKTL_DIR)
        return base_path / cls.CONFIG_FILE_NAME

    @classmethod
    def init_config(cls, init: Union[str, bool] = False) -> None:
        cls.set_config(init=init)

    @classmethod
    def is_initialized(cls) -> bool:
        config_file_path = cls.get_config_file_path()
        return config_file_path.is_file()

    @classmethod
    def set_config(cls, init: Union[str, bool] = False) -> None:
        config_file_path = cls.get_config_file_path()

        if config_file_path.is_file() and init:
            log.debug(
                "%s file already present at %s", cls.CONFIG_FILE_NAME, config_file_path
            )
            return

        if init:
            config_file_content = CONFIG_FILE_TEMPLATE.format(version=__version__)
            with open(config_file_path, "w") as config_file_handle:
                config_file_handle.write(config_file_content)

    @classmethod
    def get_config(cls) -> Optional[dict]:
        if not cls.is_initialized():
            return None
        config_file_path = cls.get_config_file_path()
        with open(config_file_path, "r") as config_file:
            return yaml.safe_load(config_file)

    @classmethod
    def get_value(cls, key: str) -> Union[Optional[str], Optional[dict]]:
        config = cls.get_config()
        if config:
            if key in config.keys():
                return config[key]
            else:
                log.warning("Config `%s` has no key `%s`", cls.CONFIG_FILE_NAME, key)
        return None
