"""
Blow out logs fire back-ends.

Authors:
    Dmitry Parfyonov <parfyonov.dima@gmail.com>
"""

# import

import os
import sys
import time
from typing import List

try:
    from pymemcache.client import hash as memcache
except ImportError:
    memcache = None

# Blowout

class Blowout(object):

    def get_timeout(self, handler_id: str, blowout_seconds: float) -> float:
        """
        Get timeout.
        Args:
            handler_id:
            blowout_seconds:
        """
        raise NotImplementedError()

    def set_timeout(self, handler_id: str, blowout_seconds: float):
        """
        Set timeout.
        Args:
            handler_id:
            blowout_seconds:
        """
        raise NotImplementedError()

    def can_emit(self, handler_id: str, blowout_seconds: float) -> bool:
        """
        Can emit record.
        Args:
            handler_id: log handler id
            blowout_seconds: mute period
        """
        timeout = self.get_timeout(handler_id, blowout_seconds)

        if timeout == 0 or timeout < time.time():
            self.set_timeout(handler_id, blowout_seconds)

            return True

        return False

# BlowoutProcess

class BlowoutProcess(Blowout):

    def __init__(self):
        super(BlowoutProcess, self).__init__()
        self.emissions = {}

    def get_timeout(self, handler_id: int, blowout_seconds: float) -> float:
        """
        Get timeout.
        Args:
            handler_id:
            blowout_seconds:
        """
        return self.emissions.get(handler_id, 0)

    def set_timeout(self, handler_id: int, blowout_seconds: float):
        """
        Set timeout.
        Args:
            handler_id:
            blowout_seconds:
        """
        self.emissions[handler_id] = time.time() + blowout_seconds

# BlowoutFile

class BlowoutFile(Blowout):
    def __init__(self, path: str or None = None):
        """
        Init.
        Args:
            path: file path
        """
        super(BlowoutFile, self).__init__()
        if path is None:
            if sys.platform.startswith('linux'):  # linux
                self.path = '/run/lock/logifire'   # RAM in linux
            else:  # other os
                self.path = '/tmp/logifire'
        else:
            self.path = path

        self.__handlers_ids = set()

    def get_filename(self, handler_id: str) -> str:
        """
        Get filename.
        Args:
            handler_id: int
        """
        return "{}.{}".format(self.path, handler_id)

    def get_timeout(self, handler_id: str, blowout_seconds: float) -> float:
        """
        Get timeout.
        Args:
            handler_id:
            blowout_seconds:
        """
        try:
            mtime = os.stat(self.get_filename(handler_id)).st_mtime + float(blowout_seconds)
        except OSError:
            mtime = 0

        return mtime

    def set_timeout(self, handler_id: str, blowout_seconds: float):
        """
        Set timeout.
        Args:
            handler_id:
            blowout_seconds:
        """
        self.__handlers_ids.add(handler_id)

        open(self.get_filename(handler_id), 'w').close()

# BlowoutMemcached

class BlowoutMemcached(Blowout):
    def __init__(self, servers: List[str] or None = None, client_config: dict or None = None):
        """
        Init.
        Args:
            servers: memcached servers
            client_config: memcached client config
        """
        assert memcache is not None, "module \"pymemcache\" is required"

        super(BlowoutMemcached, self).__init__()

        default_client_config = dict(
            key_prefix=b'logifire.',
            no_delay=True,
            use_pooling=True,
            max_pool_size=10
        )
        if client_config:
            default_client_config.update(client_config)

        default_client_config['default_noreply'] = False  # required

        self.__client = memcache.HashClient(servers or [('127.0.0.1', 11211)], **default_client_config)

    def get_timeout(self, handler_id: str, blowout_seconds: float) -> float:
        """
        Get timeout.
        Args:
            handler_id:
            blowout_seconds:
        """
        return 0

    def set_timeout(self, handler_id: str, blowout_seconds: float):
        """
        Set timeout.
        Args:
            handler_id:
            blowout_seconds:
        """
        pass

    def can_emit(self, handler_id: str, blowout_seconds: float) -> bool:
        """
        Can emit record.
        Args:
            handler_id: log handler id
            blowout_seconds: mute period
        """
        ms = 1 if blowout_seconds < 1 else int(blowout_seconds)

        return self.__client.add(handler_id, '1', expire=ms)
