# -*- coding:utf-8 -*-
# author:jackwu 
# time:2022/5/25
import datetime
import os
import sys


PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_PATH)
from itsdangerous import json
from loguru import logger


def get_logger(task_name):
    logger.add(os.path.join(PROJECT_PATH, "logs", f"{task_name}.log"),
               level='DEBUG',
               format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {line} : {message}',
               rotation="500 MB")
    return logger


def set_pid(pid_key):
    """设置pid"""
    if pid_key:
        pid_dict = get_pid_dict()
        pid_dict[pid_key.lower()] = int(os.getpid())

        with open(os.path.join(PROJECT_PATH, "docs", "pid.json"), "w") as f:
            json.dump(pid_dict, f)
        return True
    else:
        return False

def get_pid_dict():
    with open(os.path.join(PROJECT_PATH, "docs", "pid.json"), "r+") as f:
        pid_dict = json.load(f)
    return pid_dict


def reset_redis_task_status(task_dict, redis_ser, redis_prefix, update_time=True, minutes=120):
    """
    重置redis中任务状态和下次查询时间
    :param task_dict:       当前任务字典
    :param redis_ser:       redis连接对象
    :param redis_prefix:    redis-key 前缀
    :param update_time:     是否更新查询时间
    :param minutes:         下次任务查询间隔时间

    :return:
    """
    task_dict['task_status'] = 0
    if update_time:
        task_dict['next_query_time'] = (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime(
            "%Y-%m-%d %H:%M:%S")
    redis_ser.set(redis_prefix + task_dict['boxNo'], json.dumps(task_dict))


