import datetime
import time
import shelve
import time
import threading
import asyncio
from TDhelper.Decorators.log import logging_setup, SYS_LOGS, logging
from TDhelper.Scheduler.log_config import logging_config
from TDhelper.bin.globalvar import *
from TDhelper.reflect import *
from TDhelper.Scheduler.base import *
from TDhelper.generic.requier import R

class SchedulerService(threading.Thread):
    def __init__(
        self, serializeFile="/data/", report_dir="/data/report", logging_cfg=None
    ):
        threading.Thread.__init__(self)
        logging_setup(logging_cfg if logging_cfg != None else logging_config)
        self.loop = asyncio.get_event_loop()
        self._report_dir = report_dir
        self._cacheFile = serializeFile
        self._eventLock = threading.Event()
        self._eventLock.set()
        self._timeArray = [
            ['item' for _ in range(5)] for _ in range(86400)
        ]  # 时间轮，一天的86400秒(后续可修改多重时间轮:时，分，秒，毫秒)
        self._runtasks = []  # 正在运行的任务列表
        self._index = 0  # 当前索引秒
        self._last_index = 0  # 上一次索引秒
        self.run()  # 启动任务线程
        # threading.Thread(target=self.Scheduler).start()  #启动任务列表线程

    def LoadConfig(self):
        """Load scheduler config"""
        pass

    def Install(self, task: Scheduler):
        """Install task"""
        config = task.Config()
        """config params
        config["type"]
        config["starttime"]
        config["sleep"]
        config["plug"]
        config["name"]"""

        with shelve.open(
            self._cacheFile, flag="c", writeback=True
        ) as cFile:  # open config cache file
            try:
                if config["type"].lower() == "realtime":  # run on now
                    pass
                elif config["type"].lower() == "interval":  # loop run task
                    pass
                elif config["type"].lower() == "timming":  # run on datetime with oncee
                    pass
            finally:
                cFile.close()

    def Uninstall(self, task):
        """Uninstall task"""
        pass

    async def task_list(self, timestamp):
        logging.info("async task_list TIMESTAMP(%d)." % timestamp)
        if 0 < timestamp < len(self._timeArray):
            _tasks = self._timeArray[timestamp]
            for item in _tasks:
                dynamic_cls=R("TDhelper.Scheduler.example_scheduler")
                dynamic_cls.Instance("example_scheduler",{
                    "name":"a",
                    "_plugin":"plugin",
                    "taskType":"type",
                    "startTime":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "sleep":10
                })
                state, result= await dynamic_cls.call_async("run")
                if state:
                    logging.info("example result:%s",result['result'])
                else:
                    logging.error("%s",result['msg'])
        else:
            logging.error("timestamp(%d) out of range. scope(0-86400)" % timestamp)

    async def generate_report(self, datetime):
        """
        gennerate today task report.
        args:
            datetime: YYYY-MM-DD.report
        """
        pass

    def run(self, *args, **kw):
        while True:
            self._index = (
                time.localtime().tm_hour * 60 * 60
                + time.localtime().tm_min * 60
                + time.localtime().tm_sec
            )  # 当前秒索引
            if self._index != self._last_index:
                if self._index >= 86400:  # 当日计时完毕
                    logging.info("today tasks complete. task report:*.report")
                    self.loop.run_until_complete(
                        asyncio.wait([self.generate_report(datetime())])
                    )
                    break
                else:
                    tasks = [asyncio.ensure_future(self.task_list(self._index))]
                    self.loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(0.5)
            self._last_index = self._index
        self.loop.close()
