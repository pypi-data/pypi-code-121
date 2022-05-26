import configparser
import os
from dataclasses import dataclass
from typing import Optional

import click

import montecarlodata.settings as settings
from montecarlodata.fs_utils import mkdirs


@dataclass
class Config:
    mcd_id: str
    mcd_token: str
    mcd_api_endpoint: str
    aws_profile: Optional[str] = None
    aws_region: Optional[str] = None


class ConfigManager:
    """
     Token is generated at https://github.com/monte-carlo-data/monolith-django/blob/a18ffc64ea2517166e66f0d3e85417b582398513/monolith/service/account.py#L236
     with the function call as `secrets.token_urlsafe(42)`, which is always 56 characters 
     Details in https://docs.python.org/3/library/secrets.html#secrets.token_urlsafe
    """
    TOKEN_LENGTH = 56
    MCD_TOKEN = 'mcd_token'

    def __init__(self, profile_name: str, base_path: str, config_parser: Optional[configparser.ConfigParser] = None):
        self._profile_name = profile_name
        self._base_path = base_path
        self._profile_config_file = os.path.join(self._base_path, settings.PROFILE_FILE_NAME)

        self._config = config_parser or configparser.ConfigParser()
        self._config.read(self._profile_config_file)


    """
        There is a circular dependency between ConfigManager and montecarlodata.errors
        so the decorator is imported here instead at top of the file with the other local imports. 
        TODO: Move the config class into common.
    """
    from montecarlodata.errors import manage_errors
    @manage_errors
    def write(self, **kwargs) -> None:
        """
        Write any configuration key value pairs to the specified section (profile name)
        """        
        if self._profile_name not in self._config.sections():
            # if the section does not exist add it
            self._config.add_section(self._profile_name)

        for k, v in kwargs.items():
            if k == self.MCD_TOKEN and len(v) != self.TOKEN_LENGTH:
                raise ValueError(f"{self.MCD_TOKEN} received should have {self.TOKEN_LENGTH} length but received {len(v)}")
            self._config.set(self._profile_name, k, v)

        mkdirs(self._base_path)
        with open(self._profile_config_file, 'w') as cf:
            self._config.write(cf)

    def read(self) -> Optional[Config]:
        """
        Return configuration from section (profile name) if it exists.
        Any MCD values can be overwritten by the environment. Uses system default for AWS if not set.
        """
        try:
            return Config(
                mcd_id=settings.MCD_DEFAULT_API_ID or self._config.get(self._profile_name, 'mcd_id'),
                mcd_token=settings.MCD_DEFAULT_API_TOKEN or self._config.get(self._profile_name, 'mcd_token'),
                mcd_api_endpoint=settings.MCD_API_ENDPOINT or self._config.get(self._profile_name, 'mcd_api_endpoint', fallback=settings.MCD_DEFAULT_API_ENDPOINT),
                aws_profile=self._config.get(self._profile_name, 'aws_profile', fallback=None),
                aws_region=self._config.get(self._profile_name, 'aws_region', fallback=None)
            )
        except configparser.NoSectionError:
            click.echo(f"Failed to find configuration for '{self._profile_name}'. Please setup using 'configure' first")