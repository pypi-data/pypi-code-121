#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the Process base flow
"""

from .request_flow import RequestFlow


class ProcessFlow(RequestFlow):
    """
    A subclass for Process flow
    """

    def __init__(self, request, client, logger, config):
        super().__init__(request, client, logger, config)
