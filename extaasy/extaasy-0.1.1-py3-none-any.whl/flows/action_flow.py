#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the Action base flow
"""

from connect.eaas.extension import ProductActionResponse

from ..action import Action
from .base_flow import BaseFlow


class ActionFlow(BaseFlow):
    """
    A subclass for Action flow
    """

    def __init__(self, request, client, logger, config):
        super().__init__(request, client, logger, config)
        self.data = Action(**request)

    def handle(self) -> ProductActionResponse:
        return super().handle()
