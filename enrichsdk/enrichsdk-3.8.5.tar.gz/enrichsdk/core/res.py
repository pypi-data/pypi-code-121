import psutil
import resource
import logging
import platform

logger = logging.getLogger("app")


def set_limits_memory(params={}):

    # Default fraction of max memory to be used
    fraction = params.get("memory", 0.8)

    # Get available virtual memory
    vmem = psutil.virtual_memory()

    max_vmem = int(fraction * vmem.available)

    opsys = platform.system()
    release = int(platform.release().split('.')[0])

    # use AS as alternative to VMEM if the attribute isn't defined.
    # http://stackoverflow.com/a/30269998/5731870
    if hasattr(resource, "RLIMIT_VMEM"):
        resource.setrlimit(resource.RLIMIT_VMEM, (max_vmem, max_vmem))
    elif hasattr(resource, "RLIMIT_AS"):
        if opsys == 'Darwin' and release >= 21:
            # MacOS Monterey or higher
            # the setrlimit does not work
            pass
        else:
            resource.setrlimit(resource.RLIMIT_AS, (max_vmem, max_vmem))

    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    soft = round(soft / (1.0 * 1024 * 1024))
    hard = round(hard / (1.0 * 1024 * 1024))

    return "Memory: Soft ({}MB) Hard ({}MB)".format(soft, hard)


def set_limits(params={}):
    msg = set_limits_memory(params)

    logger.debug("Resource Limits set", extra={"transform": "Enricher", "data": msg})
