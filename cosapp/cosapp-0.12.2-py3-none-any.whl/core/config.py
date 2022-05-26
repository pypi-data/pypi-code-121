"""
Configuration of CoSApp.
"""
import os
import sys
import json

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
import logging
from pathlib import Path
from typing import FrozenSet

import jsonschema

logger = logging.getLogger(__name__)


class CoSAppConfiguration:
    r"""Encapsulate CoSApp configuration parameters and its handlers.
    
    CoSApp configuration folder are by default store in 
    On Linux::

       $HOME/.cosapp.d

    On Windows::

       %USERPROFILE%\.cosapp.d

    This default configuration folder is overwritten by the environment
    variable ``COSAPP_CONFIG_DIR``.
    """

    COSAPP_CONFIG_DIR = ".cosapp.d"
    CONFIG_FILE = "cosapp_config.json"  # type: str

    def __init__(self) -> None:
        """Constructor"""
        self._userid = ""  # type: str
        self._roles = frozenset()  # type: FrozenSet[FrozenSet[str]]

        self.__load_configuration()

    def __get_config_path(self) -> str:
        folder = Path(
            os.environ.get("COSAPP_CONFIG_DIR", None) or 
            Path.home().joinpath(CoSAppConfiguration.COSAPP_CONFIG_DIR)
        )
        return folder.joinpath(CoSAppConfiguration.CONFIG_FILE)

    def __load_configuration(self) -> None:
        """Read configuration from file or generate the default.

        Raises
        ------
        OSError
            If the current platform is not recognized
        """
        fullpath = self.__get_config_path()
        warning_msg = "The configuration file cannot be opened, fall back to default."
        if os.path.isfile(fullpath):  # Load local parameters - offline connection
            try:
                parameters = self.validate_file(fullpath)
                self._userid = parameters["userid"]
                self._roles = frozenset(
                    [frozenset(role) for role in parameters["roles"]]
                )
            except (OSError, JSONDecodeError):
                logger.warning(warning_msg)
        else:
            logger.warning(warning_msg)
        self.update_configuration()  # Try to update user permission from official root

    @property
    def userid(self) -> str:
        """str : User ID"""
        return self._userid

    @property
    def roles(self) -> FrozenSet[FrozenSet[str]]:
        """FrozenSet[FrozenSet[str]] : Roles that the user can impersonate."""
        return self._roles

    @staticmethod
    def validate_file(path: str) -> dict:
        """Validate the provided file against JSON schema for configuration file.

        Parameters
        ----------
        path : str
            Absolute path to the file to be tested.

        Returns
        -------
        dict
            The dictionary read in the validated file

        Raises
        ------
        jsonschema.exceptions.ValidationError
            If the provided file does not conform to the JSON schema.
        """
        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "configuration_schema.json"
            )
        ) as fp:
            config_schema = json.load(fp)
        with open(path) as untested_file:
            params = json.load(untested_file)

        jsonschema.validate(params, config_schema)

        return params

    def update_configuration(self) -> None:
        """Update the configuration file for the current user.

        The update process ask the server about updated role.
        """
        if len(self._userid) == 0:
            self._userid = os.environ.get("USERNAME", "") or os.environ.get("USER", "")

            if not self._userid:
                raise OSError("Unable to find the user id.")

        # TODO - request reference roles source here

        # Save back the changes following the update
        parameters = {"userid": self.userid, "roles": list()}

        for role in self.roles:
            parameters["roles"].append(list(role))

        try:
            config_file = self.__get_config_path()
            config_dir = os.path.dirname(config_file)
            if not os.path.isdir(config_dir):
                os.makedirs(config_dir)

            with open(config_file, "w") as file:
                json.dump(parameters, file, sort_keys=True)
        except OSError:
            logger.warning("Fail to save configuration locally.")
