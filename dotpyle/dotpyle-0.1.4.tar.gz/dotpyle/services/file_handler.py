import glob
import itertools
from os.path import join, isfile, isdir
from os import listdir
from yaml import safe_load, safe_dump
from dotpyle.utils.path import (
    get_configuration_path,
    get_local_configuration_path,
    get_dotfiles_path,
    get_script_path,
)
from shutil import copy2
from dotpyle.utils import constants
from dotpyle.services.logger import Logger


class BasicFileHandler:
    def __init__(self, file_path: str, template_path: str, logger: Logger):
        self.logger = logger

        if not isfile(file_path):
            self.logger.warning(
                "File {0} does not exist. Creating from template...".format(
                    file_path
                )
            )
            copy2(template_path, file_path)

        self.file_path = file_path
        self._config = self.read()

    def read(self):
        self.logger.warning("Reading file {0}".format(self.file_path))
        with open(self.file_path, "r") as stream:
            self._config = safe_load(stream)

        return self._config

    def save(self, config: dict):
        """Save the configuration to the file.

        Args:
            config (str): New configuration for the file.
        """
        # TODO: Check config first
        with open(self.file_path, "w") as stream:
            safe_dump(config, stream)
            self._config = config

    @property
    def config(self):
        return self._config


class FileHandler(BasicFileHandler):
    def __init__(self, logger: Logger, path=None):
        super().__init__(
            file_path=get_configuration_path() if path is None else path,
            template_path=constants.CONFIG_TEMPLATE_PATH,
            logger=logger,
        )

    def get_profile_paths(self, key, profile):
        dotfiles_path = join(get_dotfiles_path())
        for key in [
            f for f in listdir(dotfiles_path) if isdir(join(dotfiles_path, f))
        ]:
            key_path = join(dotfiles_path, key)
            for prof in [
                f for f in listdir(key_path) if isdir(join(key_path, f))
            ]:
                prof_path = join(key_path, prof)
                return list(
                    itertools.chain(
                        glob.iglob(join(prof_path, "**")),
                        glob.iglob(join(prof_path, ".**")),
                    )
                )


class LocalFileHandler(BasicFileHandler):
    def __init__(self, logger: Logger, path=None):
        super().__init__(
            file_path=get_local_configuration_path() if path is None else path,
            template_path=constants.CONFIG_LOCAL_TEMPLATE_PATH,
            logger=logger,
        )

    def install_profile(self, name, profile):
        self.config["installed"][name] = profile

    def uninstall_profile(self, name):
        del self.config["installed"][name]

    def is_profile_installed(self, name, value):
        return (
            name in self.config["installed"]
            and self.config["installed"][name] == value
        )

    def get_installed_profile(self, name):
        installed = self.get_installed()
        return installed.get(name, None)
        # if name in installed:
        # return installed[name]
        # return None  # maybe raise exception

    def get_installed(self):
        return self.config["installed"]


class ScriptFileHandler(BasicFileHandler):
    def __init__(self, logger: Logger, script_name: str):
        super().__init__(
            file_path=get_script_path(script_name),
            template_path=constants.SCRIPT_TEMPLATE_PATH,
            logger=logger,
        )
