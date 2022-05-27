import datetime
import json

import loguru
import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from redis.client import Pipeline

from duyan_download_task import constants
from duyan_download_task.constants import TaskStatus, ItemStatus
from duyan_download_task.model import DownloadTaskMain, DownloadItem
from duyan_download_task.task import SubTypeInfo
from duyan_download_task.utils import mysql_util, common_utils
from duyan_download_task.utils.config_util import Config
from duyan_download_task.utils.logger_util import LOG

SUB_TYPE_QUEUE_DICT = {}  # TODO 放到redis 由子任务脚本注册
SUB_TYPE_INFO_DICT = {}


class DownloadTaskScheduler(object):
    """
    调度任务启动类
    """

    def __init__(self, config_path, log_path, cron="0 0-59/2 * * * *"):
        self.cron = common_utils.get_cron_trigger_for_str(cron)
        self.task_dispatcher = CtiDownloadTaskDispatcher(config_path, log_path)
        self.task_status_manager = CtiDownloadTaskStatusManager(config_path, log_path)
        self.blocking_scheduler = BlockingScheduler()

    def heart_beat(self):
        loguru.logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ heart beat ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    def start(self):
        self.blocking_scheduler.add_job(self.task_dispatcher.execute_job, trigger=self.cron,
                                        next_run_time=datetime.datetime.now(), max_instances=1)
        self.blocking_scheduler.add_job(self.task_status_manager.execute_job, trigger=self.cron,
                                        next_run_time=datetime.datetime.now(), max_instances=1)
        # heart_beat
        self.blocking_scheduler.add_job(self.heart_beat, "interval", seconds=60)
        self.blocking_scheduler.start()


class CtiDownloadTaskDispatcher(object):
    """
    download_item任务分发到不同队列
    """

    def __init__(self, config_path, log_path):
        # 配置
        self._config = Config(config_path)
        self._logger = LOG.get_logger(log_path, enqueue=True)
        self.repository = Repository(self._config)
        # redis链接池
        self._redisPool = redis.ConnectionPool(host=self._config.redis_config.host,
                                               port=self._config.redis_config.port,
                                               password=self._config.redis_config.password,
                                               db=self._config.redis_config.db)
        # redis客户端
        self._redisCli = redis.Redis(connection_pool=self._redisPool)

    @loguru.logger.catch
    def execute_job(self) -> object:
        self.get_and_refresh_task_info()
        update_task = list()
        # 数据查询分组
        download_tasks = self.repository.get_download_tasks()
        self._logger.info(f"获取到download_tasks数据:[{len(download_tasks)}]条")
        # 推任务到队列
        pip = self._redisCli.pipeline(transaction=True)
        for download_task in download_tasks:
            download_task_po = DownloadTaskMain(download_task)
            # 不处理通话记录导出
            # if not is_call_log_task(download_task_po.type) and not is_pre_download_task(download_task_po.sub_type):
            task_id = download_task_po.id
            # 非多子任务任务直接推队列
            task_info = SUB_TYPE_INFO_DICT.get(download_task_po.sub_type)
            if not task_info.is_multi_task:
                # 筛选item
                this_items = self.repository.get_download_items(task_id)
                # 未查到 跳过
                if this_items is None or len(this_items) == 0:
                    continue
                # 推item到队列
                self.push_item_to_queue(this_items, pip)
                update_task.append(task_id)
        # 更新任务状态
        if update_task:
            self.repository.update_download_status(update_task=update_task)
            self._logger.info(f"download_task[{update_task}]加入任务队列成功")
            # pip执行
            pip.execute()
        pip.close()
        return None

    def push_item_to_queue(self, items: list, pipeline: Pipeline):
        """
        推任务到队列
        :param items:
        :param pipeline:
        :return:
        """
        for item in items:
            download_item_po = DownloadItem(item)
            # 预约下载跳过
            # if is_pre_download_task(download_item_po.type):
            #     continue
            sub_type = download_item_po.type
            item_id = download_item_po.id
            queue_key = SUB_TYPE_QUEUE_DICT.get(sub_type)
            if queue_key is not None:
                pipeline.rpush(queue_key, item_id)
                self._logger.info(f"download_item[ID:{item_id}]加入任务队列{queue_key}成功,sub_type:{sub_type}")
            else:
                self._logger.error(f"不存在的子类型,download_item[ID]:{item_id},sub_type:{sub_type}")

    def get_and_refresh_task_info(self):
        """
        刷新任务信息
        :return:
        """
        results = self._redisCli.hgetall(constants.TASK_INFO_KEY)
        if results:
            for key, value in results.items():
                key = int(bytes.decode(key))
                value = bytes.decode(value)
                info_arr = json.loads(value)
                info = SubTypeInfo(info_arr[0], info_arr[1], info_arr[2], info_arr[3], info_arr[4])
                SUB_TYPE_QUEUE_DICT[key] = info.queue_key
                SUB_TYPE_INFO_DICT[key] = info


