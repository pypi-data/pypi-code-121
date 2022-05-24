# -*- coding: utf-8 -*-

from tuxsuite import config
from dataclasses import dataclass


@dataclass
class Config:
    group: str
    project: str
    token: str
    tuxapi_url: str


__config__ = None


def load_config():
    global __config__
    if not __config__:
        __config__ = config.Config()

    return Config(
        group=__config__.group,
        project=__config__.project,
        token=__config__.auth_token,
        tuxapi_url=__config__.tuxapi_url,
    )
