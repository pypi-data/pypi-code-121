#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements specific exceptions
"""


class ConfigurationError(Exception):
    """
    Configuration Exception
    An error in the configuration prevents the application from running.
    """

    def __init__(self, message: str):
        super().__init__(message)
