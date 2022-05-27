# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from configparser import ConfigParser
import playmolecule
import inspect
import logging
import os


logger = logging.getLogger(__name__)


_config = ConfigParser()


def loadConfig():
    if os.getenv("PM_SDK_CONFIG"):
        path = os.environ["PM_SDK_CONFIG"]
    elif os.getenv("SDKCONFIG"):
        path = os.environ["SDKCONFIG"]
    else:
        homeDir = os.path.dirname(inspect.getfile(playmolecule))
        path = os.path.join(homeDir, "config.ini")

    logger.info(f"Reading PM API configuration from {path}")
    _config.read(path)
