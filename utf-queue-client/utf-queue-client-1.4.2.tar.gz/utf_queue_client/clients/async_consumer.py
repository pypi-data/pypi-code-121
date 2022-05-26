import functools
import time
import pika
import pika.channel
import pika.frame
from pika.exchange_type import ExchangeType
from . import Loggable
from typing import Optional, Union, Callable
import regex
from enum import Enum


class MessageContainer:
    def __init__(
        self,
        channel: pika.channel.Channel,
        basic_deliver: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ):
        self.channel: pika.channel.Channel = channel
        self.basic_deliver: pika.spec.Basic.Deliver = basic_deliver
        self.properties: pika.spec.BasicProperties = properties
        self.body: bytes = body


class MessageHandlerError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)


class ExceptionHandlingBehavior(Enum):
    ACK = 0
    NACK = 1
    NONE = 2


class AsyncConsumerBase(Loggable):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, this class will stop and indicate
    that reconnection is necessary. You should look at the output, as
    there are limited reasons why the connection may be closed, which
    usually are tied to permission related issues or socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """

    def __init__(
        self,
        amqp_url: str,
        queue: str,
        message_handler: Callable[[MessageContainer], None],
        durable: bool = False,
        exchange: str = "",
        exchange_type: Optional[ExchangeType] = None,
        routing_key: Optional[str] = None,
        handler_exception_behavior: ExceptionHandlingBehavior = ExceptionHandlingBehavior.NACK,
    ):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self._consuming = False
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._queue = queue
        self._durable = durable
        self._routing_key = routing_key
        self._message_handler = message_handler
        self._handler_exception_behavior = handler_exception_behavior
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count = 1

    @property
    def consuming(self):
        return self._consuming

    @classmethod
    def sanitize_url_for_display(cls, url: str) -> str:
        m: regex.Match = regex.match(
            r"(?<protocol>.+?//)(?<username>.+?):(?<password>.+?)@(?<address>.+)", url
        )
        if m is not None:
            url = url.replace(m.group("password"), "******")
        return url

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        parameters = pika.URLParameters(self._url)
        self.logger.info(f"Connecting to {self.sanitize_url_for_display(self._url)}")
        return pika.SelectConnection(
            parameters=parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed,
        )

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            self.logger.info("Connection is closing or already closed")
        else:
            self.logger.info("Closing connection")
            self._connection.close()

    def on_connection_open(self, _unused_connection: pika.BaseConnection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param pika.SelectConnection _unused_connection: The connection

        """
        self.logger.info("Connection opened")
        self.open_channel()

    def on_connection_open_error(
        self, _unused_connection: pika.BaseConnection, err: Union[str, Exception]
    ):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error

        """
        self.logger.error(f"Connection open failed: {err}")
        self.reconnect()

    def on_connection_closed(
        self, _unused_connection: pika.BaseConnection, reason: Exception
    ):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning(f"Connection closed, reconnect necessary: {reason}")
            self.reconnect()

    def reconnect(self):
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.

        """
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        self.logger.info("Creating a new channel")
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        self.logger.info("Channel opened")
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._exchange)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        self.logger.info("Adding channel close callback")
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel: pika.channel.Channel, reason: Exception):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed

        """
        self.logger.warning(f"Channel {channel} was closed: {reason}")
        self.close_connection()

    def setup_exchange(self, exchange_name: str):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        if exchange_name != "":
            self.logger.info(f"Declaring exchange: {exchange_name}")
            # Note: using functools.partial is not required, it is demonstrating
            # how arbitrary data can be passed to the callback when it is called
            cb = functools.partial(self.on_exchange_declareok, userdata=exchange_name)
            self._channel.exchange_declare(
                exchange=exchange_name, exchange_type=self._exchange_type, callback=cb
            )
        else:
            self.setup_queue(self._queue, self._durable)

    def on_exchange_declareok(self, _unused_frame: pika.frame.Frame, userdata: str):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        :param str|unicode userdata: Extra user data (exchange name)

        """
        self.logger.info(f"Exchange declared: {userdata}")
        self.setup_queue(self._queue, self._durable)

    def setup_queue(self, queue_name: str, durable: bool):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.
        :param bool durable: True if the queue is durable

        """
        self.logger.info(f"Declaring queue {queue_name}")
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name, durable=durable, callback=cb)

    def on_queue_declareok(self, _unused_frame: pika.frame.Frame, userdata: str):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        :param str|unicode userdata: Extra user data (queue name)

        """
        if self._exchange != "":
            queue_name = userdata
            self.logger.info(
                f"Binding {self._exchange} to {queue_name} with {self._routing_key}"
            )
            cb = functools.partial(self.on_bindok, userdata=queue_name)
            self._channel.queue_bind(
                queue_name, self._exchange, routing_key=self._routing_key, callback=cb
            )
        else:
            self.set_qos()

    def on_bindok(self, _unused_frame: pika.frame.Frame, userdata: str):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.

        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        :param str|unicode userdata: Extra user data (queue name)

        """
        self.logger.info(f"Queue bound: {userdata}")
        self.set_qos()

    def set_qos(self):
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.

        """
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok
        )

    def on_basic_qos_ok(self, _unused_frame: pika.frame.Frame):
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame

        """
        self.logger.info(f"QOS set to: {self._prefetch_count}")
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        self.logger.info("Issuing consumer related RPC commands")
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self._queue, self.on_message)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        self.logger.info("Adding consumer cancellation callback")
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame: pika.frame.Method):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        self.logger.info(
            f"Consumer was cancelled remotely, shutting down: {method_frame}"
        )
        if self._channel:
            self._channel.close()

    def handle_message(self, message: MessageContainer):
        if self._message_handler is not None:
            self._message_handler(message)

    def on_message(
        self,
        channel: pika.channel.Channel,
        basic_deliver: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel channel: The channel object
        :param pika.Spec.Basic.Deliver basic_deliver: method
        :param pika.Spec.BasicProperties properties: properties
        :param bytes body: The message body

        """
        self.logger.info(
            f"Received message # {basic_deliver.delivery_tag} from {properties.app_id}"
        )
        try:
            self.handle_message(
                MessageContainer(channel, basic_deliver, properties, body)
            )
            self.acknowledge_message(basic_deliver.delivery_tag)
        except MessageHandlerError:
            if self._handler_exception_behavior == ExceptionHandlingBehavior.NACK:
                self.logger.warning(
                    "MessageHandlerError when handling message -- sending NACK"
                )
                self.nack_message(basic_deliver.delivery_tag)
            elif self._handler_exception_behavior == ExceptionHandlingBehavior.ACK:
                self.logger.warning(
                    "MessageHandlerError when handling message -- sending ACK"
                )
                self.acknowledge_message(basic_deliver.delivery_tag)
            else:
                self.logger.warning(
                    "MessageHandlerError when handling message -- skipping acknowledge"
                )

    def nack_message(self, delivery_tag, requeue=False):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Nack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        :param bool requeue: Attempt to requeue the message

        """
        self.logger.debug(f"NACKing message {delivery_tag}")
        self._channel.basic_nack(delivery_tag, requeue=requeue)

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        self.logger.debug(f"Acknowledging message {delivery_tag}")
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            self.logger.info("Sending a Basic.Cancel RPC command to RabbitMQ")
            cb = functools.partial(self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
        :param str|unicode userdata: Extra user data (consumer tag)

        """
        self._consuming = False
        self.logger.info(
            f"RabbitMQ acknowledged the cancellation of the consumer: {userdata}"
        )
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        self.logger.info("Closing the channel")
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        if not self._closing:
            self._closing = True
            self.logger.info("Stopping")
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            self.logger.info("Stopped")


