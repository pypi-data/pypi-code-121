import sys
from importlib.metadata import version
from importlib.resources import path as rpath
from datetime import datetime, timezone
from configparser import ConfigParser
from logging import Logger, getLogger

from .utils import get_expanded_path

log: Logger = getLogger(__name__)


DEFAULT_CONFIG_PATH = '$XDG_CONFIG_HOME/pyssg/config.ini'
VERSION = version('pyssg')


def __expand_all_paths(config: ConfigParser) -> None:
    log.debug('expanding all path options')
    for option in config.options('path'):
        path: str = config.get('path', option)
        config.set('path', option, get_expanded_path(path))


def __check_well_formed_config(config: ConfigParser) -> None:
    log.debug('checking that config file is well formed')
    default_config: ConfigParser = ConfigParser()
    with rpath('pyssg.plt', 'default.ini') as p:
        log.debug('reading config file "%s"', p)
        default_config.read(p)

    for section in default_config.sections():
        log.debug('checking section "%s"', section)
        if not config.has_section(section):
            log.error('config does not have section "%s"', section)
            sys.exit(1)
        for option in default_config.options(section):
            log.debug('checking option "%s"', option)
            if not config.has_option(section, option):
                log.error('config does not have option "%s" in section "%s"', option, section)
                sys.exit(1)


def get_parsed_config(path: str) -> ConfigParser:
    config: ConfigParser = ConfigParser()
    log.debug('reading config file "%s"', path)
    config.read(path)

    __check_well_formed_config(config)
    __expand_all_paths(config)

    # set other required options
    log.debug('setting extra config options')
    config.set('fmt', 'rss_date', '%%a, %%d %%b %%Y %%H:%%M:%%S GMT')
    config.set('fmt', 'sitemap_date', '%%Y-%%m-%%d')
    config.set('info', 'version', VERSION)
    config.set('info', 'rss_run_date', datetime.now(
        tz=timezone.utc).strftime(config.get('fmt', 'rss_date')))
    config.set('info', 'sitemap_run_date', datetime.now(
        tz=timezone.utc).strftime(config.get('fmt', 'sitemap_date')))

    return config
