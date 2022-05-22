#===============================================================================
# check_gpu_availability.py
#===============================================================================

# Imports ======================================================================

import GPUtil
import nvsmi
import psutil
from tabulate import tabulate
from sys import exit
from time import sleep

def format_processes_table(processes):
    """Alternative string representation for a GPU process

    Parameters
    ----------
    processes
        an iterable of GPUprocess objects from nvsmi

    Returns
    -------
    str
        string representation of the processes  table
    """

    headers = ('GPU', 'PID', 'Process Name', 'GPU Memory Usage')
    table = ((p.gpu_id, p.pid, p.process_name,
              f'{int(p.used_memory)/1024:.2f} GB') for p in processes)

    return tabulate(table, headers=headers, tablefmt='rst')


def check_gpu_availability(devices, gpu_load: float = 0.9,
                           gpu_mem: float = 0.9):
    """Check for availability of indicated GPUs. If not available, prompt user
    to free up resources by terminating GPU processes. Terminate execution
    if GPUs are not made available.

    Parameters
    ----------
    devices
        iterable of devices ID's to check for
    gpu_load : float
        minimum GPU load availability (as a fraction of total)
    gpu_mem : float
        minimum GPU memory availability (as a fraction of total)
    """

    gpus=GPUtil.getGPUs()
    if not gpus:
        print('No GPUs found on this machine, terminating.')
        exit()
    available = GPUtil.getAvailable(limit=len(gpus), maxLoad=1-gpu_load,
                                    maxMemory=1-gpu_mem)
    unavailable = tuple(str(d) for d in devices if d not in available)
    if unavailable:
        processes = tuple(p for p in nvsmi.get_gpu_processes()
                    if p.gpu_id in unavailable)
        processes_table = format_processes_table(processes)
        reply = input('Cannot launch because the following processes are '
                    f'occupying resources on device(s) '
                    f'{", ".join(unavailable)}:\n\n{processes_table}\n\n'
                    f'Terminate these processes and continue? [y/N]:')
        if reply.casefold() in {'y', 'yes'}:
            for pid in {p.pid for p in processes}:
                psutil.Process(pid).terminate()
            sleep(4)
            check_gpu_availability(devices, gpu_load=gpu_load, gpu_mem=gpu_mem)
        else:
            print('GPU(s) not available, terminating.')
            exit()
