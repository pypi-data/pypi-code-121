# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: October 15th 2021 13:47:00 pm
'''

import logging
from threading import Lock

LOG_FORMAT = '%(asctime)s %(levelname)-7s %(name)s - %(message)s'


class BaseSyncLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.INFO):
        super().__init__(name, level)
        self.lock = Lock()

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        with self.lock:
            super()._log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)


logging.setLoggerClass(BaseSyncLogger)
logging.basicConfig(format=LOG_FORMAT)
