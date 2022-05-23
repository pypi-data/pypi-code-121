#   Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import asyncio
import datetime
import logging
import time
from typing import Dict, Optional, Union, Callable, Any, Tuple

import aio_pika
from aio_pika.robust_connection import RobustConnection
from aio_pika.robust_channel import RobustChannel
from aio_pika.robust_queue import RobustQueue
from aio_pika.message import IncomingMessage
from th2_common.schema.message.configuration.message_configuration import ConnectionManagerConfiguration


logger = logging.getLogger(__name__)


class Consumer:
    """Creates Consumer

    `Consumer` implements all methods to create connection and channel for consuming messages, adding subscribers and
    finally closing channel and connection.

    :param :class: `ConnectionManagerConfiguration` connection_manager_configuration:
    :param dict connection_parameters: Provides RabbitMQ configuration parameters for connection
    """

    DELAY_FOR_RECONNECTION = 5
    DEFAULT_SUBSCRIBER_NAME = 'rabbitmq_subscriber'

    def __init__(self,
                 connection_manager_configuration: ConnectionManagerConfiguration,
                 connection_parameters: dict) -> None:

        self._subscriber_name: str = connection_manager_configuration.subscriber_name
        self._prefetch_count: str = connection_manager_configuration.prefetch_count
        self._subscribers: Dict[str, Tuple[RobustQueue, Callable]] = dict()
        self._connection_parameters: Dict[str, Union[str, int]] = connection_parameters
        self._connection: Optional[RobustConnection] = None
        self._channel: Optional[RobustChannel] = None
        self.__consumer_tag_id: int = -1

    async def connect(self) -> None:
        """Coroutine that creates connection, channel for publisher and sets QOS"""

        loop = asyncio.get_running_loop()
        while not self._connection:
            try:
                self._connection = await aio_pika.connect_robust(loop=loop, **self._connection_parameters)
            except Exception as e:
                logger.error(f"Exception was raised while connecting Consumer: {e}")
                time.sleep(Consumer.DELAY_FOR_RECONNECTION)
        logger.info('Connection for Consumer has been created')

        while not self._channel:
            try:
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=self._prefetch_count)
            except Exception as e:
                logger.error(f"Exception was raised while creating channel for Consumer: {e}")
                time.sleep(Consumer.DELAY_FOR_RECONNECTION)
        logger.info(f"Channel for Consumer has been created. QOS set to: {self._prefetch_count}")

    def next_id(self) -> int:
        """Unique id for consumer_tag"""

        self.__consumer_tag_id += 1
        return self.__consumer_tag_id

    def add_subscriber(self, queue_name: str, on_message_callback: Callable[[IncomingMessage], Any]) -> str:
        """ Adding subscriber

        :param str queue_name: Name of the queue from where messages will be consumed
        :param :class: `Callable[[IncomingMessage], Any]` on_message_callback: Called for every
        message consumed

        :return: consumer_tag
        :rtype: str
        """

        if self._subscriber_name is None:
            self._subscriber_name = Consumer.DEFAULT_SUBSCRIBER_NAME
            logger.info(f"Using default subscriber name: '{self._subscriber_name}'")
        consumer_tag = f'{self._subscriber_name}.{self.next_id()}.{datetime.datetime.now()}'

        queue = asyncio.run_coroutine_threadsafe(self._get_queue_coroutine(queue_name),
                                                 self._connection.loop).result()

        self._subscribers[consumer_tag] = (queue, on_message_callback)

        asyncio.run_coroutine_threadsafe(self._start_consuming(consumer_tag),
                                         self._connection.loop)

        return consumer_tag

    async def _get_queue_coroutine(self, queue_name: str) -> RobustQueue:
        """Coroutine that returns robust queue"""

        return await self._channel.get_queue(name=queue_name)

    async def _start_consuming(self, consumer_tag: str) -> None:
        """Coroutine for consuming messages from queue"""

        queue, callback = self._subscribers[consumer_tag]
        await queue.consume(callback=callback, consumer_tag=consumer_tag)

    def remove_subscriber(self, consumer_tag: str) -> None:
        """Remove subscriber and cancel consuming from queue"""

        remove_consumer = asyncio.run_coroutine_threadsafe(self._stop_consuming(consumer_tag), self._connection.loop)
        remove_consumer.result()
        self._subscribers.pop(consumer_tag)

    async def _stop_consuming(self, consumer_tag: str) -> None:
        """Coroutine to cancel consuming from queue"""

        logger.info(f'Sending a Basic.Cancel RPC command to RabbitMQ for tag: {consumer_tag}')
        queue, _ = self._subscribers[consumer_tag]
        await queue.cancel(consumer_tag)
        logger.info(f'RabbitMQ acknowledged the cancellation of the consumer: {consumer_tag}')

    async def stop(self) -> None:
        """Cancel consuming for every subscriber and close connection"""

        for consumer_tag in self._subscribers:
            await self._stop_consuming(consumer_tag)

        await self._connection.close()
