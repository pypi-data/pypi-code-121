# -*- coding: utf-8 -*-
# AristaFlow REST Libraries
from aristaflow.remote_iterator_handler import RemoteIteratorHandler
from aristaflow.service_provider import ServiceProvider


class AbstractService(object):
    """Abstract base class for service helpers"""

    _service_provider: ServiceProvider = None
    _rem_iter_handler: RemoteIteratorHandler = None
    _disconnected: bool = False

    def __init__(self, service_provider: ServiceProvider):
        self._service_provider = service_provider
        self._rem_iter_handler = RemoteIteratorHandler(service_provider)

    def disconnect(self):
        """ Called when the service should disconnect any open connection from the backend. """
        self._disconnected = True
