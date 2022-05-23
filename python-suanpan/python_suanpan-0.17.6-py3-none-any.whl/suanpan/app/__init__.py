# coding=utf-8
from __future__ import absolute_import, print_function

import typing
from suanpan import g
from suanpan.proxy import Proxy
from suanpan.app.message_handler import MessageHandler

if typing.TYPE_CHECKING:
    from suanpan.stypes import AppT


class App(Proxy):
    MAPPING = {
        "spark": "suanpan.app.spark.SparkApp",
        "docker": "suanpan.app.docker.DockerApp",
        "stream": "suanpan.app.stream.StreamApp",
    }

    @property
    def isSpark(self):
        return self.isType("spark")

    @property
    def isDocker(self):
        return self.isType("docker")

    @property
    def isStream(self):
        return self.isType("stream")

    def isType(self, appType):
        return getattr(self, self.TYPE_KEY, None) == appType


TYPE = g.appType
app: 'AppT' = App(type=TYPE)
