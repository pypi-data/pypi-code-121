import numpy as np
import time
import os
import subprocess

def callscript(*args, **kwargs):
    cmd = kwargs['command']
    if 'argument' in kwargs.keys():
        cmd = cmd + " " + str(kwargs['argument'])
    os.system(cmd)
    return 'Done!!! '


def printrun(*args):
    result = []
    for arg in args:
        if isinstance(arg, list) and len(arg) == 1:
            result.append(arg[0])
        else:
            result.append(arg)
    if len(result) == 1:
        result = result[0]
    print(result)
    return result


def MERGE(**kwargs):
    dic_merged = {}
    for key, value in kwargs.items():
        if isinstance(value, np.number):
            value = float(value)
        else:
            value = value
    return (kwargs)   


def flat_tuple(lazy_tuple, return_number):
    flat_list = []
    for i in range(return_number):
        flat_list.append([])
    for i in range(return_number):       
        for j in range(len(lazy_tuple)):    
            for item in lazy_tuple[j][i]:  
                flat_list[return_number- (i + 1)].append(item)
    return flat_list


def flat_list(lazy_list):
    flat_list = []
    for list in lazy_list:
            for item in list:
                flat_list.append(item)
    return flat_list


def wfgenes_argparser(args):

    """ Check if the arguments are provided from the command-line. 
    If there is no command-line value for any argument, it will be loaded from WConfig"""
    resource = {}        
    resource['pool'] = args.pool 
    if resource['pool'] == 'local_threads':
        resource['threads_number'] = args.threads_number
    elif resource['pool'] == 'slurm':
        resource['cpu_per_node']  = args.cpu_per_node     
        resource['scale'] = args.scale     
        resource['worker_per_node'] = args.worker_per_node     
        resource['memory'] = args.memory     
        resource['partition'] = args.partition      
        resource['walltime'] = args.walltime    
    elif resource['pool'] == 'local_processes':
        resource['processes_number'] = args.processes_number 
        resource['cpu_per_process'] = args.cpu_per_process
    
    return resource

        
def transfer_files(user, host, filespath, launchdir, subfolder='', path_type='PYTHONPATH'):
    """ Transfer a list of file in the given path """
    space = ' '
    ssh_link = user + '@' + host + ':'
    subfolder_path = os.path.join(launchdir, subfolder)
    env_path = 'export ' + path_type + '=$' + path_type + ':' + subfolder_path
    rsync_cmd = "rsync -a --rsync-path='mkdir -p"
    rsync_cmd += space + subfolder_path + space
    rsync_cmd += "&& rsync'" + space
    if len(filespath) != 0:
        for path in filespath:
            if path.selected_path is not None:
                rsync_extend = ''
                if not path.selected_filename:
                    rsync_extend = rsync_cmd
                    rsync_extend += "-rv" + space
                    rsync_extend += path.selected_path + '/*' + space
                    rsync_extend += ssh_link
                    rsync_extend += subfolder_path
                    print(rsync_extend)
                    proc = subprocess.call(rsync_extend, shell=True)
                else:
                    rsync_extend = rsync_cmd
                    rsync_extend += "-v" + space
                    rsync_extend += path.selected + space
                    rsync_extend += ssh_link
                    rsync_extend += subfolder_path
                    print(rsync_extend)
                    proc = subprocess.call(rsync_extend, shell=True)
    return env_path


        
