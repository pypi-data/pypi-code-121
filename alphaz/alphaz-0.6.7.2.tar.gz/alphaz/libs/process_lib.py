import os, psutil, datetime, time

from core import core

from alphaz.libs import io_lib

def get_process_informations_filepath(log):
    output_directory    = core.config.get('directories/data')
    if output_directory is None:
        log.error('Missing <directories/data> path in configuration')
        exit()

    output_filepath     = output_directory + os.sep + 'monitor'
    return output_filepath

def set_process_informations(name, log, infos: dict = {}):
    pid                 = os.getpid()
    
    output_filepath     = get_process_informations_filepath(log)

    processes_infos     = get_process_memory_informations(name,log)
    if processes_infos is None:
        processes_infos = {}

    if is_process_running(name,log):
        log.error('Process name=%s and pid=%s is already running'%(name,processes_infos['pid']))
        exit()
    
    processes_infos[name] = infos
    processes_infos[name]['pid'] = pid
    processes_infos[name]['started'] = datetime.datetime.now()

    io_lib.archive_object(processes_infos,output_filepath)

def get_process_memory_informations(name,log):
    output_filepath     = get_process_informations_filepath(log)
    processes_infos     = io_lib.unarchive_object(output_filepath)
    if processes_infos is None or name not in processes_infos:
        return None
    return processes_infos[name]

def get_process_informations(pid):
    for proc in psutil.process_iter():
        # Get process detail as dictionary
        pInfoDict = proc.as_dict(attrs=['pid', 'memory_percent', 'name', 'cpu_times', 'create_time', 'memory_info'])

        if pInfoDict['pid'] == pid:
            return pInfoDict
    return None

def is_process_running(name,log):
    processes_infos         = get_process_memory_informations(name,log)

    if processes_infos is not None and 'pid' in processes_infos:
        memory_pid          = processes_infos['pid']
        current_pid_infos   = get_process_informations(memory_pid)

        if current_pid_infos is not None and current_pid_infos['pid'] == memory_pid:
            return True
    return False

def kill_process(name,log,timeout=15):
    processes_infos         = get_process_memory_informations(name,log)

    if processes_infos is not None and 'pid' in processes_infos:
        memory_pid          = processes_infos['pid']

        killed = False
        for proc in psutil.process_iter():
            pInfoDict = proc.as_dict(attrs=['pid', 'memory_percent', 'name', 'cpu_times', 'create_time', 'memory_info'])

            if pInfoDict['pid'] == memory_pid:
                proc.kill()
                killed = True

        if killed:
            if not is_process_running(name,log):
                time.sleep(timeout)
            return is_process_running(name,log)
    return False