#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the common base flow
"""

import json
from typing import Optional, Union

from connect.eaas.extension import ProcessingResponse, ProductActionResponse, ValidationResponse

from .. import consts
from ..logger import ExtensionLoggerAdapter


class BaseFlow:
    """
    A flow base class
    """

    def __init__(self, request, client, logger, config):
        # Initialize logger adapter
        self.logger = ExtensionLoggerAdapter(logger.logger, logger.extra, request.get(consts.ID, ''))

        # Set source request
        self.request = request
        self.logger.debug(json.dumps(self.request, indent=4))

        # Set connect client
        self.client = client

    def handle(self) -> Optional[Union[ProcessingResponse, ValidationResponse, ProductActionResponse]]:
        """
        Handles the request process
        """

        return self.process()

    def process(self):  # pragma: no cover
        pass

    def sync_request(self, **kwargs):
        """
        Sets current value in source request

        :param kwargs: variable-length argument list, keyword arguments:
            status
            reason
            parameters
        """

        if consts.STATUS in kwargs:
            self.request[consts.STATUS] = kwargs.get(consts.STATUS)

        if consts.REASON in kwargs:
            self.request[consts.REASON] = kwargs.get(consts.REASON)

        if consts.PARAMS in kwargs:
            # input params with new values
            input_params = kwargs.get(consts.PARAMS)
            # existing asset params in the request
            request_params = self.request[consts.ASSET][consts.PARAMS]

            for new_param in input_params:
                # search existing param by input param identifier
                param_to_update = next((p for p in request_params if p[consts.ID] == new_param.get(consts.ID)), None)
                if param_to_update:
                    # assigns new values
                    param_to_update[consts.VALUE] = new_param.get(consts.VALUE)
                    param_to_update[consts.VALUE_ERROR] = new_param.get(consts.VALUE_ERROR)
