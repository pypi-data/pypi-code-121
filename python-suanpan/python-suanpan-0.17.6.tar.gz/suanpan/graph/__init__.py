# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.proxy import Proxy


class Graph(Proxy):
    DEFAULT_TYPE = "default"
    MAPPING = {
        "default": "suanpan.graph.base.Graph",
    }


graph = Graph()
