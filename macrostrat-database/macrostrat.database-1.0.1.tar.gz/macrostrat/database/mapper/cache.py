from sqlalchemy.ext.automap import automap_base
from os import path, makedirs
from macrostrat.utils.logs import get_logger
from sqlalchemy.ext.automap import automap_base
from pickle import load, dump
from .base import ModelHelperMixins

log = get_logger(__name__)

class AutomapError(Exception):
    pass

class DatabaseModelCache(object):
    cache_file = None

    def __init__(self, cache_file=None):
        self.cache_file = cache_file


    @property
    def _metadata_cache_filename(self):
        return self.cache_file

    # https://stackoverflow.com/questions/41547778/sqlalchemy-automap-best-practices-for-performance/44607512
    def _cache_database_map(self, metadata):
        if self.cache_file is None:
            return
        # save the metadata for future runs
        try:
            cache_dir = path.dirname(self.cache_file)
            if not path.exists(cache_dir):
                makedirs(cache_dir)
            # make sure to open in binary mode - we're writing bytes, not str
            with open(self.cache_file, "wb") as f:
                dump(metadata, f)
            log.info(f"Cached database models to {self.cache_file}")
        except IOError:
            # couldn't write the file for some reason
            log.info(
                f"Could not cache database models to {self.cache_file}"
            )

    def _load_database_map(self):
        # We have hard-coded the cache file for now
        if self.cache_file is None:
            return None
        cached_metadata = None
        try:
            with open(self.cache_file, "rb") as f:
                cached_metadata = load(file=f)

        except (IOError, EOFError):
            # cache file not found - no problem
            log.info(
                f"Could not find database model cache ({self._metadata_cache_filename})"
            )
        return cached_metadata

    def automap_base(self):
        cached_metadata = self._load_database_map()
        if cached_metadata is None:
            base = automap_base(cls=ModelHelperMixins)
        else:
            log.info("Loading database models from cache")
            base = automap_base(metadata=cached_metadata)
            base.loaded_from_cache = True
        base.builder = self
        return base