class CtiDownloadTaskStatusManager(object):
    """
    所有item任务完成后更新task状态为已完成
    """

    def __init__(self, config_path, log_path):
        # 配置
        self._config = Config(config_path)
        self._logger = LOG.get_logger(log_path, enqueue=True)
        self.repository = Repository(self._config)

    @loguru.logger.catch
    def execute_job(self) -> object:

        # 进行中任务 跟新为完成的任务 或 失败的任务
        complete_task = []
        fail_task = []
        download_tasks = self.repository.get_download_tasks_processing()
        for download_task in download_tasks:
            download_task_po = DownloadTaskMain(download_task)
            # 预约每日下载直接跳过 不更新完成和失败状态
            # if is_everyday_pre_download_task(download_task_po.sub_type):
            #     continue
            this_items = self.repository.get_all_download_items(download_task_po.id)
            # 完成
            this_items_success = list(filter(lambda x: DownloadItem(x).status == ItemStatus.VALID.value, this_items))
            if len(this_items) > 0 and len(this_items) == len(this_items_success):
                complete_task.append(download_task_po.id)
                continue
            # 失败
            fail_items = list(filter(lambda x: DownloadItem(x).status == TaskStatus.FAIL.value, this_items))
            if len(this_items) > 1:
                # 多子任务 全部失败才失败
                fail = (len(this_items) - len(fail_items)) == 0
            else:
                # 其他只要失败就失败
                fail = len(fail_items) > 0
            if fail:
                fail_task.append(download_task_po.id)
                continue

        # 完成的任务更新为 过期
        expire_task = []
        expire_items = []
        # now_timestamp = datetime.datetime.now().timestamp()

        # item 过期
        valid_items = self.repository.get_need_expire_items()
        for valid_item in valid_items:
            expire_items.append(valid_item.get('id'))

        # task_main 过期
        valid_tasks = self.repository.get_download_tasks_valid()
        for valid_task in valid_tasks:
            download_task_po = DownloadTaskMain(valid_task)
            # 预约每日下载直接跳过 不更新失效
            # if is_everyday_pre_download_task(download_task_po.sub_type):
            #     continue
            # task 所有非带参item都过期 过期task
            exceed_items = self.repository.get_download_items_by_task_id_and_status(download_task_po.id,
                                                                                    ItemStatus.EXCEED.value)
            real_items = self.repository.get_all_download_items(download_task_po.id)
            if len(exceed_items) > 0 and len(exceed_items) == len(real_items):
                expire_task.append(download_task_po.id)
                continue

        # 跟新状态
        if len(complete_task) > 0:
            self.repository.update_task_status(TaskStatus.VALID, complete_task)
            self._logger.info(f"已完成下载任务ID列表{complete_task}")
        if len(fail_task) > 0:
            self.repository.update_task_status(TaskStatus.FAIL, fail_task)
            self._logger.info(f"已失败下载任务ID列表{fail_task}")
        if len(expire_task) > 0:
            self.repository.update_task_status(TaskStatus.EXCEED, expire_task)
            self._logger.info(f"已过期下载任务ID列表{expire_task}")
        if len(expire_items) > 0:
            self.repository.update_task_item_status(TaskStatus.EXCEED, expire_items)
            self._logger.info(f"已过期下载任务ITEM_ID列表{expire_items}")
        return None


