#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the Request base flow
"""

from .base_flow import BaseFlow
from ..request import Request


class RequestFlow(BaseFlow):
    """
    A subclass for Request flow
    """

    def __init__(self, request, client, logger, config):
        super().__init__(request, client, logger, config)

        # Deserialize request
        self.request_data = Request(**request)
