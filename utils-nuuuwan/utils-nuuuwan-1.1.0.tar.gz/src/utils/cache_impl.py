"""Utils for caching functions."""
import json
import os
import threading
import time

from utils import filex, hashx, jsonx

DEFAULT_TIMEOUT = 60
DEFAULT_DIR = '/tmp/cache'
DEFAULT_CACHE_NAME = 'new_cache'


class _Cache:
    """Implements base cache logic."""

    __store = {}
    __lock_map_lock = threading.Lock()
    __lock_map = {}

    __dir = DEFAULT_DIR
    __cache_name = DEFAULT_CACHE_NAME
    __timeout = DEFAULT_TIMEOUT

    def __init__(
        self,
        cache_name=None,
        timeout=None,
        dir=None,
    ):
        """Implement class constructor."""
        if cache_name is not None:
            self.__cache_name = cache_name
        if timeout is not None:
            self.__timeout = timeout
        if dir is not None:
            self.__dir = dir

        os.system('mkdir -p %s' % self.__get_dir())

    def __get_dir(self):
        return '%s/%s' % (self.__dir, self.__cache_name)

    def __get_lock(self, key):
        # pylint: disable=R1732
        self.__lock_map_lock.acquire()
        if key not in self.__lock_map:
            self.__lock_map[key] = threading.Lock()
        lock = self.__lock_map[key]
        self.__lock_map_lock.release()
        return lock

    def __acquire_lock(self, key):
        self.__get_lock(key).acquire()

    def __release_lock(self, key):
        self.__get_lock(key).release()

    def __get_cache_file_name(self, cache_key):
        return '%s/%s' % (self.__get_dir(), hashx.md5(cache_key))

    def __get_file_exists(self, key):
        return os.path.exists(self.__get_cache_file_name(key))

    def __get_from_file(self, key):
        data_json = filex.read(self.__get_cache_file_name(key))
        if data_json == '':
            return None
        packet = json.loads(data_json)
        return packet

    def __set(self, key, data):
        self.__acquire_lock(key)
        packet = {'data': jsonx.serialize(data), 'set_time': time.time()}
        filex.write(
            self.__get_cache_file_name(key),
            json.dumps(packet, ensure_ascii=True),
        )
        self.__store[key] = packet
        self.__release_lock(key)

    def get(self, key_or_list, fallback):
        """Get data from cache if cache key exists, if not from fallback."""
        if isinstance(key_or_list, list):
            key = ':'.join(key_or_list)
        else:
            key = key_or_list

        packet = None
        if key in self.__store:
            packet = self.__store[key]

        if not packet:
            if self.__get_file_exists(key):
                packet = self.__get_from_file(key)
                if packet is not None:
                    self.__store[key] = packet

        if packet:
            if 'set_time' in packet:
                min_set_time = time.time() - self.__timeout
                if packet['set_time'] > min_set_time:
                    return jsonx.deserialize(packet['data'])

        data = fallback()
        if data is not None:
            self.__set(key, data)
        return data
