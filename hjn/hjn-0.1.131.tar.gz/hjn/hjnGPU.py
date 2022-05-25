from gpuinfo import GPUInfo
import numpy as np
import time

def findGPU(waitS=2):
    """get ID of GPUS
    :param num_gpu:  num of GPUs to use
    :return: gpu_id: ID of allocated GPUs
    """
    gpu_id = None
    waitSec = np.random.uniform(0,waitS)
    time.sleep(waitSec)
    available_device=GPUInfo.check_empty()
    if not available_device is None:
        if len(available_device)>0:
            idx = np.random.randint(0,len(available_device))
            gpu_id=available_device[idx]

    return gpu_id


