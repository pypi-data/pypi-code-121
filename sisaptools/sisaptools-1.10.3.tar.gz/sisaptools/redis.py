# -*- coding: utf8 -*-

"""
Eines per a la connexió a Redis.
"""

from __future__ import absolute_import
import redis

from .constants import APP_CHARSET, IS_PYTHON_3
from .services import REDIS_INSTANCES


class Redis(redis.StrictRedis):
    """
    Modificació de StrictRedis per poder instanciar de
    forma transparent segons la versió de l'intèrpret.
    """

    def __init__(self, alias):
        redis.StrictRedis.__init__(
            self,
            host=REDIS_INSTANCES[alias]['host'],
            port=REDIS_INSTANCES[alias]['port'],
            encoding=APP_CHARSET,
            decode_responses=IS_PYTHON_3
        )
