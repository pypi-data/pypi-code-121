# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-10-22 13:32:07
@LastEditTime: 2022-04-26 10:02:26
@LastEditors: HuangJianYi
@Description: 
"""
from seven_framework import *

class ActionHelper:
    """
    :description:执行帮助类 例子：执行多个方法run_func_while([lambda: act_info_model.add_entity(act_info),lambda: act_info_model.get_dict("id>0"),lambda: act_info_model.get_list("id>0")]) 或执行单个方法run_func_while(lambda: act_info_model.add_entity(act_info))
    """
    logger_error = Logger.get_logger_by_name("log_error")

    @classmethod
    def run_action_while(self, action, sleep_time=0.5, is_log=False, error_count_log=100, title=""):
        """
        :description: 无限循环执行动作
        :param action:方法
        :param sleep_time:异常停留时间，单位秒
        :param is_log:是否记录日志
        :param error_count_log:出错多少次记一次日志
        :param title:异常标题
        :return:无返回
        :last_editors: HuangJianYi
        """
        if not action:
            raise ValueError("参数action不能为空")
        if not sleep_time:
            raise ValueError("参数sleep_time不能为空")
        run_count = 0
        while True:
            try:
                if isinstance(action,list):
                    for item in action:
                        item()
                else:
                    action()
                break
            except Exception:
                if is_log == True and (run_count % error_count_log == 0):
                    self.logger_error.error(f"title:{title},ex:{traceback.format_exc()}")
                print(title+":"+traceback.format_exc())
            run_count+=1
            time.sleep(sleep_time)

    @classmethod
    def run_func_while(self, func, sleep_time=0.5, is_log=False, error_count_log=100, title=""):
        """
        :description: 无限循环执行动作
        :param func:方法
        :param func:异常标题
        :param sleep_time:异常停留时间，单位秒
        :param is_log:是否记录日志
        :param error_count_log:出错多少次记一次日志
        :return:结果数据
        :last_editors: HuangJianYi
        """
        if not func:
            raise ValueError("参数func不能为空")
        if not sleep_time:
            raise ValueError("参数sleep_time不能为空")
        run_count = 0
        while True:
            try:
                if isinstance(func,list):
                    result = []
                    for item in func:
                        result.append(item())
                    return result
                else:
                    return func()
            except Exception:
                if is_log == True and (run_count % error_count_log == 0):
                    self.logger_error.error(f"title:{title},ex:{traceback.format_exc()}")
                print(title+":"+traceback.format_exc())
            run_count+=1
            time.sleep(sleep_time)

    @classmethod
    def run_action(self, action, sleep_time=0.5, retry_run_count=10, is_log=False, error_count_log=10, title=""):
        """
        :description: 限制次数执行动作
        :param action:方法
        :param sleep_time:异常停留时间，单位秒
        :param retry_run_count:尝试次数
        :param is_log:是否记录日志
        :param error_count_log:出错多少次记一次日志
        :param title:异常标题
        :return:bool
        :last_editors: HuangJianYi
        """
        if not action:
            raise ValueError("参数action不能为空")
        if not sleep_time:
            raise ValueError("参数sleep_time不能为空")
        run_count = 0
        while run_count <= retry_run_count:
            try:
                if isinstance(action,list):
                    for item in action:
                        item()
                else:
                    action()
                break
            except Exception:
                if is_log == True and (run_count % error_count_log == 0):
                    self.logger_error.error(f"title:{title},ex:{traceback.format_exc()}")
                print(title+":"+traceback.format_exc())
            run_count+=1
            time.sleep(sleep_time)

    @classmethod
    def run_func(self, func, sleep_time=0.5, retry_run_count=10, is_log=False, error_count_log=10, title=""):
        """
        :description: 限制次数执行动作
        :param action:方法
        :param sleep_time:异常停留时间，单位秒
        :param retry_run_count:尝试次数
        :param is_log:是否记录日志
        :param error_count_log:出错多少次记一次日志
        :param title:异常标题
        :return:结果数据
        :last_editors: HuangJianYi
        """
        if not func:
            raise ValueError("参数func不能为空")
        if not sleep_time:
            raise ValueError("参数sleep_time不能为空")
        run_count = 0
        while run_count <= retry_run_count:
            try:
                if isinstance(func,list):
                    result = []
                    for item in func:
                        result.append(item())
                    return result
                else:
                    return func()
            except Exception:
                if is_log == True and (run_count % error_count_log == 0):
                    self.logger_error.error(f"title:{title},ex:{traceback.format_exc()}")
                print(title+":"+traceback.format_exc())
            run_count+=1
            time.sleep(sleep_time)
        return None
