import os
import resource
import psutil
import time
import logging

logger = logging.getLogger("app")


def set_limits_memory(params={}):

    # Default fraction of max memory to be used
    fraction = params.get("memory", 0.8)

    # Get available virtual memory
    vmem = psutil.virtual_memory()

    max_vmem = int(fraction * vmem.available)

    # use AS as alternative to VMEM if the attribute isn't defined.
    # http://stackoverflow.com/a/30269998/5731870
    if hasattr(resource, "RLIMIT_VMEM"):
        resource.setrlimit(resource.RLIMIT_VMEM, (max_vmem, max_vmem))
    elif hasattr(resource, "RLIMIT_AS"):
        resource.setrlimit(resource.RLIMIT_AS, (max_vmem, max_vmem))

    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    soft = round(soft / (1.0 * 1024 * 1024))
    hard = round(hard / (1.0 * 1024 * 1024))

    return "Memory: Soft ({}MB) Hard ({}MB)".format(soft, hard)


def set_limits(params={}):
    msg = set_limits_memory(params)

    logger.debug("Resource Limits set", extra={"transform": "Enricher", "data": msg})


def clear_cache():
    """
    https://www.thegeekdiary.com/how-to-clear-the-buffer-pagecache-disk-cache-under-linux/
    """
    os.system("sudo /bin/bash -c 'echo 1 > /proc/sys/vm/drop_caches'")


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    set_limits({"memory": 0.8})
