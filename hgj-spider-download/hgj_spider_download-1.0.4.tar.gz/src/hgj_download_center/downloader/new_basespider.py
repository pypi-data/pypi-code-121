# -*- coding:utf-8 -*-
# author:jackwu 
# time:2022/5/18
# des: requests 工具类
import os
import sys
import time
import traceback
import requests

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)

from datetime import datetime
from queue import Queue
from queue import Empty
from threading import Thread
from hgj_download_center.downloader.downloader import Downloader
from hgj_download_center.store.py_store_redis_pool import StoreRedislPool
from hgj_download_center.util.util_common import get_logger, set_pid
from hgj_download_center.util.util_retry import retry
from hgj_download_center.util.util_useragent import UtilUseragent
from utils.config import REDIS_CONFIG  #  报错：需自行导入Redis配置
from hgj_download_center.util.util_deal_tool import DealTtool
from prettytable import PrettyTable


class NewBaseSpider(object):
    def __init__(self, task_name, use_redis=True, env=None, carrier_account=None):
        """
        基本的爬虫类,由队列控制；
        发送的对象统一封装成SpiderRequest对象
        启动时，通过start_requests方法构造一批待发送的任务对象送到待发送队列里面
        :param task_name:                   任务名称
        :param use_redis:                   是否使用redis
        :param env:                         开发环境
        :param carrier_account:             账号密码管理
        """
        self.task_name = task_name.lower()
        self.use_redis = use_redis
        if use_redis:
            self.redis = StoreRedislPool(REDIS_CONFIG).redis
            self.redis_prefix = f'track_{self.task_name}_'         # 单条任务键名
            self.redis_all_prefix = f'track_all_{self.task_name}'  # redis 索引名
            self.deal_tool = DealTtool(self.task_name, self.redis, self.redis_all_prefix, self.redis_prefix)
        self.logger = get_logger(self.task_name)
        # self.pc_user_agents = UtilUseragent.get()
        # self.mb_user_agents = UtilUseragent.get(type='MOBILE')
        self.sending_queue = Queue()
        self.sended_queue = Queue()
        self.response_queue = Queue()
        self.sended_queue_max = 5000     # sended_queue 最大值
        self.response_queue_max = 1500   # response_queue 最大值
        self.task_name = task_name
        self.request_proxy = False
        self.downloader = self.get_downloader()
        self.thread_wait = 0
        self.logger.info(f'程序启动：{env}')
        self.username = carrier_account.get(self.task_name.upper(), {}).get("username", "")
        self.password = carrier_account.get(self.task_name.upper(), {}).get("password", "")
        if sys.platform != "darwin":
            set_pid(pid_key=self.task_name)

    def get_downloader(self):
        """
        设置下载器类型，默认为Downloader
        Return:
            SpiderDownloader
        """
        return Downloader(self.task_name)

    def start_requests(self):
        """
        初始化待发送请求队列，由子类实现。拼装请求数据并送到sending_queue队列中
        todo: 2022-05: 当前只接收列表中存放单条任务的格式
        """
        raise NotImplementedError()

    def is_finish(self):
        """
        根据相关队列是否全都为空来判断任务处理结束
        """
        return self.sending_queue.empty() and self.sended_queue.empty() and self.response_queue.empty()

    def record_log(self):
        """
        记录抓取日志，用于调整各个线程参数设置
        """
        while True:
            table = PrettyTable(["x", "y"])
            table.add_row(["datetime", str(datetime.now())])
            table.add_row(["sending_queue", self.sending_queue.qsize()])
            table.add_row(["sended_queue", self.sended_queue.qsize()])
            table.add_row(["response_queue", self.response_queue.qsize()])
            table.reversesort = True
            print(table)
            del table
            # objgraph.show_most_common_types()
            time.sleep(30)

    def get_redis_tasks(self):
        """ 组装要发送的任务列表"""
        task_list = []
        redis_tasks = self.deal_tool.get_sending_redis_tasks()
        for task_dict in redis_tasks:
            next_query_time = task_dict.get('next_query_time', '')
            if task_dict['task_status'] == 0 and (
                    next_query_time == '' or datetime.strptime(task_dict['next_query_time'], "%Y-%m-%d %H:%M:%S") <= datetime.now()):
                task_list.append(task_dict)
        return task_list

    @retry(retry_times=-1, wait=5)
    def put_task_dict_into_redis(self):
        """ 从接口获取数据"""
        while True:
            self.deal_tool.put_dict_and_check([self.task_name])
            time.sleep(30 * 60)

    def deal_request_results(self, results, request):
        if results['success']:
            self.sended_queue.put(request)
        else:
            print('send parameters error urls: {}'.format(request.urls))

    @retry(retry_times=-1, wait=5)
    def send_requests(self, max_idle_time):
        results = dict()  # todo: 以后部署服务器后完善
        results['success'] = True
        start_time = time.time()
        while True:
            try:
                if self.sended_queue.qsize() < self.sended_queue_max and self.response_queue.qsize() < self.response_queue_max:
                    request = self.sending_queue.get(timeout=1)
                    self.deal_request_results(results, request)
            except Empty:
                pass
                if max_idle_time == -1:
                    pass
                elif start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception:
                print(traceback.format_exc())

    @retry(retry_times=-1, wait=5)
    def get_response(self, max_idle_time):
        """
        获取url爬取结果。将sended_queue队列中的SpiderRequest对象通过downloader到下载中心去获取抓取到的html
        """
        start_time = time.time()
        while True:
            try:
                if self.response_queue.qsize() < self.response_queue_max:
                    request = self.sended_queue.get(timeout=1)  # task_id,user_id,urls
                    results = self.downloader.get(request, request_proxy=self.request_proxy)       # request 对象
                    self.response_queue.put((request, results))  # 结果
                    start_time = time.time()
                    self.get_wait()     # wait confirm
                else:
                    time.sleep(5)
            except Empty:
                if max_idle_time == -1:
                    pass
                elif start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(5)
            except Exception:
                print(traceback.format_exc())

    @retry(retry_times=-1, wait=5)
    def deal_response(self, max_idle_time=-1):
        """
        从结果队列response_queue中取出结果进行处理
        """
        start_time = time.time()
        while True:
            try:
                request, results = self.response_queue.get(timeout=1)
                try:
                    self.deal_response_results(request, results)
                except Exception:
                    print(traceback.format_exc())
                start_time = time.time()
            except Empty:
                if max_idle_time == -1:
                    pass
                elif start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception:
                print(traceback.format_exc())

    def deal_response_results(self, request_, results):
        u = request_.urls[0]
        result = {"url": u["url"], "result": "", "header": "",
                  "redirect_url": "", "code": 0}

        if results['success']:
            response = results.get('results', '')
            code = response.status_code; result["code"]=code
            if code == 200:
                try:
                    if response.encoding == 'ISO-8859-1':
                        encodings = requests.utils.get_encodings_from_content(response.text)
                        if encodings:
                            encoding = encodings[0]
                        else:
                            encoding = response.apparent_encoding
                    else:
                        encoding = response.encoding
                except:
                    encoding = "utf-8"
                if result["url"] != response.url:
                    result["redirect_url"] = response.url
                encode_content = response.content.decode(encoding, 'replace').encode('utf-8', 'replace')
                if not isinstance(encode_content, str):
                    encode_content = encode_content.decode(encoding="utf-8", errors='ignore')  # bytes to str
                result["result"] = encode_content
                self.deal_response_results_status(2, u, result, request_)
            else:
                self.deal_response_results_status(2, u, result, request_)
        else:
            self.deal_response_results_status(3, u, result, request_)

    def deal_response_results_status(self, task_status, url, result, request):
        """
            处理 task_status 是2,3的任务  重试返回数组， 若重试需切换headers内容需自行定义
        :param task_status:
        :param url:
        :param result:
        :param request:
        :return:
        """
        raise NotImplementedError()

    def get_wait(self):
        """
        获取结果等待, 控制发往处理队列的速率
        """
        if self.thread_wait != 0:
            time.sleep(self.thread_wait)
        else:
            if self.response_queue.qsize() > 4000:
                time.sleep(5)
            elif self.sended_queue.qsize() < 2000:
                time.sleep(1)
            else:
                time.sleep(0.1)

    def run(self, put_num=0, get_num=1, send_num=0, deal_num=0, send_idle_time=-1,get_idle_time=-1,deal_idle_time=-1, record_log=False, spider_count=0):
        """
        爬虫启动入口
        Args:
        """
        if self.use_redis:
            self.deal_tool.check_redis_data()
        thread_start = Thread(target=self.start_requests)  # 发送请求
        thread_start.start()
        print("put_num: {}; send_num:{}; deal_num: {};  spider_count: {}".format(put_num, send_num, deal_num, spider_count))
        threads = list()

        put_num = 0 if not self.use_redis else put_num  # 不使用redis时，不会从接口中获取数据
        for i in range(0, put_num):
            threads.append(Thread(target=self.put_task_dict_into_redis, args=()))
        for i in range(0, get_num):
            threads.append(Thread(target=self.get_response, args=(get_idle_time,)))
        for i in range(0, send_num):
            threads.append(Thread(target=self.send_requests, args=(send_idle_time,)))
        for i in range(0, deal_num):
            threads.append(Thread(target=self.deal_response, args=(deal_idle_time,)))
        if record_log:
            thread = Thread(target=self.record_log)
            thread.setDaemon(True)
            threads.append(thread)
        for thread in threads:
            thread.start()