#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import traceback
import signal
import psutil

from . import idbUtil
from .appMonitor import app_monitor
from logzero import logger

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

device_captrue_pro = {}

data_colunms = {'android':['time','app_cpu','total_cpu','memory','native_mem','dalvik_mem','total_traffic','traffic_up',
                       'traffic_down','gpu','threads','virtual_mem','activity','fps','wakeups'],
                'ios':['time','app_cpu','total_cpu','memory','native_mem','dalvik_mem','total_traffic','traffic_up',
                       'traffic_down','gpu','threads','virtual_mem','activity','fps','mediasvrd_cpu','wakeups']
                }

class DeviceCaptrueInfo(object):
    def __init__(self,device,platform,monitor,file_name,offset=0):
        self.device = device
        self.platform = platform
        self.monitor_process = monitor
        self.perf_file_name = file_name
        self.read_offset = offset
        self.perf_file_handler = None

def start_captrue(platform,device,package):
    try:
        if device in device_captrue_pro:
            logger.info("设备【%s】已存在采集进程，不能重复开启采集",device)
            return False
        folder = os.path.join(os.environ['HOME'],"perftool")
        cur_floder = os.path.join(folder,time.strftime("%Y-%m-%d", time.localtime(time.time())))
        file_name = "%s_%s"%( package,time.strftime("%Y-%m-%d_%H%M%S", time.localtime(time.time())) )
        cur_floder = os.path.join(cur_floder,file_name)
        os.makedirs(cur_floder,exist_ok=True)
        perf_file_name = os.path.join(cur_floder,file_name+".csv")
        logger.info("device=%s package=%s",device,package)
        logger.info("性能数据保存路径：%s",perf_file_name)
        monitor = None
        if platform=="android":
            monitor = app_monitor(1,perf_file_name,package,device,3600*6)
            monitor.setDaemon(True)
            monitor.start()
        elif platform=='ios':
            pid,process_name = idbUtil.getapp_pid(device,package)
            cmd = f'"{sys.executable}" "{os.path.join(ROOT_DIR,"ios_monitor.py")}" -filename "{perf_file_name}" ' \
                  f'-time {3600*6} -process {process_name} -udid {device} -bundle_id {package}'
            logger.info('启动ios_monitor采集性能数据:%s' % (cmd))
            logFile = open(os.path.join(cur_floder,"py_ios_device.log"), 'w+', encoding='utf-8')
            monitor = subprocess.Popen(cmd,stdout=logFile, stderr=logFile,shell=True)
        device_captrue_pro[device] = DeviceCaptrueInfo(device,platform,monitor,perf_file_name)
        return True
    except Exception as e:
        logger.error("start captrue got error:%s",traceback.format_exc())
        return False

def stop_all():
    for device in device_captrue_pro.keys():
        stop_captrue(device)
        
def stop_captrue(device):
    try:
        if device in device_captrue_pro:
            dcinfo = device_captrue_pro[device]
            if dcinfo.perf_file_handler:
                dcinfo.perf_file_handler.close()
            logger.info("停止采集进程：%s ",device)
            if dcinfo.platform=='android':
                dcinfo.monitor_process.stop()
                dcinfo.monitor_process.join(30)
            elif dcinfo.platform=='ios':
                if os.name == "nt":
                    dcinfo.monitor_process.terminate()
                else:
                    try:
                        dcinfo.monitor_process.send_signal(signal.SIGINT)
                    except Exception as e:
                        logger.error(f"采集进程退出异常 {str(e)}")
                try:
                    kill_proc_tree(dcinfo.monitor_process.pid, sig=signal.SIGINT)
                except Exception as e:
                    logger.info(str(e))
            del device_captrue_pro[device]
    except Exception as e:
        logger.error("stop_captrue got error:%s",traceback.format_exc())

def wait_file_exists(file_name):
    st = time.time()
    while os.path.exists(file_name) is False and time.time()-st<120:
        time.sleep(3)

def read_perf_data(device):
    result = []
    try:
        if device not in device_captrue_pro:
            logger.info("设备【%s】还没有开始采集",device)
            return result
        dcinfo = device_captrue_pro[device]
        if dcinfo.perf_file_handler is None:
            wait_file_exists(dcinfo.perf_file_name)
            dcinfo.perf_file_handler = open(dcinfo.perf_file_name,mode='r',encoding='utf-8')
        dcinfo.perf_file_handler.seek(dcinfo.read_offset)
        data = dcinfo.perf_file_handler.read()
        data_lines = data.splitlines()
        for line in data_lines:
            columns = data_colunms[dcinfo.platform]
            if line.startswith("TimeStamp") or len(line.split(','))!=len(columns):
                continue
            result.append(dict(zip(columns,line.split(','))))
        dcinfo.read_offset += len(data)
    except Exception as e:
        logger.error("read_perf_data got error:%s",traceback.format_exc())
    return result

def get_perf_file_name(device):
    if device in device_captrue_pro:
        return device_captrue_pro[device].perf_file_name
    return None

def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    if psutil.pid_exists(pid) is False:
        return
    if pid == os.getpid():
        return
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return (gone, alive)
