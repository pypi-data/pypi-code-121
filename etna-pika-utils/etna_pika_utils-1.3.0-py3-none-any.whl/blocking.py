"""
Module providing wrappers around the pika.BlockingConnection adapter
"""

from time import sleep
from typing import Callable, Optional

import pika
import pika.exceptions

from ._logging import _LOGGER

_DEFAULT_MAX_RECONNECTION_RETRIES = 0
_DEFAULT_BACKOFF_FACTOR = 0.0


class RecoverableBlockingSession:
    """
    Wrapper class around pika.BlockingConnection to support recovering a lost connection
    """

    BACKOFF_MAX_SLEEP_TIME = 120

    def __init__(
        self,
        params: pika.connection.Parameters,
        max_reconnection_retries: int = _DEFAULT_MAX_RECONNECTION_RETRIES,
        backoff_factor: float = _DEFAULT_BACKOFF_FACTOR,
    ):
        """
        :param params:                      the parameters to use when connecting
        :param max_reconnection_retries:    the maximum amount of connection retries that should be performed in a row
        :param backoff_factor:              the back-off factor to use between each connection attempts
        """

        self._params = params
        self._max_reconnection_retries = max_reconnection_retries
        self._backoff_factor = backoff_factor

    def _retry_loop(self) -> pika.BlockingConnection:
        retry_count = 0
        while True:
            try:
                return pika.BlockingConnection(self._params)
            except pika.exceptions.AMQPConnectionError as e:
                retry_count += 1
                if retry_count == self._max_reconnection_retries:
                    _LOGGER.warning("Maximum amount of connection retries exceeded: %r", e)
                    raise e
                sleep(min(self._backoff_factor * (2 ** (retry_count - 1)), self.BACKOFF_MAX_SLEEP_TIME))

    def connect(self) -> pika.BlockingConnection:
        """
        Establish a connection to RabbitMQ using the parameters supplied at construction

        :raise pika.exceptions.AMQPConnectionError: if the maximum amount of retries has been exceeded
        """

        _LOGGER.debug("Connecting to RabbitMQ with parameters: %r", self._params)

        try:
            return pika.BlockingConnection(self._params)
        except pika.exceptions.AMQPConnectionError as e:
            if self._max_reconnection_retries <= 0:
                raise e
            return self._retry_loop()


class RecoverableBlockingPublisher(RecoverableBlockingSession):
    """
    Class providing automatic connection recovery for publishers
    """

    def __init__(
        self,
        params: pika.connection.Parameters,
        configure_channel: Callable[[pika.adapters.blocking_connection.BlockingChannel], None],
        max_reconnection_retries: int = _DEFAULT_MAX_RECONNECTION_RETRIES,
        backoff_factor: float = _DEFAULT_BACKOFF_FACTOR,
    ):
        """
        :param params:                      the parameters to use when connecting
        :param configure_channel:           the callback used to configure the channel after connecting successfully
        :param max_reconnection_retries:    the maximum amount of connection retries that should be performed in a row
        :param backoff_factor:              the back-off factor to use between each connection attempts
        """

        super().__init__(params, max_reconnection_retries, backoff_factor)
        self._configure_channel = configure_channel
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def _connect(self):
        self._connection = self.connect()
        self._channel = self._connection.channel()
        self._configure_channel(self._channel)

    def basic_publish(
        self,
        exchange: str,
        routing_key: str,
        body: bytes,
        properties=None,
        mandatory: bool = False,
    ):
        """
        Publish to the channel with the given exchange, routing key, and body.

        See pika.adapters.blocking_connection.BlockingChannel.basic_publish for details.
        """

        if self._channel is None or self._channel.is_closed:
            self._connect()

        try:
            self._channel.basic_publish(exchange, routing_key, body, properties, mandatory)
        except pika.exceptions.AMQPConnectionError as e:
            _LOGGER.warning("Connection error: %r", e)
            self._connect()
            self._channel.basic_publish(exchange, routing_key, body, properties, mandatory)


class RecoverableBlockingConsumer(RecoverableBlockingSession):
    """
    Class providing automatic connection recovery for consumers
    """

    def __init__(
        self,
        params: pika.connection.Parameters,
        configure_channel: Callable[[pika.adapters.blocking_connection.BlockingChannel], None],
        max_reconnection_retries: int = 0,
        backoff_factor: float = 0.0,
    ):
        """
        :param params:                      the parameters to use when connecting
        :param configure_channel:           the callback used to configure the channel after connecting successfully
        :param max_reconnection_retries:    the maximum amount of connection retries that should be performed in a row
        :param backoff_factor:              the back-off factor to use between each connection attempts
        """

        super().__init__(params, max_reconnection_retries, backoff_factor)
        self._configure_channel = configure_channel
        self._channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def start(self):
        """
        Start the consumption loop
        """

        connecting = True
        while True:
            try:
                connection = self.connect()
                connecting = False
                self._channel = connection.channel()

                self._configure_channel(self._channel)

                _LOGGER.debug("Starting message consumption")
                self._channel.start_consuming()

            except pika.exceptions.AMQPConnectionError as e:
                if connecting is True:
                    break

                _LOGGER.warning("Connection error: %r", e)
                connecting = True
                continue

    def stop(self):
        """
        Stop the consumption loop
        """

        if self._channel is not None and not self._channel.is_closed:
            self._channel.stop_consuming()


class RecoverableBlockingConsumerPublisher:
    def __init__(
        self,
        params: pika.connection.Parameters,
        configure_consumer_channel: Callable[[pika.adapters.blocking_connection.BlockingChannel], None],
        configure_publisher_channel: Callable[[pika.adapters.blocking_connection.BlockingChannel], None],
        max_reconnection_retries: int = _DEFAULT_MAX_RECONNECTION_RETRIES,
        backoff_factor: float = _DEFAULT_BACKOFF_FACTOR,
    ):
        """
        :param params:                      the parameters to use when connecting
        :param configure_consumer_channel:  the callback used to configure the consumer channel after connecting
        :param configure_publisher_channel: the callback used to configure the publisher channel after connecting
        :param max_reconnection_retries:    the maximum amount of connection retries that should be performed in a row
        :param backoff_factor:              the back-off factor to use between each connection attempts
        """
        self.consumer = RecoverableBlockingConsumer(
            params,
            configure_consumer_channel,
            max_reconnection_retries,
            backoff_factor,
        )
        self.publisher = RecoverableBlockingPublisher(
            params,
            configure_publisher_channel,
            max_reconnection_retries,
            backoff_factor,
        )

    def publish(self, *args, **kwargs):
        self.publisher.basic_publish(*args, **kwargs)

    def start_consuming(self):
        self.consumer.start()

    def stop_consuming(self):
        self.consumer.stop()
