# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api.dtm_pb2 import RouteCoverage as RouteDtm
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class Route(object):
    """
    Wrapper around api.dtm_pb2.RouteCoverage
    """

    def __init__(self, verb, url, route):
        self.verb = verb or "GET"
        self.url = url or ""
        self.signature = route or ""

    def to_dtm(self):
        route = RouteDtm()
        route.verb = self.verb
        route.url = self.url
        route.route = self.signature
        return route

    def to_json(self):
        return {
            "signature": self.signature,
            "verb": self.verb,
            "url": self.url,
        }
