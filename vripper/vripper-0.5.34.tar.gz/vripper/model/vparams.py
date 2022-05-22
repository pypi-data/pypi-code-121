import multiprocessing
import sys

from vripper.enum.processingpriority import ProcessingPriority


def _pop(d, k, default=None):
    if k in d:
        return d.pop(k)
    return default


class VParams:
    def __init__(self, params):
        self.dl_threadpool_size = _pop(params, "download_threadpool_size", 5)
        self.pp_pool_size = _pop(params, "processing_pool_size", 0)
        self.max_dimension = _pop(params, "max_dimension")
        self.min_dimension = _pop(params, "min_dimension", 0)
        self.priority = _pop(params, "processing_priority", ProcessingPriority.SMALLER_FILESIZE)
        self.quality = _pop(params, "compression_quality", 65)
        self.min_filecount = _pop(params, "min_filecount", 1)
        self.max_filecount = _pop(params, "max_filecount")
        self.max_filesize = _pop(params, "max_filesize", sys.maxsize)
        self.min_filesize = _pop(params, "min_filesize", 0)
        self.acceptable_filesize = _pop(params, "acceptable_filesize")
        self.min_hitrate = _pop(params, "min_hitrate", .85)
        self.download_connect_timeout = _pop(params, "download_connect_timeout", 1)
        self.download_read_timeout = _pop(params, "download_read_timeout", 10)

        if len(params) > 0:
            excessive_keys = ",".join([k for k in params])
            raise ValueError(f"Unknown parameters: {excessive_keys}")

        assert self.dl_threadpool_size > 0
        assert self.pp_pool_size >= 0

    @property
    def is_postprocessing_enabled(self):
        return (not not self.max_dimension) or (not not self.quality)
