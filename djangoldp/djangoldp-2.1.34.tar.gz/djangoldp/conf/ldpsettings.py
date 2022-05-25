import os
import sys
import yaml
import logging
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings as django_settings
from pathlib import Path
from collections import OrderedDict
from typing import Iterable
from . import default_settings

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


logger = logging.getLogger(__name__)


def configure(filename='settings.yml'):
    """Helper function to configure django from LDPSettings."""

    yaml_config = None
    try:
        with open(filename, 'r') as f:
            yaml_config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.info('Starting project without configuration file')

    # ref: https://docs.djangoproject.com/fr/2.2/topics/settings/#custom-default-settings
    ldpsettings = LDPSettings(yaml_config)

    django_settings.configure(ldpsettings)


class LDPSettings(object):

    """Class managing the DjangoLDP configuration."""

    def __init__(self, config):

        """Build a Django Setting object from a dict."""

        if django_settings.configured:
            raise ImproperlyConfigured('Settings have been configured already')

        self._config = config
        self._settings = self.build_settings()

    def build_settings(self, extend=['INSTALLED_APPS', 'MIDDLEWARE']):
        """
        Look for the parameters in multiple places.
        Each step overrides the value of the previous key found. Except for "extend" list. Those value must be lists and all values found are added to these lists without managing duplications.

        Resolution order of the configuration:
          1. Core default settings
          2. Packages settings
          3. Code from a local settings.py file
          4. YAML config file
        """

        # helper loop
        def update_with(config):
            for k, v in config.items():

                if k in extend:
                    settings[k].extend(v)

                elif not k.startswith('_'):
                    settings.update({k: v})

        # start from default core settings
        settings = default_settings.__dict__.copy()
        logger.debug(f'Building settings from core defaults')

        # INSTALLED_APPS starts empty
        settings['INSTALLED_APPS'] = []

        # look settings from packages in the order they are given (local overrides installed)
        for pkg in self.DJANGOLDP_PACKAGES:

            # FIXME: There is something better to do here with the sys.modules path
            try:
                # override with values from installed package
                mod = import_module(f'{pkg}.djangoldp_settings')
                update_with(mod.__dict__)
                logger.debug(f'Updating settings from installed package {pkg}')
            except ModuleNotFoundError:
                pass

            try:
                # override with values from local package
                mod = import_module(f'{pkg}.{pkg}.djangoldp_settings')
                update_with(mod.__dict__)
                logger.debug(f'Updating settings from local package {pkg}')
            except ModuleNotFoundError:
                pass

        # look in settings.py file in directory
        try:
            mod = import_module('settings')
            update_with(mod.__dict__)
            logger.debug(f'Updating settings from local settings.py file')
        except ModuleNotFoundError:
            pass

        # look in YAML config file 'server' section
        try:
            conf = self._config.get('server', {})
            update_with(conf)
            logger.debug(f'Updating settings with project config')
        except KeyError:
            pass

        # In the end adds the INSTALLED_APPS from the core
        settings['INSTALLED_APPS'].extend(getattr(default_settings,'INSTALLED_APPS'))

        return settings

    @property
    def DJANGOLDP_PACKAGES(self):

        """Returns the list of LDP packages configured."""

        pkg = self._config.get('ldppackages', [])
        return [] if pkg is None else pkg

    @property
    def INSTALLED_APPS(self):

        """Return the installed apps and the LDP packages."""

        # get ldp packages (they are django apps)
        apps = self.DJANGOLDP_PACKAGES.copy()

        # add the default apps
        apps.extend(self._settings['INSTALLED_APPS'])

        # As settings come from different origins duplicuation is likeliy to happen
        return list(OrderedDict.fromkeys(apps))

    def __getattr__(self, param):
        """Return the requested parameter from cached settings."""
        if param.startswith('_') or param.islower():
            # raise the django exception for inexistent parameter
            raise AttributeError(f'"{param}" is not compliant to django settings format')
        try:
            return self._settings[param]
        except KeyError:
            # raise the django exception for inexistent parameter
            raise AttributeError(f'no "{param}" parameter found in settings')

