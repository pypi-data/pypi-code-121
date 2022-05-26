import json
import aio_pika
import asyncio
from aio_pika.pool import Pool
from scan.common import logger
from json import JSONDecodeError


class RabbitMQ:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host') or 'localhost'
        self.port = kwargs.get('port') or 5672
        self.user = kwargs.get('user') or 'root'
        self.password = kwargs.get('password') or 'root'
        self.virtualhost = kwargs.get('virtualhost') or '/'
        self.channel_pool = None
        self.loop = None
        self.max_pool_size = 1

    async def init(self, max_pool_size=None):
        if max_pool_size and isinstance(max_pool_size, int):
            self.max_pool_size = max_pool_size
        await self.get_channel_pool()

    async def get_channel_pool(self):
        try:
            if self.loop or self.channel_pool:
                try:
                    await self.channel_pool.close()
                    self.loop.close()
                except Exception as e:
                    await logger.error(f'close error: {e}')
            self.loop = asyncio.get_event_loop()

            async def get_connection():
                return await aio_pika.connect_robust(host=self.host, port=int(self.port), login=self.user,
                                                     password=self.password, virtualhost=self.virtualhost)
            connection_pool = Pool(get_connection, max_size=int(self.max_pool_size), loop=self.loop)

            async def get_channel() -> aio_pika.Channel:
                async with connection_pool.acquire() as connection:
                    return await connection.channel()

            self.channel_pool = Pool(get_channel, max_size=self.max_pool_size, loop=self.loop)
        except Exception as e:
            await logger.error(f'get channel pool error: {e}')
            await asyncio.sleep(30)

    async def consume(self, queue_name, no_ack=False, durable=True, auto_delete=False, arguments=None, qos=1):
        """
        :param qos:
        :param auto_delete:
        :param durable:
        :param no_ack:
        :param arguments: mq绑定参数
        :param queue_name: 队列名
        :return:
        """
        try:
            async with self.channel_pool.acquire() as channel:
                for _ in range(3):
                    try:
                        await channel.set_qos(qos)
                        queue = await channel.declare_queue(queue_name, durable=durable, arguments=arguments,
                                                            auto_delete=auto_delete)
                        async with queue.iterator(no_ack=no_ack) as queue_iter:
                            async for message in queue_iter:
                                body = None
                                try:
                                    body = message.body
                                    data_dict = json.loads(body.decode())
                                    return data_dict, message
                                except JSONDecodeError as e:
                                    await logger.error(f'JSONDecoder error: {e}  data:{body}')
                                except Exception as e:
                                    await logger.error(f'consume msg error: {e}')
                                    await self.get_channel_pool()
                    except Exception as e:
                        await logger.error(f'consume error: {e}')
                        await self.get_channel_pool()
        except Exception as e:
            await logger.error(f'consume process error: {e}')
            await asyncio.sleep(30)
            await self.get_channel_pool()

    async def publish(self, data, routing_key, priority=None):
        """
        :param priority: 消息优先级
        :param data: 要发送的数据
        :param routing_key: 队列名
        :return:
        """
        try:
            async with self.channel_pool.acquire() as channel:
                data = json.dumps(data)
                for _ in range(3):
                    try:
                        await channel.default_exchange.publish(aio_pika.Message(body=data.encode(), priority=priority),
                                                               routing_key=routing_key)
                        return
                    except Exception as e:
                        await logger.error(f'publish error: {e}')
                        await self.get_channel_pool()
        except Exception as e:
            await logger.error(f'publish process error: {e}')
            await asyncio.sleep(30)
            await self.get_channel_pool()

    async def purge(self, queue_name, arguments=None):
        """
        :param arguments: 绑定队列参数
        :param queue_name: 要清空的队列名
        :return:
        """
        try:
            async with self.channel_pool.acquire() as channel:
                for _ in range(3):
                    try:
                        await channel.set_qos(1)
                        queue = await channel.declare_queue(queue_name, durable=True, arguments=arguments,
                                                            auto_delete=False)
                        await queue.purge()
                        return
                    except Exception as e:
                        await logger.error(f'purge error: {e}')
                        await self.get_channel_pool()
        except Exception as e:
            await logger.error(f'purge process error: {e}')
            await asyncio.sleep(30)
            await self.get_channel_pool()

    async def message_count(self, queue_name, arguments=None):
        try:
            async with self.channel_pool.acquire() as channel:
                for _ in range(3):
                    try:
                        await channel.set_qos(1)
                        queue = await channel.declare_queue(queue_name, durable=True, arguments=arguments,
                                                            auto_delete=False)
                        count = queue.declaration_result.message_count
                        return count
                    except Exception as e:
                        await logger.error(f'message_count error: {e}')
                        await self.get_channel_pool()
        except Exception as e:
            await logger.error(f'message_count process error: {e}')
            await asyncio.sleep(30)
            await self.get_channel_pool()


__all__ = RabbitMQ








