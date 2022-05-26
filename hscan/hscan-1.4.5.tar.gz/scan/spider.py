import datetime
import asyncio
from abc import ABCMeta, abstractmethod
from pymongo.errors import DuplicateKeyError
from scan import logger
from scan.config import Config
from scan.util import get_local_ip, get_local_name, date_to_char, encrypt


class Spider(object):
    __metaclass__ = ABCMeta

    def __init__(self, spider_name, cfg_path):
        self.local_ip = None
        self.container_id = None
        self.rabbitmq = None
        self.mongo_db = None
        self.redis_conn = None
        self.oss_conn = None
        self.task_num = None
        self.spider_name = spider_name
        self.spider_id = self.gen_spider_id()
        self.config = Config(cfg_path)
        self.status = 1

    def gen_spider_id(self):
        self.local_ip = get_local_ip()
        self.container_id = get_local_name()[:12]
        spider_id = self.spider_name + '-' + self.local_ip + '-' + self.container_id
        with open('spider_id', 'w') as f:
            f.write(spider_id)
            f.close()
        return spider_id

    @abstractmethod
    async def process(self, task_info):
        """
        爬虫业务逻辑入口
        :param task_info: 队列任务信息
        :return:
        """

    async def site(self):
        """
        1. 可以对配置文件进行修改
        eg：
            self.config.config.set('client', 'task_num', 1)
        :return:
        2. 可以设置新的成员变量
        eg:
            self.mq2 = ''
        """

    @abstractmethod
    async def init(self):
        """
        初始化数据处理连接
        eg:
            mq_config = self.config.rabbitmq()
            self.rabbitmq = RabbitMQ(host=mq_config.get('host'), port=mq_config.get('port'), user=mq_config.get('user'),
                           password=mq_config.get('password'))
            await self.rabbitmq.init()
        :return:
        """

    async def on_success(self, msg, mongo_conn=None, collection=None, spider_name=None, desc=None, url=None,
                         headers=None):
        """
        处理成功回调
        """
        if not self.mongo_db and not mongo_conn:
            await logger.error('没有mongodb连接信息，不能保存日志')
            return
        if not collection:
            collection = 'spider_success_logs'
        try:
            save_data = {
                "ip": self.local_ip,
                'spider_name': spider_name or self.spider_name,
                'cid': self.container_id,
                'url': url,
                'headers': headers,
                'datetime': str(datetime.datetime.now()),
                'desc': desc,
                'msg': msg
            }
            if mongo_conn:
                await mongo_conn.get_collection(collection).insert_one(save_data)
            else:
                await self.mongo_db.get_collection(collection).insert_one(save_data)
        except Exception as e:
            await logger.error(f'处理成功回调异常:{spider_name}-{self.local_ip}-{self.container_id} {e}')

    async def on_error(self, msg, mongo_conn=None, collection=None, spider_name=None, desc=None, url=None, headers=None):
        """
        处理失败日志记录
        :param collection:
        :param mongo_conn:
        :param spider_name:
        :param desc:
        :param msg: traceback信息
        :param url:
        :param headers:
        """
        await logger.error(msg)
        if not self.mongo_db and not mongo_conn:
            await logger.error('没有mongodb连接信息，不能保存日志')
            return
        if not collection:
            collection = 'spider_error_logs'
        try:
            save_data = {
                "ip": self.local_ip,
                'spider_name': spider_name or self.spider_name,
                'cid': self.container_id,
                'url': url,
                'headers': headers,
                'datetime': str(datetime.datetime.now()),
                'desc': desc,
                'msg': str(msg)
            }
            if mongo_conn:
                await mongo_conn.get_collection(collection).insert_one(save_data)
            else:
                await self.mongo_db.get_collection(collection).insert_one(save_data)
        except Exception as e:
            await logger.error(f'处理失败回调异常:{spider_name}-{self.local_ip}-{self.container_id} {e}')

    async def on_count(self, count_type,  mongo_db=None, collection=None, spider_id=None, count=1):
        """
        计数回调
        :param count_type: 1 成功  0 失败
        :param collection:
        :param mongo_db:
        :param spider_id: spider_name-local_ip-container_id
        :param count:
        :return:
        """
        if count_type not in [1, 0]:
            await logger.error('状态参数异常，不能计数')
            return
        if not mongo_db and not self.mongo_db:
            await logger.error('没有mongodb连接信息，不能计数')
            return
        if not collection:
            collection = 'spider_statistics'
        try:
            # 10分钟一组
            tick = date_to_char('m')[:-1] + '0'
            # 622ea3d44d88e061a3167f33
            # 如 test_spider-192.168.0.182-mac.local-202004261430
            if spider_id:
                count_key = spider_id + '-' + tick
            else:
                count_key = self.spider_id + '-' + tick
            if not mongo_db:
                mongo_db = self.mongo_db
            _id = encrypt(count_key)
            if count_type == 1:
                count_type_key = 'suc_count'
            else:
                count_type_key = 'fail_count'
            try:
                db_data = await mongo_db.get_collection(collection).find_one({'_id': _id})
                if db_data:
                    await mongo_db.get_collection(collection).update_one(
                        {'_id': _id}, {'$inc': {count_type_key: count}})
                else:
                    await mongo_db.get_collection(collection).insert_one(
                        {'_id': _id, 'sid': spider_id, 'date': tick, count_type_key: count})
            except DuplicateKeyError:
                await mongo_db.get_collection(collection).update_one(
                    {'_id': _id}, {'$inc': {'count': count}})
        except Exception as e:
            await logger.error(f'处理成功计数回调异常:{spider_id} {e}')

    async def queue_task(self):
        """
        分布式队列任务，在任务分发使用rabbitmq时
        """
        task_queue = self.config.rabbitmq().get('task_queue')
        if not self.rabbitmq:
            await logger.error('The task queue connection is not initialized')
            return
        arguments = None
        # 优先级队列
        if self.config.rabbitmq().get('priority'):
            arguments = {'x-max-priority': int(self.config.rabbitmq().get('priority'))}
        while self.status:
            try:
                res = await self.rabbitmq.consume(task_queue, arguments=arguments)
                if res:
                    task_info, message = res
                else:
                    await asyncio.sleep(10)
                    continue
                pres = await self.process(task_info)
                if pres:
                    await message.ack()
            except Exception as e:
                await logger.error(e)

    async def simple_task(self):
        """
        单机任务，不使用队列
        """
        while self.status:
            try:
                pres = await self.process(None)
                if pres:
                    pass
            except Exception as e:
                await logger.error(e)

    async def run(self, task_num=None):
        """
        爬虫主程序入口
        :param task_num: 并发数
        """
        # 获取爬虫配置
        await self.site()
        # 初始化并发数
        if task_num and isinstance(task_num, int):
            self.task_num = task_num
        else:
            self.task_num = int(self.config.client().get('task_num'))
        # 初始化数据库配置
        await self.init()
        # 根据任务类型，分发任务
        task_type = self.config.client().get('task_type')
        task_list = []
        if task_type == 'simple':
            for _ in range(self.task_num):
                t = asyncio.create_task(self.simple_task())
                task_list.append(t)
        else:
            for _ in range(self.task_num):
                t = asyncio.create_task(self.queue_task())
                task_list.append(t)
        await asyncio.gather(*task_list)