class Repository(object):

    def __init__(self, config: Config):
        # 数据库连接池
        self._mysqlPool = mysql_util.db(config.db_config.host,
                                        config.db_config.port,
                                        config.db_config.user,
                                        config.db_config.password,
                                        config.db_config.db_name)

    def get_download_tasks(self) -> list:
        """
        获取download_task列表
        :return:
        """
        limit_time = common_utils.get_date_around_today(days=-3, origin_date=datetime.date.today())
        sql = "select * from download_task_main where created_time > %(limit_time)s and status = %(status)s limit 1000"
        download_tasks = self._mysqlPool.select_by_param(sql,
                                                         {'status': TaskStatus.READY.value, 'limit_time': limit_time})
        return download_tasks

    def get_download_items(self, download_task_id) -> list:
        """
        获取download_items列表
        :param download_task_id:
        :return:
        """
        sql = "select * from download_item where task_id = %(taskId)s and status = %(status)s"
        return self._mysqlPool.select_by_param(sql, {'taskId': download_task_id, "status": 0})

    def update_download_status(self, update_task: list) -> None:
        """
        更新任务状态
        :param update_task:
        :return:
        """
        if len(update_task) > 0:
            sql = "update download_task_main set status = %(status)s where id in  %(taskIds)s"
            self._mysqlPool.execute(sql,
                                    {'status': TaskStatus.PROCESSING.value, 'taskIds': update_task})

    def get_download_tasks_processing(self) -> list:
        """
        获取download_task列表
        :return:
        """
        limit_time = common_utils.get_date_around_today(days=-7, origin_date=datetime.date.today())
        sql = "select * from download_task_main where created_time > %(limit_time)s and status = %(status)s limit 1000"
        download_tasks = self._mysqlPool.select_by_param(sql,
                                                         {'status': TaskStatus.PROCESSING.value,
                                                          'limit_time': limit_time})
        return download_tasks

    def get_download_tasks_valid(self) -> list:
        """
        获取download_task列表
        :return:
        """
        limit_time = common_utils.get_date_around_today(days=-7, origin_date=datetime.date.today())
        sql = "select * from download_task_main where created_time > %(limit_time)s and status = %(status)s limit 1000"
        download_tasks = self._mysqlPool.select_by_param(sql,
                                                         {'status': TaskStatus.VALID.value,
                                                          'limit_time': limit_time})
        return download_tasks

    def get_download_items_by_task_id_and_status(self, download_task_id: int, status: int) -> list:
        """
        获取download_items列表
        :param download_task_id:
        :return:
        """
        sql = "select * from download_item where task_id = %(taskId)s and status = %(status)s"
        return self._mysqlPool.select_by_param(sql, {'taskId': download_task_id, 'status': status})

    def update_task_status(self, status: TaskStatus, task_ids: list):
        """
        更新任务状态
        :param status:
        :param task_ids:
        :return:
        """
        sql = "update download_task_main set status = %(status)s where id in  %(taskIds)s"
        self._mysqlPool.execute(sql,
                                {'taskIds': task_ids, 'status': status.value})

    def update_task_item_status(self, status: TaskStatus, item_ids: list):
        """
        跟新item状态
        :param status:
        :param item_ids:
        :return:
        """
        sql = "update download_item set status = %(status)s where id in  %(itemIds)s"
        self._mysqlPool.execute(sql,
                                {'itemIds': item_ids, 'status': status.value})

    def get_all_download_items(self, download_task_id):
        return self._mysqlPool.select_by_param("select * from download_item where task_id = %(id)s",
                                               {"id": download_task_id})

    def get_need_expire_items(self):
        """
        查询需要失效的子任务
        :return:
        """
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = f"select * from download_item where status = 2 and  expire_time < '{now_str}' limit 1000"
        return self._mysqlPool.select(sql)
