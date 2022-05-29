import tempfile

import diskcache

cache = diskcache.Cache(tempfile.gettempdir() + "/edos_cache")
