# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.app.modules.base import Module, Modules
from suanpan.app.modules.core import module as core
from suanpan.app.modules.front import module as front
from suanpan.app.modules.images import module as images
from suanpan.app.modules.node import module as node
from suanpan.app.modules.params import module as params
from suanpan.app.modules.storage import module as storage

modules = Modules()
modules.register("core", core)
modules.register("node", node)
modules.register("front", front)
modules.register("params", params)
modules.register("images", images, enable=False)
modules.register("storage", storage, enable=False)
