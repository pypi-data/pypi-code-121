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


import logging
import asyncio
from threading import Thread
from contextlib import suppress

import aio_pika

from google.protobuf.pyext._message import SetAllowOversizeProtos

from th2_common.schema.message.configuration.message_configuration import ConnectionManagerConfiguration
from th2_common.schema.message.impl.rabbitmq.configuration.rabbitmq_configuration import RabbitMQConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.consumer import Consumer
from th2_common.schema.message.impl.rabbitmq.connection.publisher import Publisher
from th2_common.schema.metrics.common_metrics import HealthMetrics


logger = logging.getLogger(__name__)


class ConnectionManager:
    """Initializes RabbitMQ Publisher and Consumer.

        Channel and connection are created for publisher and consumer during initialization.

    :param :class: `RabbitMQConfiguration` configuration: Used as connection parameters to connect with RabbitMQ
    :param :class: `ConnectionManagerConfiguration` connection_manager_configuration: Used to save configuration
    parameters for Consumer
    """

    def __init__(self, configuration: RabbitMQConfiguration,
                 connection_manager_configuration: ConnectionManagerConfiguration) -> None:

        SetAllowOversizeProtos(connection_manager_configuration.message_recursion_limit > 100)

        self.__metrics = HealthMetrics(self)

        self.connection_parameters = {
            'host': configuration.host,
            'port': configuration.port,
            'login': configuration.username,
            'password': configuration.password,
            'virtualhost': configuration.vhost
        }

        self.consumer = Consumer(connection_manager_configuration,
                                 self.connection_parameters)
        self.publisher = Publisher(self.connection_parameters)

        self._loop = asyncio.get_event_loop()
        self.publisher_consumer_thread = Thread(target=self._start_background_loop)
        self.publisher_consumer_thread.start()

        self.consumer_future = asyncio.run_coroutine_threadsafe(self.consumer.connect(), self._loop)
        self.consumer_future.result()

        self.publisher_future = asyncio.run_coroutine_threadsafe(self.publisher.connect(), self._loop)
        self.publisher_future.result()

        self.__metrics.enable()

    def _start_background_loop(self) -> None:
        """Set and run event loop in the thread forever"""

        asyncio.set_event_loop(self._loop)
        self._loop.set_exception_handler(self._handle_exception)
        self._loop.run_forever()

    def _handle_exception(self, loop, context) -> None:
        """Custom exception handling"""

        if isinstance(context.get('exception'), aio_pika.exceptions.CONNECTION_EXCEPTIONS):
            pass
        elif context['message']:
            logger.error(context['message'])

    def close(self) -> None:
        """Closing consumer's and publisher's channel and connection."""

        try:
            logger.info('Closing Consumer')
            stopping_consumer = asyncio.run_coroutine_threadsafe(self.consumer.stop(), self._loop)
            stopping_consumer.result()
        except Exception as e:
            logger.exception(f'Error while stopping Consumer: {e}')
        try:
            logger.info('Closing Publisher')
            stopping_publisher = asyncio.run_coroutine_threadsafe(self.publisher.stop(), self._loop)
            stopping_publisher.result()
        except Exception as e:
            logger.exception(f'Error while stopping Publisher: {e}')

        graceful_shutdown = asyncio.run_coroutine_threadsafe(self._cancel_pending_tasks(), self._loop)
        graceful_shutdown.result()

    async def _cancel_pending_tasks(self) -> None:
        """Coroutine that ensures graceful shutdown of event loop"""

        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
                with suppress(asyncio.exceptions.CancelledError):
                    await task
        self._loop.stop()
