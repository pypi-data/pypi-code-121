# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helpers for customizing the configuration in a controlled manner."""

from invenio_base.utils import load_or_import_from_config


class FromConfig:
    """Data descriptor to connect config with application configuration.

    See https://docs.python.org/3/howto/descriptor.html .

    .. code-block:: python

        # service/config.py
        class ServiceConfig:
            foo = FromConfig("FOO", default=1)

        # config.py
        FOO = 2

        # ext.py
        c = ServiceConfig.build(app)
        c.foo  # 2
    """

    def __init__(self, config_key, default=None):
        """Constructor for data descriptor."""
        self.config_key = config_key
        self.default = default

    def __get__(self, obj, objtype=None):
        """Return value that was grafted on obj (descriptor protocol)."""
        return load_or_import_from_config(
            app=obj._app,
            key=self.config_key,
            default=self.default)

    def __set_name__(self, owner, name):
        """Store name of grafted field (descriptor protocol)."""
        # If we want to allow setting it we can implement this.
        pass

    def __set__(self, obj, value):
        """Set value on grafted_field of obj (descriptor protocol)."""
        # If we want to allow setting it we can implement this.
        pass


class ConfiguratorMixin:
    """Shared customization for requests service config."""

    @classmethod
    def build(cls, app):
        """Build the config object."""
        return type(f"Custom{cls.__name__}", (cls,), {"_app": app})()
