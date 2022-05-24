import threading
import time
from abc import ABC, abstractmethod

from re_common.baselibrary.mthread.MThreadingRun import especialThreadName
from re_common.baselibrary.mthread.mythreading import ThreadPoolManger
from re_common.baselibrary.utils.ringlist import RingList
from re_common.facade.loggerfacade import get_streamlogger

"""
event版的多线程，现在已经不在使用 (已废弃)
"""
class MThreadingRunEvent(ABC):
    def __init__(self, num, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = get_streamlogger()
        self.etn = especialThreadName()
        # 线程数
        self.threadingnum = num
        # 代理列表
        self.list_proxy = RingList()
        # 线程池
        self.thread_pool = ThreadPoolManger(self.threadingnum, self.logger)
        self.thread_pool.set_callback(self.thread_pool_hook)
        # 结果集
        self.results = []
        # 线程方法
        self.func = self.fun
        # 结果数
        self.resultnum = 0
        # 工作线程数
        self.jobnum = 0
        # 结果集被处理标志  默认被处理 是为了兼容之前的代码不去改动
        self.dealresultstatus = True
        # 結果到达该数量后处理结果 默认及时处理
        self.dealresultsnum = 0
        # 代理设置时间
        self.proxytime = 0
        # 标识event set之后是否对任务进行了设置
        # self.eventbool = False
        self.modle = 1
        # 在任务和处理结果时event信号的状态
        self.result_event_status = True
        self.task_event_status = True
        self.thread_run_lock = threading.Lock()

        # 全局使用特殊的单词
        self.BREAK = "break"

    def set_is_restart(self, name, is_restart):
        self.thread_pool.especial_thread_pool_dicts[name].set_is_restart(is_restart)

    @abstractmethod
    def setProxy(self, proxysList=None):
        """
        将代理加入到循环队列中 self.list_proxy
        :param proxysList:
        :return:
        """
        pass

    @abstractmethod
    def fun(self, threadval, *args, **kwargs):
        pass

    @abstractmethod
    def thread_pool_hook(self, thread_pool_dicts, thread, args, kwargs) -> dict:
        """
        钩子函数 可以被重写
        主要重写里面的dicts部分
        :return:
        """
        return {}

    @abstractmethod
    def setTask(self, results=None, *args, **kwargs):
        # self.thread_pool.event.set()  # 自动释放信号
        # 当设置任务和处理结果使用同一个连接时尽量使用event信号保证不同时执行sql在一个执行未返回时
        # 请查询较大数据时主动释放
        pass

    @abstractmethod
    def getTask(self, *args, **kwargs):
        """
        主要用于mysql的请求
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def setTask_noevent(self, *args, **kwargs):
        """
        设置任务，在没有event限制的情况下将两个步骤写在一起
        :param args:
        :param kwargs:
        :return:
        """
        while True:
            results = self.getTask(*args, **kwargs)
            reslt = self.setTask(results, *args, **kwargs)
            if reslt == self.BREAK:
                break

    def __setTask(self, *args, **kwargs):
        # 设置等待任务队列为空时继续添加任务
        # 继承类必须在第一步调用父类的该方法
        while True:
            # 获取Event 状态
            self.task_event_status = True
            self.logger.info("self.thread_pool.event_is_set() is {}".format(self.thread_pool.event_is_set()))
            # 如果状态为False 即　堵塞状态
            if not self.thread_pool.event_is_set():
                # 判断　result_event_status　和　task_event_status　都堵塞　理论上不存在　但Event并不完美
                if self.result_event_status and self.task_event_status:
                    # 设置　信号允许堵塞通过　状态为True
                    self.thread_pool.event_set()
                time.sleep(1)
                continue
            self.logger.info("event_wait")
            # 等待信号后执行设置任务
            self.thread_pool.event_wait(50)
            # 得到信号后clrar 不允许其他地方运行 状态　False
            self.thread_pool.event_clear()
            if self.result_event_status is False:
                self.logger.info("elf.result_event_status is False")
                continue
            self.task_event_status = False
            # 执行getTask
            self.logger.info("getTask")
            result = self.getTask(*args, **kwargs)
            # 运行完毕 其他地方等待的信号可以继续运行 True
            self.thread_pool.event_set()
            self.task_event_status = True
            # 执行ste()
            reslt = self.setTask(result, *args, **kwargs)

            # 是否跳出循环　结束线程
            if reslt == "break":
                break
            time.sleep(1)

    def dealresult(self, *args, **kwargs):
        """
        如果没有在这里处理 请将 self.dealresultstatus = False这样不会丢数据
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def deal_results_no_event(self, *args, **kwargs):
        """
        该函数用于没有信号的机制里
        使用信号主要是因为多线程无法同时使用一个链接
        有可能出现错误
        :param args:
        :param kwargs:
        :return:
        """
        while True:
            # 处理结果标识
            self.dealresultstatus = True
            # 从结果队列获取结果到results
            self.getreustlFromQueue()
            if len(
                    self.results) > self.dealresultsnum or self.thread_pool.work_queue.is_empty() or not self.thread_pool.thread_queue:
                if len(self.results) > 0 or not self.thread_pool.thread_queue.is_empty():
                    # 处理结果
                    self.dealresult()
                    if self.dealresultstatus:
                        # 处理完结果后要清理
                        self.results.clear()
                else:
                    time.sleep(10)
            else:
                time.sleep(3)

    def deal_results(self, *args, **kwargs):
        """
        现在单开线程处理结果
        :return:
        """
        self.logger.info("开始处理结果")
        while True:
            self.result_event_status = True
            self.logger.info("self.thread_pool.event_is_set() is {}".format(self.thread_pool.event_is_set()))
            # 处理结果标识
            self.dealresultstatus = True
            # 从结果队列获取结果到results
            self.getreustlFromQueue()
            if len(self.results) > self.dealresultsnum or self.thread_pool.work_queue.is_empty() \
                    or not self.thread_pool.thread_queue.is_empty():
                if len(self.results) > 0 or not self.thread_pool.thread_queue.is_empty():
                    # 处理结果
                    # 为防止同一个连接多线程操作出现问题使用信号加锁
                    # 等待event为true
                    if not self.thread_pool.event_is_set():
                        # print("deal result is event: " + str(self.thread_pool.event.is_set()))
                        if self.result_event_status and self.task_event_status:
                            self.thread_pool.event_set()
                        time.sleep(1)
                        continue
                    self.thread_pool.event_wait(60)
                    # 设置event为false不允许其他等待线程操作
                    self.thread_pool.event_clear()
                    if self.task_event_status is False:
                        continue
                    self.result_event_status = False
                    # 处理结果
                    self.dealresult()
                    # 本地操作完毕 允许其他线程操作mysql
                    self.thread_pool.event_set()
                    self.result_event_status = True
                    if self.dealresultstatus:
                        # 处理完结果后要清理
                        self.results.clear()
                else:
                    time.sleep(10)
            else:
                time.sleep(3)

    def setfunc(self, func):
        # 设置线程方法
        self.func = func

    def add_job(self, func, *args, **kwargs):
        self.jobnum += 1
        self.thread_pool.add_job(func, *args, **kwargs)

    def getreustlFromQueue(self):
        # 从结果队列获取结果到results
        once_result_num = 0
        while not self.thread_pool.result_queue.is_empty():
            self.resultnum += 1
            once_result_num += 1
            if once_result_num > 100:
                return
            result = self.thread_pool.result_queue.get()
            self.results.append(result)
            self.thread_pool.result_queue.task_done()

    def checkResultsfininsh(self, *args, **kwargs):
        """
        该函数用于处理运行到最后时结果不足100的情况
        :return:
        """
        if self.thread_pool.work_queue.is_empty():
            t1 = len(self.results)
            self.logger.info("self.results len is %s " % str(t1))
            if t1 != 0:
                return False
            else:
                return True

    def other(self):
        self.logger.info("工作队列任务量为{},结果队列任务量为{}".format(self.thread_pool.work_queue.get_size(),
                                                        self.thread_pool.result_queue.get_size()))
        # 通过工作队列和结果队列观察是否结束
        if self.thread_pool.checkThreadRunFinish():
            self.logger.info("初次判断任务已经结束，各个队列为空")
            return True
        else:
            return False

    def check_especial_thread(self):
        if self.modle == 1:
            task = self.__setTask
            proxy = self.setProxy
            result = self.deal_results
        elif self.modle == 2:
            task = self.setTask_noevent
            proxy = self.setProxy
            result = self.deal_results_no_event
        else:
            raise Exception("不存在指定model")

        nowThreadsName = self.thread_pool.get_now_thread()
        for name in list(self.thread_pool.especial_thread_pool_dicts.keys()):
            thread = self.thread_pool.especial_thread_pool_dicts[name].get_thread()
            # 如果线程字典为空 代表已被删除
            if name in nowThreadsName and thread.is_alive():
                # print(name + ": is run")
                pass  # 当前某线程名包含在初始化线程组中，可以认为线程仍在运行
            else:
                self.logger.info("name is :" + name + "; 没有在线程中")
                if name in self.etn.list_name():
                    if name == self.etn.taskthreadname:
                        taskin = task
                    elif name == self.etn.proxythreadname:
                        taskin = proxy
                    elif name == self.etn.dealresultthreadname:
                        taskin = result
                    else:
                        raise Exception("没有对应的任务，请检查")
                    is_start = False
                    if name in self.thread_pool.especial_thread_pool_dicts:
                        threadinfo = self.thread_pool.especial_thread_pool_dicts[name]
                        if threadinfo.get_thread().is_alive():
                            is_start = True
                        if not threadinfo.get_is_restart():
                            is_start = True
                    if not is_start:
                        args = self.thread_pool.especial_thread_pool_dicts[name].get_args()
                        kwargs = self.thread_pool.especial_thread_pool_dicts[name].get_kwargs()
                        self.thread_pool.set_add_especial_thread(taskin, name, *args, **kwargs)

    def start_especial_thread(self):
        # 开启一个线程设置任务
        self.thread_pool.set_add_especial_thread(self.__setTask, self.etn.taskthreadname)
        self.thread_pool.set_add_especial_thread(self.setProxy, self.etn.proxythreadname)
        self.thread_pool.set_add_especial_thread(self.deal_results, self.etn.dealresultthreadname)
        self.thread_pool.especial_start()

    def start_especial_thread_no_evnt(self):
        # 开启一个线程设置任务
        self.thread_pool.set_add_especial_thread(self.setTask_noevent, self.etn.taskthreadname)
        self.thread_pool.set_add_especial_thread(self.setProxy, self.etn.proxythreadname)
        self.thread_pool.set_add_especial_thread(self.deal_results_no_event, self.etn.dealresultthreadname)
        self.thread_pool.especial_start()

    def is_break(self):
        return False

    def run(self, model=1):
        self.modle = model
        if model == 1:
            # 有event
            self.start_especial_thread()
        elif model == 2:
            self.start_especial_thread_no_evnt()
        while True:
            time.sleep(3)
            self.thread_pool.checkThread()
            self.check_especial_thread()
            if self.other():
                if not self.checkResultsfininsh():
                    continue
                else:
                    print("进入other 判断 再次确认finish")
                    if self.thread_pool.work_queue.is_empty() and self.thread_pool.result_queue.is_empty() \
                            and len(self.results) == 0:
                        print("运行完毕")
                        if self.is_break():
                            print("10 s break")
                            time.sleep(10)
                            break
