import abc
import json
import time
from collections import namedtuple
from datetime import datetime, timedelta, date

import loguru
import redis
from apscheduler.schedulers.blocking import BlockingScheduler

from duyan_download_task import constants
from duyan_download_task.constants import ItemStatus, TaskStatus
from duyan_download_task.model import DownloadItem, DownloadTaskMain
from duyan_download_task.utils import common_utils, logger_util, mysql_util
from duyan_download_task.utils.config_util import Config

SubTypeInfo = namedtuple('SubTypeInfo', ['task_name', 'type', 'sub_type', 'queue_key', 'is_multi_task'])


class DownloadTaskBase:

    def __init__(self, task_info: SubTypeInfo, config_path: str, logger_name: str, max_job=1,
                 cron="0 0-59/2 * * * *"):
        self._logger = logger_util.LOG.get_logger(logger_name, enqueue=True)
        # 配置
        self._config = Config(config_path)
        # mysql配置
        self.repository = Repository(self._config)
        # redis链接池
        self._redisPool = redis.ConnectionPool(host=self._config.redis_config.host,
                                               port=self._config.redis_config.port,
                                               password=self._config.redis_config.password,
                                               db=self._config.redis_config.db)
        # redis客户端
        self.redisCli = redis.Redis(connection_pool=self._redisPool)
        self.task_info = task_info
        self.TASK_TYPE = task_info.sub_type
        self.TASK_QUEUE_KEY = task_info.queue_key
        # cron表达式和并发配置
        self.CRON = common_utils.get_cron_trigger_for_str(cron)
        self.max_job = max_job if max_job else 1
        self.job_map = {}
        for i in range(self.max_job):
            self.job_map[f"{task_info.task_name}-i"] = 0
        self.blocking_scheduler = BlockingScheduler()
        self._logger.info("程序开始...")
        self.init()

    def init(self):
        # 注册信息
        self.redisCli.hset(constants.TASK_INFO_KEY, self.task_info.sub_type, json.dumps(self.task_info))
        # 处理中断任务
        items = self.repository.get_running_items(self.TASK_TYPE)
        self._logger.info(f"开始处理上次未完成的任务，共{items and len(items) or 0}条")
        if items is None or len(items) == 0:
            return
        for item in items:
            self.execute_unit_job(f"{self.task_info.task_name}-0", item.get("id"))

    def get_task(self):
        """
        获取任务
        :return:
        """
        result = self.redisCli.lpop(self.TASK_QUEUE_KEY)
        if result:
            if isinstance(result, bytes):
                result = bytes.decode(result, encoding="utf-8")
            task_item_id = int(result)
        else:
            task_item_id = None
        return task_item_id

    def get_task_batch(self, batch_size: int) -> list:
        """
        批量获取任务
        :param batch_size:
        :return:
        """
        result = []
        pipeline = self.redisCli.pipeline()
        for i in range(0, batch_size - 1):
            pipeline.lpop(self.TASK_QUEUE_KEY)
        response = pipeline.execute()
        for one in response:
            if one is None:
                continue
            result.append(int(bytes.decode(one, encoding="utf-8")))
        return result

    @loguru.logger.catch
    def execute_job(self, job_name):
        """
        逻辑执行入口
        :return:
        """
        self.heart_beat()
        task_item_id = self.get_task()
        if task_item_id:
            self.execute_unit_job(job_name, task_item_id)

    @loguru.logger.catch
    def execute_batch_job(self, job_name, batch_size: int = 10):
        """
        批量任务执行入口
        :param batch_size:
        :return:
        """
        assert batch_size > 0
        task_item_ids = self.get_task_batch(batch_size)
        for task_item_id in task_item_ids:
            self.execute_unit_job(job_name, task_item_id)

    def execute_unit_job(self, job_name, task_item_id: int) -> object:
        """
        执行任务但愿
        :param task_item_id:
        :param job_name:
        :return:
        """
        data = None
        task_id = None
        item_id = None
        try:
            if task_item_id is None:
                return
            self._logger.info(f"ITEM:[ID:{task_item_id}],任务开始执行")
            self.job_map[job_name] = task_item_id

            # 更新为下载中
            self.repository.update_processing_item(task_item_id)

            # 查询任务记录
            task_item_obj = self.repository.get_task_item(task_item_id)
            if task_item_obj is None:
                self._logger.info(f"ITEM:[ID:{task_item_id}],任务不存在,数据库无法找到对应记录")
                return
            self._logger.info(f"ITEM:[ID:{task_item_id}],任务开始执行")

            # 判断data不为空 参数校验
            task_item = DownloadItem(task_item_obj)
            task_id = task_item.task_id
            item_id = task_item.id
            data = task_item.data
            if task_item.data is None or str(task_item.data).strip() == '':
                self._logger.warning(f"TASK[ID:{task_id}],ITEM[ID:{item_id}],任务执行失败,data为空")
                self.repository.finish_task_with_error(task_item_id, data, message="任务执行失败,data为空")
                return

            if not common_utils.is_json(data):
                self._logger.warning(f"TASK[ID:{task_id}],ITEM[ID:{item_id}],任务执行失败,data格式异常")
                self.repository.finish_task_with_error(task_item_id, data, message="任务执行失败,data格式异常")
                return

            if task_item.org_id is None:
                self._logger.warning(f"TASK[ID:{task_id}],ITEM[ID:{item_id}],任务执行失败,orgId为空")
                self.repository.finish_task_with_error(task_item_id, data, message="任务执行失败,orgId为空")
                return

            data_obj = self.get_validated_data_params(task_item_id, data)
            if data_obj is None:
                return

            status = task_item.status
            if status > 1:
                self._logger.warning(f"TASK[ID:{task_id}],ITEM[ID:{item_id}],任务状态为：{status}，不予处理.")
                return

            # 导出上传逻辑
            url, md5_value, file_name = self.export(task_item, data_obj)
            # 跟新为已完成
            self.repository.update_success_item(task_item_id, url, md5_value, file_name)
        except Exception as e:
            self._logger.error(f"TASK[ID:{task_id}],ITEM[ID:{item_id}],任务执行失败,error:{e}")
            self._logger.exception(e)
            self.repository.finish_task_with_error(task_item_id, data, f"任务执行失败;{e}")
            # raise e
        finally:
            self.job_map[job_name] = 0

    def execute_split_job(self):
        """
        执行子任务拆分逻辑
        :return:
        """
        if not self.task_info.is_multi_task:
            self._logger.info(f"非多子任务任务，无需任务拆分!")
            return
        tasks = self.repository.get_download_task_ready(self.task_info.sub_type)

        for task in tasks:
            item_data_list = []
            task = DownloadTaskMain(task)
            items = self.split_task(task)
            for item in items:
                item: DownloadItem = item
                item_data_list.append(
                    [item.file_name, item.type, item.task_id, item.org_id, item.data, item.status, item.created_time,
                     item.last_updated_time])
            if item_data_list:
                self.repository.insert_download_items(item_data_list)
                time.sleep(0.5)
                items = self.repository.get_download_task_items(task.id, ItemStatus.READY.value)
                self.push_item_to_queue(items)
                self.repository.update_download_status(task.id, TaskStatus.PROCESSING.value)
                self._logger.info(f"任务:[TASK_ID:{task.id}],拆分子任务完成!")

    def push_item_to_queue(self, items: list):
        """
        推任务到队列
        :param items:
        :return:
        """
        pipeline = self.redisCli.pipeline()
        for item in items:
            download_item_po = DownloadItem(item)
            sub_type = download_item_po.type
            item_id = download_item_po.id
            if self.TASK_QUEUE_KEY is not None:
                pipeline.rpush(self.TASK_QUEUE_KEY, item_id)
                self._logger.info(f"download_item[ID:{item_id}]加入任务队列{self.TASK_QUEUE_KEY}成功,sub_type:{sub_type}")
            else:
                self._logger.error(f"不存在的子类型,download_item[ID]:{item_id},sub_type:{sub_type}")
        pipeline.execute()

    def heart_beat(self):
        task = []
        for key, value in self.job_map.items():
            task.append(f"{key}:{value}")
        self._logger.info(f"心跳 ， 统计活跃任务 目前任务有：【{str.join('】【', task)}】")

    def start(self):
        """
        开始执行入口
        :return:
        """
        # 初始化执行线程
        for run_processing_name in self.job_map:
            self.blocking_scheduler.add_job(self.execute_job, trigger=self.CRON, name=run_processing_name,
                                            next_run_time=datetime.now(), max_instances=1,
                                            args=(run_processing_name,))
            time.sleep(1)
        # execute_split_job
        self.blocking_scheduler.add_job(self.execute_split_job, "interval", seconds=60)
        # heart_beat
        self.blocking_scheduler.add_job(self.heart_beat, "interval", seconds=60)
        self.blocking_scheduler.start()

    @abc.abstractmethod
    def get_validated_data_params(self, task_item_id: int, data: str) -> dict or None:
        pass

    @abc.abstractmethod
    def export(self, task_item: DownloadItem, data_obj: dict) -> tuple:
        pass

    @abc.abstractmethod
    def split_task(self, task: DownloadTaskMain) -> list:
        pass


