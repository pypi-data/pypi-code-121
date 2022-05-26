# -*- coding:utf-8 -*-
"""
处理任务工具
"""
import datetime
import os
import sys
import json
import time


PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)
from utils.util_data_interaction import UtilData  # 报错：需自行配置对应接口的请求
from functools import reduce
from hgj_download_center.util.util_common import reset_redis_task_status


class DealTtool(object):
    def __init__(self, task_name, redis_serve, redis_all_prefix, redis_prefix):
        self.task_name = task_name
        self.util_data = UtilData()
        self.redis = redis_serve
        self.redis_all_prefix = redis_all_prefix
        self.redis_prefix = redis_prefix

    def put_dict_and_check(self, task_name_list: list):
        """ 获取新任务存入redis并去重 """
        new_redis_dict = dict()
        new_task_index_list = []  # 存新任务的索引值
        task_list = self.util_data.get_data(task_name_list)
        existing_tasks_index = self.get_existing_all_tasks()

        for task_dict in task_list:
            redis_key = self.redis_prefix + task_dict['boxNo']
            if self.redis.exists(redis_key) == 1:continue
            task_dict['task_status'] = 0
            new_redis_dict[redis_key] = json.dumps(task_dict)
            new_task_index_list.append(redis_key)

        # 批量放入redis
        if len(new_redis_dict.keys()) > 0:
            self.redis.mset(new_redis_dict)

        # 将单个任务索引存表
        if existing_tasks_index is None:
            existing_tasks_index = []
        existing_tasks_index.extend(new_task_index_list)
        func = lambda x, y: x if y in x else x + [y]
        existing_tasks_index = reduce(func, [[], ] + existing_tasks_index)
        self.redis.set(self.redis_all_prefix, json.dumps(existing_tasks_index))

    def get_existing_all_tasks(self, first_send=False) -> list:
        """ 获取redis中指定船司的所有索引"""
        if first_send:
            existing_tasks_index = self.get_existing_all_2()
            self.redis.set(self.redis_all_prefix, json.dumps(existing_tasks_index))
        else:
            existing_tasks_index = self.redis.get(self.redis_all_prefix)
            existing_tasks_index = [] if existing_tasks_index is None else json.loads(existing_tasks_index)
        return existing_tasks_index

    def get_existing_all_2(self, search_num=1000) ->list:
        """ 首次启动脚本需要 模板查询一次"""
        if search_num < 1000: search_num = 1000
        k = 0
        data_list = []
        while True:
            try:
                l = self.redis.scan(k, count=search_num)
                data_list.extend(i for i in l[1] if self.redis_prefix in i)
                k = l[0]
                if k == 0:
                    break
            except:
                break
        return data_list

    def get_redis_keys(self, first_send=False):
        """ 获取redis-keys"""
        existing_tasks_index = self.get_existing_all_tasks(first_send)
        return existing_tasks_index

    def get_sending_redis_tasks(self) -> list:
        """ 获取待发送的任务"""
        keys = self.get_redis_keys()
        redis_tasks = []
        for task_dict in self.redis.mget(keys):
            if type(task_dict) is None or type(task_dict) != str:
                continue
            task_dict = json.loads(task_dict)
            next_query_time = task_dict.get('next_query_time', '')
            if next_query_time:
                next_query_time = datetime.datetime.strptime(next_query_time.replace(' ', 'T'), '%Y-%m-%dT%H:%M:%S')
                if datetime.datetime.now() - datetime.timedelta(hours=2) > next_query_time and task_dict["task_status"] == 1:
                    task_dict["task_status"] = 0
                    self.redis.set(self.redis_prefix + task_dict['boxNo'], json.dumps(task_dict))
            redis_tasks.append(task_dict)
        return redis_tasks

    def update_redis_data(self, task_dict, item, task_name=""):
        """ 更新查询完的数据更新"""
        takeHeavyBoxTime = item.get("takeHeavyBoxTime", "")
        backEmptyBoxTime = item.get("backEmptyBoxTime", "")
        new_task_dict = dict(task_dict, **item)
        self.util_data.reply_res(new_task_dict)  # 先返回数据
        if task_name in ["ial", "kkc"] and not takeHeavyBoxTime:
            reset_redis_task_status(new_task_dict, self.redis, self.redis_prefix, )
        elif task_name == "" and not backEmptyBoxTime:
            reset_redis_task_status(new_task_dict, self.redis, self.redis_prefix, )
        else:
            self.send_res(new_task_dict)
            self.redis.delete(self.redis_prefix + task_dict['boxNo'])
            self.update_redis_index(task_dict)

    def update_redis_index(self, task_dict):
        """ 更新redis索引相关"""
        existing_tasks_index = self.get_existing_all_tasks()
        redis_key = self.redis_prefix + task_dict['boxNo']
        try:
            existing_tasks_index.remove(redis_key)
        except:
            pass
        self.redis.set(self.redis_all_prefix, json.dumps(existing_tasks_index))

    def send_res(self, callback_data):
        """发送已标记的回执"""
        self.util_data.destination_refuse(callback_data)

    def check_redis_data(self):
        """ 程序启动 重置所有任务状态"""
        keys = self.get_redis_keys(first_send=True)
        redis_tasks = [json.loads(i) for i in self.redis.mget(keys)]
        for task_dict in redis_tasks:
            redis_key = self.redis_prefix + task_dict['boxNo']
            if task_dict['task_status'] != 0:
                task_dict['task_status'] = 0
                self.redis.set(redis_key, json.dumps(task_dict))
                time.sleep(0.5)

    def update_error_data(self, task_dict):
        search_flag = True
        next_query_time = task_dict.get('next_query_time', '')
        if task_dict['task_status'] != 0 and (
                next_query_time == '' or datetime.datetime.strptime(task_dict['next_query_time'],"%Y-%m-%d %H:%M:%S") <= datetime.datetime.now()):
            task_dict['task_status'] = 0
            self.redis.set(self.redis_prefix + task_dict['boxNo'], json.dumps(task_dict))
        elif task_dict['task_status'] == 0 and (next_query_time == ''
            or datetime.datetime.strptime(task_dict['next_query_time'], "%Y-%m-%d %H:%M:%S") > datetime.datetime.now()):
            search_flag = False
        return search_flag
