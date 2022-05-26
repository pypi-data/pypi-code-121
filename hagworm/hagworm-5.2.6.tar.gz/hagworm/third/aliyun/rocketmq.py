# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from mq_http_sdk.mq_client import MQClient as _MQClient
from mq_http_sdk.mq_consumer import MQConsumer as _MQConsumer
from mq_http_sdk.mq_producer import MQProducer as _MQProducer, MQTransProducer as _MQTransProducer, TopicMessage
from mq_http_sdk.mq_exception import MQServerException, MQClientNetworkException

from ...extend.interface import TaskInterface
from ...extend.asyncio.base import Utils, AsyncCirculator
from ...extend.asyncio.task import IntervalTask
from ...extend.asyncio.future import ThreadPool


CLIENT_WAIT_TIMEOUT = 10
CLIENT_ERROR_RETRY_COUNT = 5


class MQConsumer(_MQConsumer):

    async def consume_message(self, batch_size=1, wait_seconds=-1):

        return await self.mq_client.thread_run(super().consume_message, batch_size, wait_seconds)

    async def ack_message(self, messages):

        receipt_handle_list = [msg.receipt_handle for msg in messages]

        return await self.mq_client.thread_run(super().ack_message, receipt_handle_list)


class MQProducer(_MQProducer):

    async def publish_message(self, msg_body, msg_tag=r''):

        return await self.mq_client.thread_run(super().publish_message, TopicMessage(msg_body, msg_tag))


class MQTransProducer(_MQTransProducer):

    async def publish_message(self, msg_body, msg_tag=r''):

        return await self.mq_client.thread_run(super().publish_message, TopicMessage(msg_body, msg_tag))

    async def consume_half_message(self, batch_size=1, wait_seconds=-1):

        return await self.mq_client.thread_run(super().consume_half_message, batch_size, wait_seconds)

    async def commit(self, message):

        return await self.mq_client.thread_run(super().commit, message.receipt_handle)

    async def rollback(self, message):

        return await self.mq_client.thread_run(super().rollback, message.receipt_handle)


class _TaskMixin(TaskInterface):

    def __init__(self, message_handler):

        self._task = IntervalTask.create(1, self._do_task)

        self._message_handler = message_handler

    def start(self):
        self._task.start()

    def stop(self):
        self._task.stop()

    def is_running(self):
        self._task.is_running()

    async def _do_task(self):
        raise NotImplementedError()


class MQClient(_MQClient):

    def __init__(self, host, access_id, access_key, security_token=r'', debug=False, logger=None):

        super().__init__(host, access_id, access_key, security_token, debug, logger)

        # 原版SDK中的MQClient线程不安全，利用线程池仅有一个线程这种特例，保证线程安全
        self._thread_pool = ThreadPool(1)

    async def thread_run(self, func, *args, **kwargs):

        global CLIENT_ERROR_RETRY_COUNT

        result = None

        # 增加网络异常重试机制
        async for times in AsyncCirculator(max_times=CLIENT_ERROR_RETRY_COUNT):

            try:

                result = await self._thread_pool.run(func, *args, **kwargs)

            except MQClientNetworkException as err:

                if times < CLIENT_ERROR_RETRY_COUNT:
                    Utils.log.warning(err)
                else:
                    raise err

            else:

                break

        return result

    def get_consumer(self, instance_id, topic_name, consumer, message_tag=r''):

        return MQConsumer(instance_id, topic_name, consumer, message_tag, self, self.debug)

    def get_producer(self, instance_id, topic_name):

        return MQProducer(instance_id, topic_name, self, self.debug)

    def get_trans_producer(self, instance_id, topic_name, group_id):

        return MQTransProducer(instance_id, topic_name, group_id, self, self.debug)


class MQMultiProducers:

    def __init__(self, client_num, host, access_id, access_key, security_token=r'', debug=False, logger=None):

        self._clients = [
            MQClient(host, access_id, access_key, security_token, debug, logger)
            for _ in range(client_num)
        ]

        self._producers = None
        self._producers_iter = None

    def init_producers(self, instance_id, topic_name):

        self._producers = [
            client.get_producer(instance_id, topic_name)
            for client in self._clients
        ]

        self._producers_iter = Utils.itertools.cycle(self._producers)

    async def publish_message(self, msg_body, msg_tag=r''):

        producer = next(self._producers_iter)

        return await producer.publish_message(msg_body, msg_tag)


