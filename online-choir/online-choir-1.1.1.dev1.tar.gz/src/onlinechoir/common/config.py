from configparser import ConfigParser
from pathlib import Path

from .platform import get_config_folder


def read_config(fname: Path):
    conf = ConfigParser()
    conf.read(str(fname))
    return conf


def config_path() -> Path:
    return get_config_folder() / 'config.ini'


def default_config():
    return read_config(config_path())
