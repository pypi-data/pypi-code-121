import logging


logger = logging.getLogger(__name__)


def ensurelist(tocheck, tomod=None):
    """Convert numpy ndarray and scalars to lists.

    Lists and tuples are left as is. If a second argument is given,
    the type check is performed on the first argument, and the second argument is converted.
    """
    if tomod is None:
        tomod = tocheck
    if type(tocheck).__name__ == "ndarray":
        return list(tomod)
    if isinstance(tocheck, range):
        return list(tocheck)
    if not isinstance(tocheck, list) and not isinstance(tocheck, tuple):
        return [
            tomod,
        ]
    return tomod


def _getCPUdevices():
    import psutil

    return psutil.cpu_count()


def _getGPUdevices():
    from subprocess import check_output

    logger.info("Trying to determine all GPU devices")
    try:
        check_output("nvidia-smi -L", shell=True)
        ngpu = check_output("nvidia-smi -L | wc -l", shell=True).decode("ascii")
        devices = range(int(ngpu))
    except:
        raise
    return devices


def _getVisibleGPUdevices():
    import os

    visible_devices = os.getenv("CUDA_VISIBLE_DEVICES")
    if visible_devices is not None:
        visible_devices = [int(v) for v in visible_devices.split(",")]
    return visible_devices


def _filterVisibleGPUdevices(devices, _logger):
    visible_devices = _getVisibleGPUdevices()
    if visible_devices is not None:
        if _logger:
            logger.info("GPU devices requested: {}".format(",".join(map(str, devices))))
            logger.info(
                "GPU devices visible: {}".format(",".join(map(str, visible_devices)))
            )
        # Only keep the selected visible devices. intersect of the two lists
        devices = [dd for dd in devices if dd in visible_devices]
    return devices
