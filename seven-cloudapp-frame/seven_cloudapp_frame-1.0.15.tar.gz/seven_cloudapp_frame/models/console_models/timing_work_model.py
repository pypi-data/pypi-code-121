# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-19 13:37:16
@LastEditTime: 2022-04-25 13:38:17
@LastEditors: HuangJianYi
@Description: 
"""
import threading, multiprocessing
from seven_cloudapp_frame.models.seven_model import InvokeResultData
from seven_framework import *
from seven_framework.console.base_console import *

class TimingWork():
    """
    :description: 定时作业
    """
    def __init__(self):
        self.work_name = "" #作业名称
        self.start_hours = 0 #开始小时
        self.end_hours = 24 #结束小时
        self.fail_count = 0 #失败重试次数
        self.fail_sleep_time = 1 #失败休眠时间，单位秒
        self.sleep_time = 1 #休眠时间，单位秒
        self.is_execute_one = False #是否执行一次

    do_work_thread = None

    def execute(self):
        """
        :description: 执行内容，用于重写
        :return: InvokeResultData
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        is_stop_work = False
        return invoke_result_data,is_stop_work

    def __process_work(self,work_name):
        """
        :description: 处理作业 "job_config":{"work1":{"start_hours":0,"end_hours":24},"work2":{"start_hours":0,"end_hours":24}}
        :param work_name: 作业名称
        :return: 
        :last_editors: HuangJianYi
        """
        self.work_name = work_name
        job_config = config.get_value("job_config",{})
        content_dict = job_config.get(work_name,None)
        if content_dict:
            self.start_hours = content_dict.get("start_hours",0)
            self.end_hours = content_dict.get("end_hours",24)
            self.fail_count = content_dict.get("fail_count",0)
            self.fail_sleep_time = content_dict.get("fail_sleep_time",1)
            self.sleep_time = content_dict.get("sleep_time",1)
            self.is_execute_one = content_dict.get("is_execute_one",False)
        while True:
            now_hour = TimeHelper.get_now_datetime().hour
            if now_hour >= self.start_hours and now_hour <= self.end_hours:
                invoke_result_data = InvokeResultData()
                is_stop_work = False
                try:
                    execute_result = self.execute()
                    if isinstance(execute_result, tuple):
                        invoke_result_data = execute_result[0]
                        is_stop_work = execute_result[1]
                    else:
                        invoke_result_data = execute_result
                except:
                    invoke_result_data.success = False
                if invoke_result_data.success == False and self.fail_count > 0 and is_stop_work == False:
                    for i in range(self.fail_count):
                        try:
                            execute_result = self.execute()
                            if isinstance(execute_result, tuple):
                                invoke_result_data = execute_result[0]
                                is_stop_work = execute_result[1]
                            else:
                                invoke_result_data = execute_result
                        except:
                            invoke_result_data.success = False
                        if is_stop_work == True:
                            print("定时:" + work_name + "强行停止运行")
                            break
                        if invoke_result_data.success == True:
                            print("定时:" + work_name + "第" + (i + 1) + "次尝试执行成功")
                            break
                        else:
                            print("定时:" + work_name + "第" + (i + 1) + "次尝试执行失败")
                            if self.fail_count > 0:
                                time.sleep(self.fail_sleep_time)
                if invoke_result_data.success == True:
                    print("定时:" + work_name + "本次执行成功")
                else:
                    print("定时:" + work_name + "本次执行失败")
                if is_stop_work == True:
                    print("定时:" + work_name + "强行停止运行")
                    break
                if self.is_execute_one == True:
                    time.sleep(60*60)
                    break
                else:
                    time.sleep(self.sleep_time)
            else:
                time.sleep(10)

    def start_work(self,work_name):
        """
        :description: 开始执行
        :param work_name: 作业名称
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            if self.do_work_thread == None:
                print("定时:" + work_name + "开始启动")
                self.do_work_thread = threading.Thread(target=self.__process_work, args=[work_name])
                self.do_work_thread.start()
                print("定时:" + work_name + "启动成功")
        except:
            logger_error.error(f"定时:{work_name}启动异常,ex:{traceback.format_exc()}")
            print(f"定时:{work_name}启动异常,ex:{traceback.format_exc()}")
