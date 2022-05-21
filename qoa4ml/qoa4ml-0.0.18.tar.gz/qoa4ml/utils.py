from concurrent.futures import thread
import json, psutil, time
from qoa4ml.reports import Qoa_Client
from threading import Thread

def load_config(file_path:str)->dict:
    """
    file_path: file path to load config
    """
    with open(file_path, "r") as f:
        return json.load(f)

def to_json(file_path:str, conf:dict):
    """
    file_path: file path to save config
    """
    with open(file_path, "w") as f:
        json.dump(conf, f)
    
def get_cpu(key:str = None):
    if key == "cpu time":
        return psutil.cpu_times().user
    if key == "percentage":
        pass
    return psutil.cpu_percent()

def get_mem(key:str = None):
    if key == "percentage":
        return psutil.virtual_memory().percent
    if key == "free":
        return psutil.virtual_memory().free
    if key == "total":
        return psutil.virtual_memory().total
    if key == "active":
        return psutil.virtual_memory().active
    if key == "available":
        return psutil.virtual_memory().available
    if key == "used":
        pass
    return psutil.virtual_memory().used


sys_monitor_flag = False

def system_report(client:Qoa_Client, metrics: dict, interval:int):
    client.add_metric(metrics['cpu_stat'])
    client.add_metric(metrics['mem_stat'])
    metric_list = []
    while sys_monitor_flag:
        for metric_name in metrics['cpu_stat']:
            metric = client.get_metric(metric_name)
            metric.set(get_cpu(metrics['cpu_stat'][metric_name]["key"]))
            metric_list.append(metric_name)
        for metric_name in metrics['mem_stat']:
            metric = client.get_metric(metric_name)
            metric.set(get_mem(metrics['mem_stat'][metric_name]["key"]))
            metric_list.append(metric_name)
        client.report(metrics=metric_list)
        time.sleep(interval)


def sys_monitor(client:Qoa_Client, metrics: dict, interval:int):
    sub_thread = Thread(target=system_report, args=(client, metrics, interval))
    sub_thread.start()
