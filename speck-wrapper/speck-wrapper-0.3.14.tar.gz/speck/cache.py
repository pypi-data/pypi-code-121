"""
Cache utility.
The primary purpose of this is to reduce the number of required API calls.
"""

import os
import sys

import zlib
import pickle

from pathlib import Path

__all__ = [
    'CacheManager',
    'BufferedCacheManager',
    'FileCacheManager'
]

class CacheManager:
    """
    Abstract class representing a cache manager.
    """

    def __init__(self, path):
        pass

    def find_all(self):
        """Find all stored cache."""
        return None

    def read(self, name):
        """Reads cache with ``name`` if it exists."""
        return None

    def dump(self, name, data):
        """Save data into cache."""
        return None

    def cleanup(self, name):
        """Cleanup all cache with a ``name``"""
        return None

    def debug_size(self):
        """Get size of cache for debugging."""
        return sys.getsizeof(self)


class BufferedCacheManager(CacheManager):
    """
    Buffered Cache Manager implementation. Stored cache in memory.
    """

    def __init__(self, path=None):
        self._buf = {}

        super().__init__(path)

    def find_all(self):
        """
        Find all cache stored in memory.

        :rtype: :class:`generator`
        """
        return (i for i in self._buf)

    def read(self, name):
        """Reads cache with ``name`` if it exists."""
        if name in self._buf:
            return pickle.loads(zlib.decompress(self._buf[name]))

        return None

    def dump(self, name, data):
        """Save data into cache."""
        self._buf[name] = zlib.compress(pickle.dumps(data))

    def cleanup(self, name):
        """Cleanup all cache with a ``name``. Supports wildcard (*) deletion."""

        els = name.split('*') # splits across *

        print(els)

        need_remove = []

        for i in self._buf:
            for n, j in enumerate(els):
                if not (
                    j == '' or (j in i and
                        (i.index(j) >= i.index(els[0 if n < 1 else n - 1]))
                        )
                    ):
                    break

                    # Explanation for above check
                    # ---------------------------
                    # `els` is a list of all components split across *.
                    # We check if each component of `else` is in
                    # the cache name being checked (`j in i`).
                    # If the component is empty, we can skip directly.
                    # If it is, we make sure its after the previous
                    # component (second check).
            else:
                need_remove.append(i)

        for i in need_remove:
            del self._buf[i]

    def debug_size(self):
        """
        Get size of internal cache for debugging.

        :returns: Cache size in memory in bytes.
        """
        return sys.getsizeof(self._buf)

class FileCacheManager(CacheManager):
    """
    File based Cache Manager implementation. Keeps track of and gets/updates data from cache files.

    :param path: Path to the "cache directory". Cache files will be stored here.
    """

    def __init__(self, path):
        self._path = path

        super().__init__(path)

        Path(path).mkdir(parents=True, exist_ok=True)  # Creates cache folder

        # Cache is identified with its `name` attribute. Cache can be read by keeping track of this
        # value and reading it with `read` later on.

    @property
    def path(self):
        """
        Returns the directory to which cache files are being stored.

        :rtype: :class:`str`
        """
        return self._path

    def find_all(self):
        """
        Return a list of all tracked cache files.

        :rtype: :class:`generator`
        """
        return (
            ''.join(i.split('.')[:-1]) if i.endswith('.dat') else i
            for i in os.listdir(self._path)
        )

    def read(self, name):
        """Tries to read cache with ``name``. Returns ``None`` if no such file is found."""

        try:
            # Cache is stored as an object in a binary file,
            # which can be loaded into an object directly later on.
            with open(f"{self._path}/{name}.dat", "rb") as f:
                return pickle.loads(zlib.decompress(pickle.load(f)))

        except pickle.PickleError:
            pass
        except FileNotFoundError:
            pass

        return None

    def dump(self, name, data):
        """Writes data to a cache file with ``name``. ``name`` must be kept track of manually."""

        with open(f"{self._path}/{name}.dat", "wb") as f:
            pickle.dump(zlib.compress(pickle.dumps(data)), f)

    def cleanup(self, name):
        """Cleans up all cache files with a given ``name``. Supports wildcard (*) deletion."""

        els = name.split('*')

        try:
            for i in os.listdir(self._path):
                for n, j in enumerate(els):
                    k = ''.join(i.split('.')[:-1]) if i.endswith('.dat') else i
                    if not (
                        j == '' or (j in k and
                            (k.index(j) >= k.index(els[0 if n < 1 else n - 1]))
                            )
                        ):
                        break
                else:
                    os.remove(f"{self._path}/{i}") # Delete the file

        except FileNotFoundError:
            pass
