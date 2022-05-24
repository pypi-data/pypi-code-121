# -*- coding: utf-8 -*-
# Default Python Libraries
from typing import Type

# AristaFlow REST Libraries
from af_execution_manager.api.arista_flow_service_api import AristaFlowServiceApi
from aristaflow.service_provider import ServiceProvider


class SseHelper(object):
    """
    Helper for using Server Sent Events.
    """

    _service_provider: ServiceProvider = None

    def __init__(self, service_provider: ServiceProvider):
        """
        Constructor
        """
        self._service_provider = service_provider

    def register(self, api_klass: Type):
        afs: AristaFlowServiceApi = self._service_provider.get_arista_flow_service_api(api_klass)
        afs.register_sse()
