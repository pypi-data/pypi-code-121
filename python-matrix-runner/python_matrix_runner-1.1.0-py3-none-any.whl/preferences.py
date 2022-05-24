# -*- coding: utf-8 -*-

import inspect
import logging

from configparser import ConfigParser
from pathlib import Path
from site import USER_BASE

from colorlog import default_log_colors


__all__ = ['Preferences', 'log_level', 'log_colors', 'prefix_colors', 'summary_colors']


class Preferences:
    """Preferences capsule"""

    system_conf = Path(__file__).parent.joinpath("default.conf")
    user_conf = Path(USER_BASE).joinpath("matrix_runner.conf")
    local_conf = Path(inspect.stack()[-1][1]).resolve().parent.joinpath("matrix_runner.conf")
    instance = None

    def __init__(self, system: Path = system_conf, user: Path = user_conf, local: Path = local_conf):
        """Load preferences from multi-leveled configuration files

        Local preferences take precedence over user and system levels.
        User preferences take precedence over system level.
        System preferences take precedence over built-in fallback values.

        Args:
            system: Path to the system level configuration file
            user: Path to the user level configuration file
            local: Path to the local configuration file
        """
        self._conf = ConfigParser()
        self._conf.read(system)
        self._conf.read(user)
        self._conf.read(local)

    @property
    def log_level(self):
        """Default log level"""
        level = self._conf.get('global', 'loglevel', fallback='WARNING')
        levelnum = logging.getLevelName(level)
        if isinstance(levelnum, int):
            return levelnum
        logging.warning("Invalid log level defined in config file: '%s'!", level)
        return logging.WARNING

    @property
    def log_colors(self):
        """Colors to be used for log output."""
        return {k: self._conf.get('colors', k, fallback=v) for k, v in default_log_colors.items()}

    @property
    def prefix_colors(self):
        """Colors to be used for log prefix."""
        return {
            'config': self._conf.get('colors', 'config', fallback='blue'),
            'action': self._conf.get('colors', 'action', fallback='purple'),
        }

    @property
    def summary_colors(self):
        """Colors to be used for summaries."""
        return {
            'config': self._conf.get('colors', 'summary_config', fallback='bold_blue'),
            'success': self._conf.get('colors', 'summary_success', fallback='green'),
            'unstable': self._conf.get('colors', 'summary_unstable', fallback='yellow'),
            'skip': self._conf.get('colors', 'summary_skip', fallback='yellow'),
            'fail': self._conf.get('colors', 'summary_fail', fallback='bold_red'),
            'error': self._conf.get('colors', 'summary_error', fallback='bold_red')
        }


def log_level():
    """Default log level"""
    if not Preferences.instance:
        Preferences.instance = Preferences()
    return Preferences.instance.log_level


def log_colors():
    """Colors to be used for log output."""
    if not Preferences.instance:
        Preferences.instance = Preferences()
    return Preferences.instance.log_colors


def prefix_colors():
    """Colors to be used for log prefix."""
    if not Preferences.instance:
        Preferences.instance = Preferences()
    return Preferences.instance.prefix_colors


def summary_colors():
    """Colors to be used for summaries."""
    if not Preferences.instance:
        Preferences.instance = Preferences()
    return Preferences.instance.summary_colors
