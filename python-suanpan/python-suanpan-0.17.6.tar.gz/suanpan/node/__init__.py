# coding=utf-8
from __future__ import absolute_import, print_function

import typing
from suanpan import app
from suanpan.proxy import Proxy

if typing.TYPE_CHECKING:
    from suanpan.stypes import NodeT


class Node(Proxy):
    MAPPING = {
        "spark": "suanpan.node.spark.SparkNode",
        "docker": "suanpan.node.docker.DockerNode",
        "stream": "suanpan.node.stream.StreamNode",
    }


node: 'NodeT' = Node(type=app.TYPE)