class MQCycleConsumer(MQConsumer, _TaskMixin):

    def __init__(self, message_handler, instance_id, topic_name, consumer, message_tag, mq_client, debug=False):

        MQConsumer.__init__(self, instance_id, topic_name, consumer, message_tag, mq_client, debug)
        _TaskMixin.__init__(self, message_handler)

        self._client_batch_size = 1
        self._client_wait_seconds = CLIENT_WAIT_TIMEOUT

    def set_client_batch_size(self, val):

        self._client_batch_size = val

    def set_client_wait_seconds(self, val):

        self._client_wait_seconds = val

    async def _do_task(self):

        messages = None

        try:
            messages = await self.consume_message(self._client_batch_size, self._client_wait_seconds)
        except MQServerException as err:
            if err.type != r'MessageNotExist':
                Utils.log.error(err)

        if messages:
            await Utils.awaitable_wrapper(
                self._message_handler(self, messages)
            )


class MQMultiCycleConsumers(TaskInterface):

    def __init__(self, client_num, host, access_id, access_key, security_token=r'', debug=False, logger=None):

        self._clients = [
            MQClient(host, access_id, access_key, security_token, debug, logger)
            for _ in range(client_num)
        ]

        self._consumers = None

        self._running = False

    def init_consumers(self,
                       message_handler, instance_id, topic_name, consumer, message_tag, debug=False,
                       *, consumer_cls=MQCycleConsumer
                       ):

        if self._consumers:
            self.stop()

        self._consumers = [
            consumer_cls(message_handler, instance_id, topic_name, consumer, message_tag, client, debug)
            for client in self._clients
        ]

    def set_client_batch_size(self, val):

        if self._consumers:
            for consumer in self._consumers:
                consumer.set_client_batch_size(val)

    def set_client_wait_seconds(self, val):

        if self._consumers:
            for consumer in self._consumers:
                consumer.set_client_wait_seconds(val)

    def start(self):

        if self._running or self._consumers is None:
            return False

        self._running = True

        for consumer in self._consumers:
            consumer.start()

        return True

    def stop(self):

        if not self._running or self._consumers is None:
            return False

        self._running = False

        for consumer in self._consumers:
            consumer.stop()

        return True

    def is_running(self):

        return self._running


class MQCycleTransProducer(MQTransProducer, _TaskMixin):

    def __init__(self, message_handler, instance_id, topic_name, group_id, mq_client, debug=False):

        MQTransProducer.__init__(self, instance_id, topic_name, group_id, mq_client, debug)
        _TaskMixin.__init__(message_handler)

        self._client_batch_size = 1
        self._client_wait_seconds = CLIENT_WAIT_TIMEOUT

    def set_client_batch_size(self, val):

        self._client_batch_size = val

    def set_client_wait_seconds(self, val):

        self._client_wait_seconds = val

    async def _do_task(self):

        messages = None

        try:
            messages = await self.consume_half_message(self._client_batch_size, self._client_wait_seconds)
        except MQServerException as err:
            if err.type != r'MessageNotExist':
                Utils.log.error(err)

        if messages:
            await Utils.awaitable_wrapper(
                self._message_handler(self, messages)
            )


class MQMultiCycleTransProducers(TaskInterface):

    def __init__(self, client_num, host, access_id, access_key, security_token=r'', debug=False, logger=None):

        self._clients = [
            MQClient(host, access_id, access_key, security_token, debug, logger)
            for _ in range(client_num)
        ]

        self._producers = None
        self._producers_iter = None

        self._running = False

    def init_producers(self,
                       message_handler, instance_id, topic_name, group_id, debug=False,
                       *, producer_cls=MQCycleTransProducer
                       ):

        if self._producers:
            self.stop()

        self._producers = [
            producer_cls(message_handler, instance_id, topic_name, group_id, client, debug)
            for client in self._clients
        ]

        self._producers_iter = Utils.itertools.cycle(self._producers)

    def set_client_batch_size(self, val):

        if self._producers:
            for producer in self._producers:
                producer.set_client_batch_size(val)

    def set_client_wait_seconds(self, val):

        if self._producers:
            for producer in self._producers:
                producer.set_client_wait_seconds(val)

    async def publish_message(self, msg_body, msg_tag=r''):

        producer = next(self._producers_iter)

        return await producer.publish_message(msg_body, msg_tag)

    def start(self):

        if self._running or self._producers is None:
            return False

        self._running = True

        for producer in self._producers:
            producer.start()

        return True

    def stop(self):

        if not self._running or self._producers is None:
            return False

        self._running = False

        for producer in self._producers:
            producer.stop()

        return True

    def is_running(self):

        return self._running