class Repository(object):

    def __init__(self, config: Config):
        # 数据库连接池
        self.db = mysql_util.db(config.db_config.host,
                                config.db_config.port,
                                config.db_config.user,
                                config.db_config.password,
                                config.db_config.db_name)
        self._logger = loguru.logger

    def get_download_task_ready(self, sub_type):
        """
        获取download_task列表
        :return:
        """
        limit_time = common_utils.get_date_around_today(days=-3, origin_date=date.today())
        sql = "select * from download_task_main where created_time > %(limit_time)s and sub_type = %(sub_type)s and status = %(status)s limit 1000"
        download_tasks = self.db.select_by_param(sql,
                                                 {'status': TaskStatus.READY.value, 'sub_type': sub_type,
                                                  'limit_time': limit_time})
        return download_tasks

    def update_download_status(self, task_id, status):
        """
        更新任务状态
        :param update_task:
        :return:
        """
        sql = "update download_task_main set status = %(status)s where id =  %(taskId)s"
        self.db.execute(sql, {'status': status, 'taskId': task_id})

    def get_task_item(self, item_id):
        """
        获取任务数据
        :param item_id:
        :return:
        """
        sql = f"select * from download_item where id = {item_id}"
        return self.db.select_one(sql)

    def get_download_task_items(self, task_id, status):
        """
        通过task_id status获取列表
        :param task_id:
        :param status:
        :return:
        """
        sql = f"select * from download_item where task_id = {task_id} and status = {status}"
        return self.db.select(sql)

    def finish_task_with_error(self, item_id, data=None, message="未知错误"):
        """
        失败更新
        :param item_id:
        :param data:
        :param message:
        :return:
        """
        if data is None:
            data = json.dumps({'error': message}, ensure_ascii=False)
        else:
            if common_utils.is_json(data):
                data = json.loads(data, encoding="utf-8")
                data['error'] = message
                data = json.dumps(data, ensure_ascii=False)
            else:
                data += message
        try:
            sql = f"update download_item set data = '{data}', status = {ItemStatus.VALID.value} where id = {item_id}"
            self.db.execute(sql)
        except Exception as e:
            loguru.logger.exception(e)
            raise Exception(e)

    def update_success_item(self, item_id, url, md5, file_name):
        """
        成功更新
        :param item_id:
        :param url:
        :return:
        """
        try:
            invalid_time = common_utils.get_date_around_today(days=+3, origin_date=datetime.now())
            sql = "update download_item set status = %(status)s, url = %(url)s , md5_value = %(md5)s, expire_time = %(invalid_time)s, file_name = %(file_name)s where id = %(item_id)s"
            self.db.execute(sql, {
                'status': ItemStatus.VALID.value,
                'url': url, 'md5': md5, 'invalid_time': invalid_time, 'file_name': file_name, 'item_id': item_id
            })
            self._logger.info(f"[ID:{item_id}]任务状态已完成, url:{url}, md5:{md5}")
        except Exception as e:
            self._logger.exception(e)
            raise Exception(e)

    def update_processing_item(self, item_id):
        """
        进行中更新
        :param item_id:
        :return:
        """
        try:
            sql = f"update download_item set status = {ItemStatus.PROCESSING.value} where id = {item_id}"
            self.db.execute(sql)
            self._logger.info(f"[ID:{item_id}]任务状态正在进行中")
        except Exception as e:
            self._logger.exception(e)
            raise Exception(e)

    def get_running_items(self, item_type):
        """
        获取正在进行中的任务
        :return:
        """
        start_time = (datetime.now() - timedelta(days=1)).strftime(constants.DEFAULT_DATETIME_FORMAT)
        end_time = datetime.now().strftime(constants.DEFAULT_DATETIME_FORMAT)
        sql = f"select * from download_item where type = {item_type} and status = 1 and created_time between '{start_time}' and '{end_time}'"
        return self.db.select(sql)

    def insert_download_items(self, items):
        sql = " insert into download_item (file_name,type,task_id,org_id,data,status,created_time,last_updated_time) values (%s,%s,%s,%s,%s,%s,%s,%s)"
        self.db.executemany(sql, items)