class ReconnectingConsumer(Loggable):
    """This is a consumer that will reconnect if the nested
    consumer indicates that a reconnect is necessary.
    """

    def __init__(
        self,
        amqp_url: str,
        queue: str,
        message_handler: Callable[[MessageContainer], None],
        durable: bool = False,
        exchange: str = "",
        exchange_type: Optional[ExchangeType] = None,
        routing_key: Optional[str] = None,
    ):
        self._reconnect_delay = 0
        self._amqp_url = amqp_url
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._queue = queue
        self._durable = durable
        self._routing_key = routing_key
        self._message_handler = message_handler
        self._consumer = self.create_consumer()

    def create_consumer(self):
        return AsyncConsumerBase(
            self._amqp_url,
            self._queue,
            self._message_handler,
            self._durable,
            self._exchange,
            self._exchange_type,
            self._routing_key,
        )

    def run(self):
        while True:
            try:
                self._consumer.run()
            except KeyboardInterrupt:
                self._consumer.stop()
                break
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            self.logger.info(f"Reconnecting after {reconnect_delay} seconds")
            time.sleep(reconnect_delay)
            self._consumer = self.create_consumer()

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay


class LocalRaspiSqaTestResultConsumer(ReconnectingConsumer):
    def __init__(
        self,
        hostname: str,
        message_handler: Callable[[MessageContainer], None],
        username: str = None,
        password: str = None,
    ):
        if username is None:
            username = "guest"
        if password is None:
            password = "guest"
        url = f"amqp://{username}:{password}@{hostname}:5672/%2F"
        super().__init__(url, "sqa_test_results", message_handler, durable=True)
