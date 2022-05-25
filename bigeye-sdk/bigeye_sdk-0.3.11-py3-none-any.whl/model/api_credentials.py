from __future__ import annotations

import abc
import json
from dataclasses import dataclass
from bigeye_sdk.log import get_logger

# create logger
log = get_logger(__file__)


class ApiConf(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def build(cls, api_conf: dict) -> ApiConf:
        pass

    @classmethod
    def load_api_conf(cls, file: str) -> BasicAuthRequestLibApiConf:
        log.info(f'Loading API Conf: {file}')
        with open(file) as json_file:
            return BasicAuthRequestLibApiConf(**json.load(json_file))


@dataclass
class BasicAuthRequestLibApiConf(ApiConf):
    """
    Configuration models to bind required host and authentication details for data_modules runtimes.
    TODO: Move away from basic auth in the future.
    """
    base_url: str
    """Host URL for the Bigeye -- e.g. app.bigeye.com"""
    user: str
    """Basic Auth user for this host."""
    password: str
    """Basic Auth password for this host."""

    @classmethod
    def build(cls, api_conf: dict) -> BasicAuthRequestLibApiConf:
        return BasicAuthRequestLibApiConf(**api_conf)
