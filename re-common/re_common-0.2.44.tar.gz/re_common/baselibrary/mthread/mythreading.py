import ctypes
import functools
import inspect
import sys
import threading
# 创建一个有4个线程的线程池
import time
import traceback
from threading import Thread

from re_common.baselibrary.utils.basequeue import BaseQueue
from re_common.facade.loggerfacade import get_streamlogger


class ThreadInfo(object):
    """
    该类存储着线程的信息，原本使用一个空的字典进行存储，
    但字典的结构不可见且不清晰，故使用类进行结构化展示
    """

    def __init__(self):
        self.is_restart = True

    def set_thread(self, thread):
        self.thread = thread
        return self

    def get_thread(self):
        return self.thread

    def set_thread_name(self, thread_name):
        self.thread_name = thread_name
        return self

    def get_thread_name(self):
        return self.thread_name

    def set_kwargs(self, kwargs):
        self.kwargs = kwargs
        return self

    def get_kwargs(self):
        return self.kwargs

    def set_args(self, args):
        self.args = args
        return self

    def get_args(self):
        return self.args

    def set_dicts(self, dicts):
        self.dicts = dicts
        return self

    def get_dicts(self):
        return self.dicts

    def set_is_restart(self, is_restart: bool):
        """
        设置该线程是否应该重启
        :param is_restart:
        :return:
        """
        self.is_restart = is_restart
        return self

    def get_is_restart(self):
        return self.is_restart


