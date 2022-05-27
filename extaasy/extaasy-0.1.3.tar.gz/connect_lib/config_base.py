#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the common methods to access to Connect environment variables
"""

from . import messages
from .exceptions import ConfigurationError


class ConfigBase:
    """
    Class to manage config common needs
    """

    def __init__(self, config):
        self.config = config

    def get_config_param(self, id_) -> str:
        """
        Obtain config parameter, which is an Environment Variable

        :param id_: Environment Variable identifier

        :return: Environment Variable value

        :raises: ConfigurationError
        """

        try:
            return self.config[id_]
        except (TypeError, KeyError):
            raise ConfigurationError(messages.CONFIGURATION_ERROR_ENVIRONMENT_VARIABLE.format(id=id_))
