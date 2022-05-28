import json
import logging


class Cache:
    _CACHE_BASE_PATH = '/tmp'

    _LOGGER = logging.getLogger()
    _LOGGER.setLevel(logging.INFO)

    def __init__(self, name):
        self._cache_path = f"{self._CACHE_BASE_PATH}/{name}.json"
        try:
            with open(self._cache_path) as cache_file:
                self.cache = json.load(cache_file)
        except IOError:
            self._LOGGER.info("No cache available. Creating empty one.")
            self.cache = {}

    @property
    def cache_path(self):
        return self._cache_path

    def get_all(self):
        return self.cache

    def set_all(self, keys_with_values):
        for key in keys_with_values:
            self.set(key, keys_with_values[key])

    def get(self, key):
        return self.cache.get(key, None)

    def set(self, key, value):
        self.cache[key] = value
        with open(self._cache_path, 'w') as cache_file:
            json.dump(self.cache, cache_file)

    def delete_all(self):
        self.cache = {}
        with open(self._cache_path, 'w') as cache_file:
            json.dump(self.cache, cache_file)
