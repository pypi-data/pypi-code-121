import functools
import time
import json

from ..logging.interface import LoggerInterface


class Rabbit:
    X_MAX_PRIORITY = 'x-max-priority'
    X_LIMIT_PRIORITY = 100
    X_LIMIT_HEARTBEAT = 600
    X_LIMIT_PREFETCH = 1

    CONTENT_TYPE = 'application/json'

    URL_FORMAT = 'amqp://{}:{}@{}:{}/{}'

    def __init__(self,
                 logger: LoggerInterface,
                 pika,
                 host: str,
                 port: int,
                 user: str,
                 password: str,
                 vhost: str,
                 exchange: str,
                 consumer_tag='',
                 exchange_type='direct',
                 logger_unique_tag='rabbit-debug'
                 ):

        self.__exchange = exchange
        self.__exchange_type = exchange_type
        self.__exchange_durable = True

        self.__request_queue = None

        self.__pika = pika

        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password

        self.__virtual_host = vhost

        self.__custom_consumer_tag = consumer_tag

        self.__logger = logger
        self.__logger_unique_tag = logger_unique_tag

        self.__priority = self.X_LIMIT_PRIORITY
        self.__heartbeat = self.X_LIMIT_HEARTBEAT
        self.__prefetch_count = self.X_LIMIT_PREFETCH

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False
        self._method = None

        self.callback = None
        self.should_reconnect = False
        self.was_consuming = False

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by self.__pika.
        :rtype: self.__pika.SelectConnection
        """
        self.__logger.debug('Connecting to Server', self.__logger_unique_tag, self.__class__.__name__)

        credentials = self.__pika.PlainCredentials(
            username=self.__user,
            password=self.__password
        )

        parameters = self.__pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            virtual_host=self.__virtual_host,
            credentials=credentials,
            blocked_connection_timeout=self.__heartbeat,
            heartbeat=self.__heartbeat
        )

        return self.__pika.SelectConnection(
            parameters=parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def connect_blocking(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by self.__pika.

        :rtype: self.__pika.SelectConnection

        """
        self.__logger.debug('Connecting to {}'.format(self.url), self.__logger_unique_tag, self.__class__.__name__)

        credentials = self.__pika.PlainCredentials(
            username=self.__user,
            password=self.__password
        )

        parameters = self.__pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            virtual_host=self.__virtual_host,
            credentials=credentials
        )

        return self.__pika.BlockingConnection(parameters)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            self.__logger.debug('Connection is closing or already closed', self.__logger_unique_tag,
                                self.__class__.__name__)
        else:
            self.__logger.debug('Closing connection', self.__logger_unique_tag, self.__class__.__name__)
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param self.__pika.SelectConnection _unused_connection: The connection
        """
        self.__logger.debug('Connection opened', self.__logger_unique_tag, self.__class__.__name__)
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param self.__pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        # self._logging.error('Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param self.__pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            # self._logging.warning_ext('Connection closed, reconnect necessary: %s', reason)
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
        on_channel_open callback will be invoked by self.__pika.
        """
        self.__logger.debug('Creating a new channel', self.__logger_unique_tag, self.__class__.__name__)
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param self.__pika.channel.Channel channel: The channel object
        """
        self.__logger.debug('Channel opened', self.__logger_unique_tag, self.__class__.__name__)
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.exchange)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        self.__logger.debug('Adding channel close callback', self.__logger_unique_tag, self.__class__.__name__)
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param self.__pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        # self._logging.warning_ext('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by self.__pika.
        :param str|unicode exchange_name: The name of the exchange to declare
        """
        self.__logger.debug('Declaring exchange: {}'.format(exchange_name), self.__logger_unique_tag,
                            self.__class__.__name__)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            self.on_exchange_declareok, userdata=exchange_name)

        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self.__exchange_type,
            # todo: add to init
            durable=self.__exchange_durable,
            callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param self.__pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        :param str|unicode userdata: Extra user data (exchange name)
        """
        self.__logger.debug('Exchange declared: {}'.format(userdata), self.__logger_unique_tag, self.__class__.__name__)
        self.setup_queue(self.__request_queue)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by self.__pika.
        :param str|unicode queue_name: The name of the queue to declare.
        """
        self.__logger.debug('Declaring queue {}'.format(queue_name), self.__logger_unique_tag, self.__class__.__name__)
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        # self._channel.queue_declare(queue=queue_name, callback=cb)

        self._channel.queue_declare(callback=cb, queue=queue_name, passive=False, durable=True,
                                    arguments={self.X_MAX_PRIORITY: int(self.__priority)})

    def on_queue_declareok(self, _unused_frame, userdata):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by self.__pika.
        :param self.__pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        queue_name = userdata
        self.__logger.debug('Binding {} to {} with {}'.format(self.exchange, queue_name, queue_name),
                            self.__logger_unique_tag, self.__class__.__name__)
        cb = functools.partial(self.on_bindok, userdata=queue_name)
        self._channel.queue_bind(
            queue=queue_name,
            exchange=self.exchange,
            routing_key=queue_name,
            callback=cb)

    def setup_queue_custom(self, queue_name, routing_key=None, priority=None):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by self.__pika.
        queue_bind        :param str|unicode queue_name: The name of the queue to declare.

        """
        self.__logger.debug("Declaring queue {}".format(queue_name), self.__logger_unique_tag, self.__class__.__name__)

        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name,
                                    passive=False,
                                    durable=True,
                                    arguments={
                                        self.X_MAX_PRIORITY: int(self.__priority) if not priority else int(
                                            priority)})
        if routing_key:
            self.__logger.debug("Bind queue {} {} {}".format(self.exchange, queue_name, routing_key),
                                self.__logger_unique_tag, self.__class__.__name__)
            self._channel.queue_bind(exchange=self.exchange, queue=queue_name, routing_key=routing_key)

    def on_bindok(self, _unused_frame, userdata):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.
        :param self.__pika.frame.Method _unused_frame: The Queue.BindOk response frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        self.__logger.debug('Queue bound: {}'.format(userdata), self.__logger_unique_tag, self.__class__.__name__)
        self.set_qos()

    def set_qos(self):
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._channel.basic_qos(
            prefetch_count=self.__prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param self.__pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        self.__logger.debug('QOS set to: {}'.format(self.__prefetch_count), self.__logger_unique_tag,
                            self.__class__.__name__)
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
        self.__logger.debug('Issuing consumer related RPC commands {}'.format(self.callback), self.__logger_unique_tag,
                            self.__class__.__name__)
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self.__request_queue, self.callback, consumer_tag=self.consumer_tag)
        self.was_consuming = True
        self._consuming = True

    def publish_message(self, json_message, routing_key, priority=1, exchange='', hdrs=None):
        """If the class is not stopping, publish a message to RabbitMQ,
        appending a list of deliveries with the message number that was sent.
        This list will be used to check for delivery confirmations in the
        on_delivery_confirmations method.

        Once the message has been sent, schedule another message to be sent.
        The main reason I put scheduling in was just so you can get a good idea
        of how the process is flowing by slowing down and speeding up the
        delivery intervals by changing the PUBLISH_INTERVAL constant in the
        class.

        """
        self.__logger.debug('Publish message', self.__logger_unique_tag, self.__class__.__name__)

        while self._channel is None or not self._channel.is_open:
            self.__logger.error("_channel is {}".format(self._channel))
            self.run_blocking()

        properties = self.__pika.BasicProperties(delivery_mode=2,
                                                 priority=priority,
                                                 content_type=self.CONTENT_TYPE,
                                                 headers=hdrs if hdrs else {})

        send = False

        try:
            json_message = json.dumps(json.loads(json_message), default=lambda o: o.__dict__, indent=4)
        except:
            json_message = json.dumps(json_message, default=lambda o: o.__dict__, indent=4)
            pass

        while not send:
            try:
                self._channel.basic_publish(
                    exchange=self.exchange if not exchange else exchange,
                    routing_key=routing_key,
                    body=json_message,
                    properties=properties)

                self.__logger.debug(
                    "Message {} bytes sent routing_key {}, priority {}".format(len(json_message), routing_key,
                                                                               priority), self.__logger_unique_tag,
                    self.__class__.__name__)
                return True
            except self.__pika.connection.exceptions.ConnectionClosed as exc:
                self.__logger.warning(
                    'Error. Connection closed, and the message was never delivered. Sleep 5 sec, Message = {}'.format(
                        json_message))
                pass

            try:
                self.run_blocking()
            except Exception:
                self.__logger.exception('Error during reconnect')
                raise
            time.sleep(5)

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by self.__pika.
        """
        self.__logger.debug('Adding consumer cancellation callback', self.__logger_unique_tag, self.__class__.__name__)
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param self.__pika.frame.Method method_frame: The Basic.Cancel frame
        """
        self.__logger.debug('Consumer was cancelled remotely, shutting down: {}'.format(method_frame),
                            self.__logger_unique_tag, self.__class__.__name__)
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.
        :param self.__pika.channel.Channel _unused_channel: The channel object
        :param self.__pika.Spec.Basic.Deliver: basic_deliver method
        :param self.__pika.Spec.BasicProperties: properties
        :param bytes body: The message body
        """
        pass

        # self._logging.debug_ext('Received message # %s from %s: %s',
        #            basic_deliver.delivery_tag, properties.app_id, body)
        # self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message_manual(self):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.
        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        """
        self.__logger.debug('Acknowledging message {}'.format(self._method.delivery_tag), self.__logger_unique_tag,
                            self.__class__.__name__)
        self._channel.basic_ack(self._method.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.
        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        """
        self.__logger.debug('Acknowledging message {}'.format(delivery_tag), self.__logger_unique_tag,
                            self.__class__.__name__)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.
        """
        if self._channel:
            self.__logger.debug('Sending a Basic.Cancel RPC command to RabbitMQ', self.__logger_unique_tag,
                                self.__class__.__name__)
            cb = functools.partial(
                self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.
        :param self.__pika.frame.Method _unused_frame: The Basic.CancelOk frame
        :param str|unicode userdata: Extra user data (consumer tag)
        """
        self._consuming = False
        self.__logger.debug('RabbitMQ acknowledged the cancellation of the consumer: {}'.format(userdata),
                            self.__logger_unique_tag, self.__class__.__name__)
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.
        """
        self.__logger.debug('Closing the channel', self.__logger_unique_tag, self.__class__.__name__)
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def run_blocking(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        self._connection = self.connect_blocking()
        self._channel = self._connection.channel()

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
            self.__logger.debug('Stopping', self.__logger_unique_tag, self.__class__.__name__)
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            self.__logger.debug('Stopped', self.__logger_unique_tag, self.__class__.__name__)

    def stop_blocking(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        self._closing = True
        self._connection.close()
        self.__logger.debug('Stopped', self.__logger_unique_tag, self.__class__.__name__)

    @property
    def consumer_tag(self) -> str:
        return self.__custom_consumer_tag

    @consumer_tag.setter
    def consumer_tag(self, tag: str):
        self.__custom_consumer_tag = tag

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method

    @property
    def queue(self):
        return self.__request_queue

    @queue.setter
    def queue(self, queue):
        self.__request_queue = queue

    @property
    def exchange(self):
        return self.__exchange

    @property
    def url(self):
        return self.URL_FORMAT.format(self.__user, self.__password, self.__host, self.__port, self.__virtual_host)