class ThreadPoolManger(object):
    """
    线程池管理器
    """
    # 线程锁
    lock = threading.Lock()

    def __init__(self, thread_num, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = get_streamlogger()
        self.prefix = "my_threading_task_"
        # 任务队列
        self.work_queue = BaseQueue(100)
        # 结果队列 有时候结果需要在主线程处理或单独线程处理时使用
        self.result_queue = BaseQueue(100)
        # 线程队列 主要管线程间的通信
        self.thread_queue = BaseQueue(10)
        # 线程池 里面保存着线程对象
        # self.threadpool = list()
        # # 线程名列表
        # self.initThreadsName = set()
        # 应该赋予一个方法 用于回调
        self.callback = None
        # 线程池的字典 有时候需要在线程池中维护一些数据，所以没有采用原来的只维护线程对象
        self.thread_pool_dicts = {}

        # 线程数量 反馈当前工作线程数量
        self.thread_num = thread_num
        # 工作线程定量 该变量是为了维持线程的数量一定
        self.max_workers = thread_num
        # 是否是动态最大值
        self.is_static_max = True
        # 线程的参数　定义线程时使用
        self.args = ()
        self.kwargs = {}

        # # 各种非工作线程池
        # self.especial_thread_pool = list()
        # # 特殊线程名
        # self.especial_threads_Name = set()

        # 各种非工作线程池 特殊线程名
        self.especial_thread_pool_dicts = {}

        # 该标志将用于sql间的同步  现在发现一个问题 在 线程中执行select会出现
        # Command Out of Sync 错误  所以启用这个信号
        # 这个错误表示 对于同一个连接 在不同线程中当一个线程发出sql且没有返回结果期间，
        # 另一个线程页发出了请求，这时mysql的第一个请求在结果缓存中还没有返回 会冲突报错
        # 这里主要是设置任务和处理结果用到同一个连接导致
        self.event = threading.Event()
        self.event_set()
        # 独立的线程变量，很多时候 多线程变量是共享且线程不安全的，
        # 该变量保证了线程内变量的安全与threadVal的概念相同
        self.localVal = threading.local()

        # # 初始化线程到线程池
        self.__init_threading_pool(self.thread_num)

    @classmethod
    def thread_lock(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                cls.lock.acquire()
                return func(*args, **kwargs)
            finally:
                cls.lock.release()

        return wrapper

    def set_args(self, args):
        """
        设置元组参数
        :param args:
        :return:
        """
        self.args = args

    def set_kwargs(self, kwargs):
        """
        设置字典参数
        :param kwargs:
        :return:
        """
        self.kwargs = kwargs

    def set_is_static_max(self, is_static_max):
        """
        设置是否允许
        :param is_static_max:
        :return:
        """
        self.is_static_max = is_static_max

    def set_max_workers(self, num):
        """
        如果线程数是动态的，就允许设置大小
        :param num:
        :return:
        """
        if self.is_static_max:
            self.logger.info("是静态最大线程数,不能对最大线程数进行设置")
        else:
            self.max_workers = num

    def get_max_workers(self):
        return self.max_workers

    def get_localVal(self):
        """
        获取线程独立变量
        :return:
        """
        return self.localVal

    def set_localVal(self, val):
        self.localVal = val

    def set_callback(self, callback):
        self.callback = callback

    def event_set(self):
        """
        设置event 允许wait继续运行 状态为True
        :return:
        """
        self.event.set()

    def event_clear(self):
        """
        设置值为False 不允许运行其他线程
        :return:
        """
        self.event.clear()

    def event_is_set(self):
        """
        返回标志
        :return:
        """
        return self.event.is_set()

    def event_wait(self, timeout=None):
        self.event.wait(timeout)

    def set_thread_name_prefix(self, prefix):
        self.prefix = prefix

    def __init_threading_pool(self, thread_num):
        """
        初始化线程池，创建指定数量的线程池
        :param thread_num:
        :return:
        """
        self.logger.info("初始化工作线程数量为：%d" % thread_num)
        for i in range(int(thread_num)):
            # 新建一个线程
            thread = ThreadManager(self.work_queue,
                                   self.result_queue,
                                   self.thread_queue,
                                   self.logger,
                                   args=self.args,
                                   kwargs=self.kwargs)
            # 线程名
            threadName = "{}{}".format(self.prefix, i + 1)
            if threadName in self.thread_pool_dicts:
                self.logger.warn("线程名%s在线程池中已经存在，跳过" % threadName)
            else:
                # 设置线程名
                thread.setName(threadName)
                self.set_thread_pool_dicts(self.thread_pool_dicts, threadName, thread, self.args, self.kwargs)

    def set_thread_pool_dicts(self, thread_pool_dicts, threadName, thread, args, kwargs):
        """
        这里调用了一个钩子函数 可以在dicts中加入其他参数
        :param thread_pool_dicts: 线程池字典对象
        :param threadName:  线程名
        :param thread:  线程
        :param args:
        :param kwargs:
        :return:
        """
        threadinfo = ThreadInfo()
        threadinfo.set_thread(thread)
        threadinfo.set_kwargs(kwargs)
        threadinfo.set_args(args)
        threadinfo.set_thread_name(threadName)
        if self.callback:
            # 对象使用
            dicts = self.callback(threadinfo)
        else:
            # 继承时使用
            dicts = self.thread_pool_hook(threadinfo)
        if not dicts:
            dicts = {}
        threadinfo.set_dicts(dicts)
        thread_pool_dicts[threadName] = threadinfo

    def thread_pool_hook(self, threadinfo: ThreadInfo) -> dict:
        """
        钩子函数 可以被重写
        主要重写里面的dicts部分
        :return:
        """
        return {}

    def reload_thread(self, thread_name):
        """
        通过线程名重启线程
        :param thread_name:
        :return:
        """
        is_start = False
        if thread_name in self.thread_pool_dicts:
            self.logger.info("{}线程名存在".format(thread_name))
            if self.thread_pool_dicts[thread_name].get_thread().is_alive():
                self.logger.info("{}线程名是存活的".format(thread_name))
                is_start = True
            else:
                self.logger.info("{}线程名是没有存活 需要重启".format(thread_name))

            if not is_start:
                args = self.thread_pool_dicts[thread_name].get_args()
                kwargs = self.thread_pool_dicts[thread_name].get_kwargs()
                self.logger.info("新建或重启线程{}".format(thread_name))
                # 新建一个线程
                thread = ThreadManager(self.work_queue, self.result_queue, self.thread_queue, self.logger, args=args,
                                       kwargs=kwargs)
                # 设置线程名
                thread.setName(thread_name)
                # # 加入线程池
                # self.threadpool.append(thread)
                self.set_thread_pool_dicts(self.thread_pool_dicts, thread_name, thread, args, kwargs)
                thread.start()

    def add_thread(self, thread_num):
        """
        添加线程，thread_num是添加线程的数量
        :param thread_num:
        :return:
        """
        # 判断可开线程的数量
        if self.thread_num < self.max_workers:
            if self.max_workers - self.thread_num < thread_num:
                thread_num = self.max_workers - self.thread_num
        else:
            self.logger.info("线程已达到最大量，不能再新开线程")
            return False
        # 添加新的线程
        count = 0
        num = 0
        while thread_num > count:
            num += 1
            thread = ThreadManager(self.work_queue, self.result_queue, self.thread_queue,
                                   self.logger,
                                   args=self.args,
                                   kwargs=self.kwargs)
            thread_name = "{}{}".format(self.prefix, num)
            if thread_name in self.thread_pool_dicts:
                continue
            thread.setName(thread_name)
            self.logger.info("添加一个线程{}".format(thread_name))
            self.set_thread_pool_dicts(self.thread_pool_dicts, thread_name, thread, self.args, self.kwargs)
            count += 1
        self.get_thread_num()
        return True

    def delete_thread(self, thread_num):
        """
        删除多少个线程，thread_num为删除数量
        :param thread_num:
        :return:
        """
        try:
            i = 0
            for key in list(self.thread_pool_dicts.keys()):
                thread = self.thread_pool_dicts[key].get_thread()
                if not thread.runstatus:
                    # 优先删除处于等待任务的线程
                    thread.thread_delete = True
                    self.stop_thread(thread)
                    del self.thread_pool_dicts[key]
                    i += 1
                elif thread.threadval.thread_delete:
                    # 删除该线程 表示线程池想删除(删除逻辑为我想删除 且程序内部允许删除时删除)
                    thread.thread_delete = True
                    del self.thread_pool_dicts[key]
                    i += 1
                if i >= thread_num:
                    break
        except IndexError:
            pass
        self.get_thread_num()

    def get_thread_num(self):
        self.thread_num = len(self.thread_pool_dicts)
        return self.thread_num

    def set_thread_num(self, thread_num):
        """
        设置当前线程数量 改设置保证了线程数量 多的会被删除,少的会被添加
        :return:
        """
        if thread_num > self.get_thread_num():
            self.add_thread(thread_num - self.thread_num)
        else:
            self.delete_thread(self.get_thread_num() - thread_num)
            # self.threadpool = self.threadpool[:int(thread_num)]
        self.thread_num = thread_num

    def add_super_thread(self, func, thread_name, mode="super", *args, **kwargs):
        """
        添加一个线程，该线程直接由原生线程控制，
        :param func:
        :param thread_name:
        :param args:
        :param kwargs:
        :return:
        """
        thread = ThreadManager(self.work_queue, self.result_queue, self.thread_queue,
                               self.logger,
                               target=func, name=thread_name,
                               args=args,
                               kwargs=kwargs)
        thread.set_mode(mode)
        return thread

    def set_add_especial_thread(self, func, threadname, mode="super", *args, **kwargs):
        """
        添加特殊的线程
        :return:
        """
        # 得到一个线程对象
        thread = self.add_super_thread(func, threadname, mode, *args, **kwargs)
        self.set_thread_pool_dicts(self.especial_thread_pool_dicts, threadname, thread, args, kwargs)
        return thread

    def add_job(self, func, *args, **kwargs):
        """
        将任务放入队列，等待线程池阻塞读取，参数是被执行的函数和函数的参数
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        self.work_queue.put((func, self.result_queue, args, kwargs))

    def start(self):
        for thread in self.thread_pool_dicts:
            time.sleep(2)
            if self.thread_pool_dicts[thread]:
                thread = self.thread_pool_dicts[thread].get_thread()
                if thread and not thread.is_alive():
                    thread.start()

    def especial_start(self):
        for threadname in self.especial_thread_pool_dicts:
            if self.especial_thread_pool_dicts[threadname]:
                threadinfo = self.especial_thread_pool_dicts[threadname]
                thread = threadinfo.thread
                if thread and not thread.is_alive():
                    self.logger.info("启动线程{}".format(thread.getName()))
                    thread.start()
                else:
                    self.logger.info("启动线程{} 失败".format(thread.getName()))

    def get_now_thread(self):
        """
        获取进程中还存在的线程
        :return:
        """
        # 用来保存当前线程名称
        nowThreadsName = []
        # 获取当前线程名
        now = threading.enumerate()
        for i in now:
            # 保存当前线程名称
            nowThreadsName.append(i.getName())
        return nowThreadsName

    # 防止线程意外挂掉 挂掉线程重启
    def checkThread(self):
        nowThreadsName = self.get_now_thread()
        # 循环线程池的key
        for name in list(self.thread_pool_dicts.keys()):
            # 取出线程对象
            thread = self.thread_pool_dicts[name].get_thread()
            # 如果线程字典为空 代表已被删除
            if name in nowThreadsName and thread.is_alive():
                pass  # 当前某线程名包含在初始化线程组中，可以认为线程仍在运行
            else:
                self.reload_thread(name)  # 重启线程
        # 如果不是静态最大值 线程可以波动
        if not self.is_static_max:
            # 空闲线程
            free_thread = 0
            # 判断线程空闲情况
            for name in list(self.thread_pool_dicts.keys()):
                thread = self.thread_pool_dicts[name].get_thread()
                if not thread.runstatus:
                    # 代表该线程等待工作队列，列入空闲线程
                    free_thread += 1
                elif thread.threadval.thread_delete:
                    free_thread += 1

            # 允许冗余2个工作线程 避免在零界点不停的创建,删除
            if free_thread > 2:
                self.max_workers = self.max_workers - (free_thread - 2)

            # 判断是否需要删除线程
            if len(self.thread_pool_dicts) > self.max_workers:
                self.logger.info("线程池有{},最大线程数量{}，调用删除线程程序".format(len(self.thread_pool_dicts), self.max_workers))
                self.delete_thread(len(self.thread_pool_dicts) - self.max_workers)

        self.logger.info("当前线程数量为{},线程为:{}".format(len(self.thread_pool_dicts), list(self.thread_pool_dicts.keys())))

    def checkThreadRunFinish(self):
        """
        通过等待的方式判断结束，等待是因为任务队列取出任务后在运行，还没放入结果队列
        :return:
        """
        self.logger.info("result_queue is empty:{}".format(self.result_queue.is_empty()))
        self.logger.info("work_queue is empty:{}".format(self.work_queue.is_empty()))
        if self.result_queue.is_empty() and self.work_queue.is_empty():
            time.sleep(10)
            t1 = self.result_queue.is_empty()
            time.sleep(10)
            t2 = self.result_queue.is_empty()
            if t1 and t2:
                if self.work_queue.is_empty():
                    return True
            return False
        return False

    # 下面两个方法是强制退出线程的方法
    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        if thread:
            try:
                self.logger.info("thread is {};thread.ident 的值为:{}".format(thread, thread.ident))
                if thread.ident:
                    self._async_raise(thread.ident, SystemExit)
            except ValueError as e:
                self.logger.info("已经运行完毕 不需要删除了")
        else:
            self.logger.info("传入的线程对象为空，理论上不应该出现这种逻辑 结束程序检查逻辑")
            sys.exit(-1)


class ThreadVal(object):
    """
    该对象维护线程函数的变量以及与线程对象间的交互
    """

    def __init__(self):
        # 该线程是否被删除
        self.thread_delete = False
        # 线程初始化参数
        self.args = ()
        self.kwargs = None
        self.result_queue = None
        self.work_queue = None

    def set_args(self, args):
        self.args = args

    def set_kwargs(self, kwargs):
        self.kwargs = kwargs

    def set_result_queue(self, result_queue):
        self.result_queue = result_queue

    def get_result_queue(self):
        return self.result_queue

    def set_work_queue(self, work_queue):
        self.work_queue = work_queue

    def get_work_queue(self):
        return self.work_queue


class ThreadManager(Thread):
    """
    定义线程类，继承threading.Thread
    该类主要实现线程的运行
    """

    def __init__(self, work_queue=None, result_queue=None, thread_queue=None, logger=None, group=None, target=None,
                 name=None, args=(), kwargs=None, daemon=True, mode="default"):
        if mode == "default":
            if work_queue is None or result_queue is None or thread_queue is None:
                raise Exception("work_queue result_queue thread_queue 必须存在")
        if args is None:
            args = ()
        # 线程本身的参数
        Thread.__init__(self, group, target, name,
                        args, kwargs, daemon=daemon)
        if kwargs is None:
            kwargs = {}
        if logger:
            self.logger = logger
        else:
            self.logger = get_streamlogger()
        self.target = target
        self.kwargs = kwargs
        self.args = args
        # 接受两个队列 一个处理结果 一个发送任务
        self.work_queue = work_queue
        self.result_queue = result_queue
        # 线程队列
        self.thread_queue = thread_queue
        # 主线程退出  该线程也会退出
        self.daemon = daemon
        # 一个标识 如果为False代表线程运行完毕等待新的任务到来,否则表示任务正在运行
        # 这个标志是为了检查程序在运行中还是等待状态
        self.runstatus = False
        # 设置该标志是为了表示是否愿意被重新启动，因为有些线程只需要运行一次
        # 而有的需要长期运行且有一定的重启机制(目前暂未启动该标志)
        self.is_restart = True
        # 为了兼容普通线程类模式  "default" 自己写的run 方法  "super": 父类的run方法
        self.mode = mode
        # 是否可以被删除 True 线程可以停止，False 不可以被停止 有时候我们需要删除一批线程 但是 线程不能中间
        # 状态被删除 故需要设置该标志
        self.thread_delete = False
        # 线程内部的一个类对象 每个线程维护一个保证里面的数据线程安全，以后为每个线程提供服务
        self.threadval = ThreadVal()
        self.threadval.set_args(self.args)
        self.threadval.set_kwargs(self.kwargs)

    def get_runstatus(self):
        return self.runstatus

    def set_runstatus(self, runstatus):
        self.runstatus = runstatus

    def get_is_restart(self):
        return self.is_restart

    def set_is_restart(self, is_restart):
        self.is_restart = is_restart

    def set_mode(self, mode):
        """
        设置运行模式 super or default
        super 将方法直接传入target
        default 使用自己封装的run
        :param mode:
        :return:
        """
        self.mode = mode

    def get_mode(self):
        return self.mode

    def run(self):
        if self.mode == "default":
            self.run_default()
        elif self.mode == "mysuper":
            self.run_arg()
        elif self.mode == "super":
            try:
                # 父类的运行程序，相当于原生支持
                super().run()
            except:
                self.logger.info(traceback.format_exc())
        else:
            raise Exception("运行模式错误 请检查 default or super")

    def run_arg(self):
        try:
            if self.target:
                self.threadval.set_result_queue(self.result_queue)
                self.threadval.set_work_queue(self.work_queue)
                self.target(self.threadval, *self.args, **self.kwargs)
        finally:
            del self.target, self.args, self.kwargs

    def run_default(self):
        """
        启动线程,默认的运行程序，
        :return:
        """
        while True:
            try:
                if self.thread_delete and self.threadval.thread_delete:
                    print("主动停止线程{},因为两个信号量都为True".format(self.getName()))
                    break
                # 该标志标识着是否取得队列值并开始工作
                self.runstatus = False
                target, result_queue, args, kwargs = self.work_queue.get()
                self.runstatus = True  # 代表取到工作队列的值
                # 更新字典 如果键相同 以初始化线程的键的值有效 所以尽量不要与初始化字典冲突
                kwargs.update(self.kwargs)
                # 初始化线程的元组参数拼接在后
                args = args + self.args
                #
                self.threadval.set_result_queue(result_queue)
                self.threadval.set_work_queue(self.work_queue)
                target(self.threadval, *args, **kwargs)
                self.work_queue.task_done()
            except UnicodeDecodeError as e:
                self.logger.error(traceback.format_exc())
            except SystemExit as e:
                if e.args == (-1,):
                    self.logger.error("由逻辑判断主动退出当前线程")
                    break
                else:
                    self.logger.error("其他SystemExit错误，检查逻辑")
