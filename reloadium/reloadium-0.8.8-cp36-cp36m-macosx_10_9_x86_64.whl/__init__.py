# flake8: noqa E402, F401
from reloadium.__utils__ import pre_import_check

pre_import_check()

from reloadium.reloader import start as reloader_start
from reloadium.reloader.config import BaseConfig
from reloadium.reloader.public import *

__author__ = "Damian Krystkiewicz"
__company__ = "Reloadware"
__copyright__ = "Copyright (C) 2022 Reloadware"  # RwRender: __copyright__ = "Copyright (C) {{ ctx.year }} Reloadware"
__stage__ = "prod"  # RwRender: __stage__ = "{{ ctx.stage }}"
__license__ = "Apache 2.0"


def start():
    import sys

    reloader_start(sys.argv)
