# coding: utf-8
# Default Python Libraries
from typing import List, Type

# AristaFlow REST Libraries
from aristaflow.service_provider import ServiceProvider


class RemoteIteratorHandler(object):
    """
    Utilities for handling remote iterators
    """

    _service_provider: ServiceProvider = None

    def __init__(self, service_provider: ServiceProvider):
        """
        Constructor
        """
        self._service_provider = service_provider

    def _consume(self, target: List, iterator_data, attrib_name: str, iter_api, iter_api_method):
        if iterator_data is None:
            return
        if getattr(iterator_data, attrib_name):
            target += getattr(iterator_data, attrib_name)
        else:
            # no data left, end recursion
            return
        if iterator_data.dropped:
            return

        next_iter = iter_api_method(iter_api, iterator_data.iterator_id)
        self._consume(target, next_iter, attrib_name, iter_api_method)

    def consume(
        self, iterator_data, attrib_name: str, iter_api_type: Type, iter_api_method=None
    ) -> List:
        iter_api = self._service_provider.get_service(iter_api_type)
        if iter_api_method is None:
            iter_api_method = getattr(iter_api_type, "get_next")
        target = []
        self._consume(target, iterator_data, attrib_name, iter_api, iter_api_method)
        return target
