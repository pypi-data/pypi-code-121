#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the Connect client methods for Validation Flow
"""

from .client_manager import ClientManager


class ValidationClient(ClientManager):
    """
    Class to manage api request for validations
    """

    def __init__(self, client):
        super().__init__(client)
