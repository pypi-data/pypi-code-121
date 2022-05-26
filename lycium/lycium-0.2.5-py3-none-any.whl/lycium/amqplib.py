#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205
"""
RabbitMQ With Tornado Connection
"""

import sys
import logging
import pika
from typing import Optional, Dict, List, Any
from pika.adapters.tornado_connection import TornadoConnection
import pika.channel
import pika.spec
import tornado.gen
import functools
import uuid
import socket
import json
import time
import copy
# import gevent
# import asyncio
from .supports import singleton, Constant
from .utilities import random_string
from .exceptionreporter import ExceptionReporter

logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
LOGGER = logging.getLogger('components.amqplib')

class _WorkerDelegateType(Constant):
    """
    """
    CONSUMER = 1
    PUBLISHER = 2

WORKER_TYPE = _WorkerDelegateType()

class _RabbitMQDefaults(Constant):
    """
    """
    SOCKET_TIMEOUT = 15
    HEARTBEAT_INTERVAL = 10

RABBIT_MQ_DEFAULTS = _RabbitMQDefaults()

class WorkerDelegate(object):
    """
    """
    worker_type = WORKER_TYPE.CONSUMER
    exchange = 'message'
    exchange_type = 'topic'
    exchange_durable = False
    queue = 'text'
    durable = False
    routing_key = 'example.text'
    callback = None
    auto_ack = True
    registered = False
    prefetch_count = 20

    def __init__(self, workerType, amqpProperties, callback, prefetch_count=20):
        self.worker_type = workerType
        self.durable = amqpProperties.get('durable', True)
        self.exchange = amqpProperties.get('exchange')
        self.exchange_type = amqpProperties.get('exchange_type')
        self.exchange_durable = amqpProperties.get('exchange_durable', self.durable)
        self.queue = amqpProperties.get('queue')
        self.routing_key = amqpProperties.get('routing_key')
        self.auto_ack = amqpProperties.get('auto_ack')
        self.prefetch_count = prefetch_count
        self.worker_tag = '%s:%s:%s' % (self.exchange, self.routing_key, self.queue)
        self.consumer_tag = None
        self.registered = False

        if callable(callback):
            self.callback = callback
        else:
            self.callback = None

    @tornado.gen.coroutine
    def executor(self, worker, ch: pika.channel.Channel, basic_deliver: pika.spec.Basic.Deliver, properties: pika.BasicProperties, body: bytes):
        if callable(self.callback):
            worker._set_reply_needed_message(properties)
            try:
                if tornado.gen.is_coroutine_function(self.callback):
                    resp = yield self.callback(ch, basic_deliver, properties, body)
                else:
                    resp = self.callback(ch, basic_deliver, properties, body)
                if resp and properties.reply_to and properties.correlation_id:
                    if isinstance(resp, (list, dict)):
                        try:
                            resp = json.dumps(resp)
                        except:
                            LOGGER.error('json serialize %s failed with error:%s', str(resp), str(e))
                    if isinstance(resp, (str, bytes)):
                        if properties.correlation_id in worker._processing_replyies:
                            reply_properties = worker._processing_replyies.get(properties.correlation_id, properties)
                            reply_properties.timestamp = int(time.time())
                            LOGGER.debug('reply message(%s) to %s', str(properties.message_id), properties.reply_to)
                            worker.publish('', properties.reply_to, resp, reply_properties)
                return True
            except Exception as e:
                LOGGER.error('Execute consumer callback:%s failed with error:%s', self.callback.__name__, str(e))
                if properties.reply_to and properties.correlation_id and properties.correlation_id in worker._processing_replyies:
                    reply_properties = worker._processing_replyies.get(properties.correlation_id, properties)
                    reply_properties.timestamp = int(time.time())
                    resp = {'code': 500, 'message': str(e)}
                    worker.publish('', properties.reply_to, json.dumps(resp), reply_properties)
                inputs_text = body.decode('utf-8', errors='ignore') if isinstance(body, bytes) else str(body)
                ExceptionReporter().report(key='AMQP-'+str('consume'), typ='AMQP', 
                    endpoint='%s|%s|%s' % (str(basic_deliver.exchange), str(basic_deliver.routing_key), str(basic_deliver.consumer_tag)),
                    method='consume',
                    inputs=inputs_text,
                    outputs='',
                    content=str(e),
                    level='ERROR',
                    extra={
                        'worker_host': worker.worker_hostname,
                        'mq_properties': {
                            'correlation_id': properties.correlation_id if properties.correlation_id else '',
                            'reply_to': properties.reply_to if properties.reply_to else '',
                            'app_id': properties.app_id if properties.app_id else '',
                            'user_id': properties.user_id if properties.user_id else '',
                            'message_id': properties.message_id if properties.message_id else '',
                        }
                    }
                )
                return False
        return False

class PublishesMessage(object):
    """
    """
    exchange = 'message'
    routing_key = 'example.text'
    message: Optional[bytes] = None
    properties: Optional[pika.BasicProperties] = None
    callback: Optional[callable] = None

    def __init__(self, exchange: str, routing_key: str, body: bytes, properties: Optional[pika.BasicProperties] = None, callback: Optional[callable] = None):
        """Constructs a publishing message

        :param str exchange: The exchange name of destination rabbitmq
        :param str routing_key: The routing key of destination rabbitmq
        :param str|bytes body: The message content
        :param pika.BasicProperties properties: The rabbitmq message properties

        """
        self.exchange = exchange
        self.routing_key = routing_key
        self.message = body
        self.properties = properties
        self.callback = callback

class PublishesResponse(object):
    """RPC mq query response
    """

    def __init__(self, ch: pika.channel.Channel, basic_deliver: pika.spec.Basic.Deliver, properties: pika.BasicProperties, body: bytes):
        self.channel: pika.channel.Channel = ch
        self.delivery: pika.spec.Basic.Deliver = basic_deliver
        self.properties: pika.BasicProperties = properties
        self.body: bytes = body

class RabbitMQWorker(object):
    """
    """

    def __init__(self,
                 host='127.0.0.1',
                 port=5672,
                 virtual_host='/',
                 username='guest',
                 password='guest',
                 socket_timeout=RABBIT_MQ_DEFAULTS.SOCKET_TIMEOUT,
                 hb_interval=RABBIT_MQ_DEFAULTS.HEARTBEAT_INTERVAL,
                 publishing_interval=0.1):
        """Constructor

        :param str host: amqp host
        :param int port: amqp port
        :param str virtual_host: amqp virtual_host
        :param str username: amqp user name
        :param str password: amqp password
        :param str socket_timeout: amqp connecting socket timeout
        :param str hb_interval: amqp heartbeat interval

        """
        self._connection_info = 'amqp://%s@%s:%s/%s' % (username, host, str(port), virtual_host)
        LOGGER.debug("initializing amqp connection: %s", self._connection_info)

        super(RabbitMQWorker, self).__init__()

        credentials = pika.PlainCredentials(username, password)
        # parameter
        self._parameters = pika.ConnectionParameters(
            host=host, port=port, virtual_host=virtual_host,
            credentials=credentials, socket_timeout=socket_timeout, heartbeat=hb_interval)
        
        self.publishing_interval = publishing_interval
        self._connection: Optional[TornadoConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
        self._closing = False
        self._custom_ioloop = None
        self._using_outside_ioloop = False
        self._main_thread_ioloop = None
        self._workers: Dict[str, WorkerDelegate] = {}
        self._workers_by_consumer_tag = {}
        self._publishes: List[PublishesMessage] = []
        self._publish_working = False
        self.tracker_queue_name = ''
        self.tracker_message_content = False
        self.worker_hostname = str(socket.gethostname())
        self._rpc_queue_name = 'rpc-%s-%s' % (self.worker_hostname, random_string(8))
        self._rpc_queue: Dict[str, PublishesMessage] = {}
        self._rpc_started: bool = False
        self._processing_replyies: Dict[str, pika.BasicProperties] = {}

    def set_custom_ioloop(self, custom_ioloop):
        """Specifies a custom ioloop, this method should be called before run

        :param None | asyncio.AbstractEventLoop |
            nbio_interface.AbstractIOServices custom_ioloop:
                Defaults to asyncio.get_event_loop().

        """
        self._custom_ioloop = custom_ioloop

    def set_main_thread_ioloop(self, main_thread_ioloop):
        """Specifies a ioloop, this method should be called before run

        :param None | asyncio.AbstractEventLoop |
            nbio_interface.AbstractIOServices main_thread_ioloop:
                Defaults to asyncio.get_event_loop().

        """
        self._main_thread_ioloop = main_thread_ioloop

    def set_using_outside_ioloop(self, using_outside_ioloop):
        """
        """
        self._using_outside_ioloop = using_outside_ioloop

    def connect(self) -> TornadoConnection :
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.adapters.tornado_connection.TornadoConnection

        """
        LOGGER.info('Connecting to %s', self._connection_info)
        self._closing = False
        return TornadoConnection(parameters=self._parameters,
                                 on_open_callback=self.on_connection_open,
                                 on_open_error_callback=self.on_connection_open_error,
                                 on_close_callback=self.on_connection_closed,
                                 custom_ioloop=self._custom_ioloop
                                )

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        LOGGER.info('Closing connection %s', self._connection_info)
        self._connection.close()

    def on_connection_closed(self, connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.

        """
        self._channel = None
        for worker_cfg in self._workers.values():
            worker_cfg.registered = False
        self._publish_working = False
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reopening in 5 seconds: %s',
                           reason)
            self._connection.ioloop.call_later(5, self.reconnect)

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param pika.SelectConnection _unused_connection: The connection

        """
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, connection, exception):
        """
        """
        LOGGER.error('Connecting to %s failed with error:%s, reconnecting', self._connection_info, str(exception))
        self._connection.ioloop.call_later(5, self.reconnect)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        if not self._closing:

            # Create a new connection
            self._connection = self.connect()

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed

        """
        LOGGER.warning('Channel %i was closed: %s', channel, reason)
        if self._connection.is_closed:
            LOGGER.warning('Channel %i closed while connection were close too.', channel)
            return
        self._connection.close()

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.add_on_cancel_callback()

        self.setup_workers()

    def setup_exchange(self, worker_cfg: WorkerDelegate):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param WorkerDelegate worker_cfg: Contains the name of the exchange to declare

        """
        if not worker_cfg.exchange:
            self.setup_queue(worker_cfg)
            return
        LOGGER.info("Declaring exchange '%s'", worker_cfg.exchange)
        self._channel.exchange_declare(worker_cfg.exchange,
                                       worker_cfg.exchange_type,
                                       durable=worker_cfg.exchange_durable,
                                       callback=lambda unused_frame: self.on_exchange_declareok(unused_frame, worker_cfg)
                                      )

    def on_exchange_declareok(self, unused_frame, worker_cfg: WorkerDelegate):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        :param str worker_cfg: WorkerDelegate config

        """
        if worker_cfg.exchange:
            LOGGER.info("Exchange '%s' declared", worker_cfg.exchange)
        self.setup_queue(worker_cfg)

    def setup_queue(self, worker_cfg: WorkerDelegate):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param WorkerDelegate worker_cfg: Contains the name of the queue to declare.

        """
        queue_name = worker_cfg.queue
        if worker_cfg.exchange_type == 'fanout':
            queue_name = ''
            LOGGER.info("Declaring queue '%s'", worker_cfg.queue)
            self._channel.queue_declare(queue_name, durable=False, auto_delete=True,
                                        callback= lambda method_frame : self.on_queue_declareok(method_frame, worker_cfg)
                                        )
        else:
            if worker_cfg.queue.startswith('amq.'):
                self.on_bindok('', worker_cfg)
                return
            LOGGER.info("Declaring queue '%s'", worker_cfg.queue)
            self._channel.queue_declare(queue_name,
                                        durable=worker_cfg.durable,
                                        callback= lambda method_frame : self.on_queue_declareok(method_frame, worker_cfg)
                                        )

    def on_queue_declareok(self, method_frame, worker_cfg: WorkerDelegate):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame
        :param WorkerDelegate worker_cfg: WorkerDelegate config

        """
        LOGGER.info('Declared queue:%s', method_frame.method.queue)
        if 'fanout' == worker_cfg.exchange_type:
            worker_cfg.queue = method_frame.method.queue
            LOGGER.info("Binding '%s' to '%s' with fanout type",
                        worker_cfg.exchange, worker_cfg.queue)
            self._channel.queue_bind(worker_cfg.queue, 
                                     worker_cfg.exchange, '', 
                                     callback= lambda unused_frame : self.on_bindok(unused_frame, worker_cfg)
                                    )
        elif worker_cfg.exchange:
            LOGGER.info("Binding '%s' to '%s' with '%s'",
                        worker_cfg.exchange, worker_cfg.queue, str(worker_cfg.routing_key))
            binding_keys = worker_cfg.routing_key if (isinstance(worker_cfg.routing_key, list) or isinstance(worker_cfg.routing_key, tuple)) else [worker_cfg.routing_key]
            for binding_key in binding_keys:
                self._channel.queue_bind(worker_cfg.queue, 
                                         worker_cfg.exchange, 
                                         binding_key, 
                                         callback= lambda unused_frame : self.on_bindok(unused_frame, worker_cfg)
                                        )
        else:
            self.on_bindok('', worker_cfg)

    def on_bindok(self, unused_frame, worker_cfg: WorkerDelegate):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame
        :param WorkerDelegate worker_cfg: WorkerDelegate config

        """
        if worker_cfg.queue and worker_cfg.exchange:
            LOGGER.info("Queue '%s' bound", worker_cfg.queue)
        if not worker_cfg.registered:
            # in case that binding a multiple routing key to the exchange
            worker_cfg.registered = True
            self.start_worker(worker_cfg)

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        # LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def on_message(self, ch: pika.channel.Channel, basic_deliver: pika.spec.Basic.Deliver, properties: pika.BasicProperties, body: bytes):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel ch: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param bytes body: The message body
        :param WorkerDelegate worker_cfg: WorkerDelegate config

        """
        # LOGGER.info('Received message # %s from %s: %s', basic_deliver.delivery_tag, str(properties.app_id), body)
        worker_cfg = self._workers_by_consumer_tag.get(basic_deliver.consumer_tag)
        if worker_cfg and worker_cfg.callback:
            # self._connection.ioloop.call_soon(worker_cfg.callback, ch, basic_deliver, properties, body)
            # worker_cfg.callback(ch, basic_deliver, properties, body)
            self._connection.ioloop.add_callback(functools.partial(worker_cfg.executor, self, ch, basic_deliver, properties, body))
            if worker_cfg.auto_ack:
                self.acknowledge_message(basic_deliver.delivery_tag)

            if self.tracker_queue_name and properties.correlation_id:
                self._connection.ioloop.add_callback(functools.partial(self._publish_tracker), body, properties)
        else:
            self._channel.basic_nack(basic_deliver.delivery_tag, requeue=True)

    def on_cancel_consuming_ok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        LOGGER.info('RabbitMQ acknowledged the cancellation of the consumer')
        # TODO
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        LOGGER.info('Closing the channel')
        self._channel.close()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            for worker_cfg in self._workers.values():
                if worker_cfg.consumer_tag:
                    self._channel.basic_cancel(worker_cfg.consumer_tag, self.on_cancel_consuming_ok)

    def start_worker(self, worker_cfg):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        :param WorkerDelegate worker_cfg: WorkerDelegate config

        """
        # self.add_on_cancel_callback()
        if worker_cfg.worker_type == WORKER_TYPE.CONSUMER:
            LOGGER.info("Issuing consumer for queue:'%s'", worker_cfg.queue)
            self._channel.basic_qos(prefetch_count=worker_cfg.prefetch_count)
            worker_cfg.consumer_tag = self._channel.basic_consume(worker_cfg.queue, 
                                                                  self.on_message,
                                                                  auto_ack = False)
            self._workers_by_consumer_tag[worker_cfg.consumer_tag] = worker_cfg
        
        elif not self._publish_working:
            self.start_publishing()

    def start_publishing(self):
        """This method will enable delivery confirmations and schedule the
        first message to be sent to RabbitMQ

        """
        LOGGER.info('Start publishing scheduler')
        # self.enable_delivery_confirmations()
        self.schedule_next_message()

    def enable_delivery_confirmations(self):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.

        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.

        """
        LOGGER.info('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing house keeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame

        """
        # confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        # LOGGER.info('Received %s for delivery tag: %i', confirmation_type,
        #             method_frame.method.delivery_tag)
        # if confirmation_type == 'ack':
        #     self._acked += 1
        # elif confirmation_type == 'nack':
        #     self._nacked += 1
        # self._deliveries.remove(method_frame.method.delivery_tag)
        # LOGGER.info(
        #     'Published %i messages, %i have yet to be confirmed, '
        #     '%i were acked and %i were nacked', self._message_number,
        #     len(self._deliveries), self._acked, self._nacked)

    def schedule_next_message(self):
        """If we are not closing our connection to RabbitMQ, schedule another
        message to be delivered in publishing_interval seconds.

        """
        # LOGGER.info('Scheduling next message for %0.1f seconds', self.publishing_interval)
        if self._connection and self._publishes:
            self._publish_working = True
            self._connection.ioloop.add_callback(functools.partial(self._do_publish_message))
        else:
            self._publish_working = False

    @tornado.gen.coroutine
    def _do_publish_message(self):
        """If the class is not stopping, publish a message to RabbitMQ,
        appending a list of deliveries with the message number that was sent.
        This list will be used to check for delivery confirmations in the
        on_delivery_confirmations method.

        Once the message has been sent, schedule another message to be sent.
        The main reason I put scheduling in was just so you can get a good idea
        of how the process is flowing by slowing down and speeding up the
        delivery intervals by changing the publishing_interval constant in the
        class.

        """
        if self._channel is None or not self._channel.is_open:
            self._publish_working = False
            return

        for element in self._publishes:
            pub_properties = element.properties
            if callable(element.callback):
                if not element.properties:
                    correlation_id = str(uuid.uuid4())
                    element.properties = pika.BasicProperties(correlation_id=correlation_id,
                                                              reply_to=self._rpc_queue_name,
                                                              message_id=correlation_id,
                                                              headers={'X-Forward-For': self._rpc_queue_name}
                    )
                if not element.properties.correlation_id:
                    element.properties.correlation_id = str(uuid.uuid4())
                    if element.properties.reply_to:
                        if not element.properties.headers:
                            element.properties.headers = {'X-Forward-For': element.properties.reply_to}
                        elif 'X-Forward-For' not in element.properties.headers:
                            element.properties.headers['X-Forward-For'] = element.properties.reply_to
                element.properties.timestamp = int(time.time())
                pub_properties = copy.deepcopy(element.properties)
                if False == self._rpc_started:
                    self._ensure_rpc_response_queue()
                    self._rpc_started = True
                self._rpc_queue[pub_properties.correlation_id] = element
                pub_properties.reply_to = self._rpc_queue_name

            self._channel.basic_publish(element.exchange, element.routing_key,
                                        element.message,
                                        pub_properties)
            if self.tracker_queue_name and element.properties and element.properties.correlation_id:
                self._connection.ioloop.add_callback(functools.partial(self._publish_tracker), element.message, element.properties)
        self._publishes = []

        # hdrs = {u'مفتاح': u' قيمة', u'键': u'值', u'キー': u'値'}
        # properties = pika.BasicProperties(
        #     app_id='example-publisher',
        #     content_type='application/json',
        #     headers=hdrs)

        # message = u'مفتاح قيمة 键 值 キー 値'
        # self._channel.basic_publish(self.exchange, self.routing_key,
        #                             json.dumps(message, ensure_ascii=False),
        #                             properties)
        # self._message_number += 1
        # self._deliveries.append(self._message_number)
        # LOGGER.info('Published message # %i', self._message_number)

        if self._publish_working:
            self.schedule_next_message()

    def _set_reply_needed_message(self, properties: pika.BasicProperties):
        if properties.correlation_id and properties.reply_to:
            self._processing_replyies[properties.correlation_id] = properties
    
    def _answer_reply_needed_message(self, properties: pika.BasicProperties):
        if properties.correlation_id:
            if properties.correlation_id in self._processing_replyies:
                del self._processing_replyies[properties.correlation_id]

    def _is_reply_needed_message_answered(self, correlation_id: str) -> bool:
        if correlation_id:
            return correlation_id in self._processing_replyies
        return False

    def _ensure_rpc_response_queue(self):
        self._channel.queue_declare(self._rpc_queue_name, 
                                    durable=False,
                                    auto_delete=True,
                                    callback=lambda method: self._channel.basic_consume(self._rpc_queue_name, self._rpc_response, auto_ack=True)
                                    )

    @tornado.gen.coroutine
    def _rpc_response(self, ch: pika.channel.Channel, basic_deliver: pika.spec.Basic.Deliver, properties: pika.BasicProperties, body: bytes):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel ch: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param bytes body: The message body

        """
        if properties.correlation_id not in self._rpc_queue:
            return
        element = self._rpc_queue[properties.correlation_id]
        if callable(element.callback):
            element.callback(ch, basic_deliver, properties, body)
        del self._rpc_queue[properties.correlation_id]
        LOGGER.info('got rpc response %s', str(body))

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        try:
            self._connection = self.connect()
            if not self._using_outside_ioloop:
                self._connection.ioloop.start()
        except KeyboardInterrupt:
            self.stop()
            if (self._connection is not None and
                    not self._connection.is_closed):
                # Finish closing
                if not self._using_outside_ioloop:
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
        LOGGER.info('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.stop()
        LOGGER.info('Stopped')

    def setup_workers(self):
        for worker_cfg in self._workers.values():
            if not worker_cfg.registered:
                self.setup_exchange(worker_cfg)
        
        if self._rpc_started:
            self._ensure_rpc_response_queue()

    def publish(self, exchange: str, routing_key: str, message: bytes, properties: Optional[pika.BasicProperties] = None, callback: Optional[callable] = None):
        """publishing a message

        :param str exchange: The exchange name of destination rabbitmq
        :param str routing_key: The routing key of destination rabbitmq
        :param str|bytes body: The message content
        :param pika.BasicProperties properties: The rabbitmq message properties

        """
        element = PublishesMessage(exchange,
                                   routing_key,
                                   message,
                                   properties,
                                   callback)
        self._publishes.append(element)

        if properties:
            # check if the publish message belongs to rpc reply
            if properties.correlation_id and routing_key == properties.reply_to:
                self._answer_reply_needed_message(properties)
        if not self._publish_working:
            self.start_publishing()

    def consume(self, exchange, exchange_type, binding_key, queue, durable, callback, auto_ack = True, exchange_durable = None, prefetch_count=20):
        """Consumes a message

        :param str exchange: The exchange name of destination rabbitmq
        :param str exchange_type: The exchange type of destination rabbitmq
        :param str binding_key: The routing key of destination rabbitmq
        :param str queue: The destination queue
        :param bool durable: If the queue is durable
        :param callable callback: callback(pika.frame.Method) for method
          Basic.ConsumeOk.
        :param bool auto_ack: Enable manually ack when set to False
        :param bool exchange_durable: if the exchange is durable
        :param int prefetch_count: each consume fetch count, default 20

        """
        key = '%s:%s:%s' % (exchange, binding_key, queue)
        if key in self._workers:
            LOGGER.error('Consumes a queue by exchange:%s binding_key:%s queue:%s while the consumer already registered.', exchange, binding_key, queue)
            return
        amqp_properties = {
            'exchange': exchange,
            'exchange_type': exchange_type,
            'exchange_durable': (durable if exchange_durable is None else exchange_durable),
            'routing_key': binding_key,
            'queue': queue,
            'durable': durable,
            'auto_ack': auto_ack,
        }
        worker_cfg = WorkerDelegate(WORKER_TYPE.CONSUMER, 
                                    amqp_properties,
                                    callback,
                                    prefetch_count=prefetch_count)
        self._workers[key] = worker_cfg
        if self._channel:
            self.setup_workers()

    def initialize_publisher(self, exchange, exchange_type, binding_key, queue, durable, exchange_durable = None):
        """Initialize a publishing queue and exchange

        :param str exchange: The exchange name of destination rabbitmq
        :param str exchange_type: The exchange type of destination rabbitmq
        :param str binding_key: The routing key of destination rabbitmq
        :param str queue: The destination queue
        :param bool durable: If the queue is durable
        :param bool exchange_durable: if the exchange is durable

        """
        key = '%s:%s:%s' % (exchange, binding_key, queue)
        if key in self._workers:
            LOGGER.error('Initialize a publisher by exchange:%s binding_key:%s queue:%s while the consumer already registered.', exchange, binding_key, queue)
            return
        amqp_properties = {
            'exchange': exchange,
            'exchange_type': exchange_type,
            'exchange_durable': (durable if exchange_durable is None else exchange_durable),
            'routing_key': binding_key,
            'queue': queue,
            'durable': durable,
            'auto_ack': False,
        }
        worker_cfg = WorkerDelegate(WORKER_TYPE.PUBLISHER, 
                                    amqp_properties,
                                    None)
        self._workers[key] = worker_cfg
        if self._channel:
            self.setup_workers()

    @tornado.gen.coroutine
    def _publish_tracker(self, message: bytes, properties: pika.BasicProperties):
        """If the class is not stopping, publish a message to RabbitMQ,
        appending a list of deliveries with the message number that was sent.
        This list will be used to check for delivery confirmations in the
        on_delivery_confirmations method.

        Once the message has been sent, schedule another message to be sent.
        The main reason I put scheduling in was just so you can get a good idea
        of how the process is flowing by slowing down and speeding up the
        delivery intervals by changing the publishing_interval constant in the
        class.

        """
        if not self.tracker_queue_name or self._channel is None or not self._channel.is_open:
            return

        self._channel.basic_publish('', self.tracker_queue_name,
                                    message if self.tracker_message_content else bytes('', 'utf-8'),
                                    properties)

@singleton
class RabbitMQFactory(object):

    def __init__(self):
        """Constructs a RabbitMQ operation factory

        """
        self._instances: Dict[str, WorkerDelegate] = {}
        self._default_virtual_host = None
        self._custom_ioloop = None
        self._tracker_queue_name: str = ''
        self._tracker_message_content: bool = False

    def initialize(self, conn_info: Dict[str, Any]):
        """Initializing a RabbitMQ operation factory

        :param dict conn_info: Connection configurations

        """
        virtual_host = conn_info.get('virtual_host')
        if virtual_host in self._instances:
            return self._instances[virtual_host]
        socket_timeout = conn_info['sock_timeout'] if 'sock_timeout' in conn_info else RABBIT_MQ_DEFAULTS.SOCKET_TIMEOUT
        heartbeat_interval = conn_info['heartbeat'] if 'heartbeat' in conn_info else RABBIT_MQ_DEFAULTS.HEARTBEAT_INTERVAL
        amqp_instance = RabbitMQWorker(host=conn_info.get('host'),
                                        port=conn_info.get('port'),
                                        username=conn_info.get('username'),
                                        password=conn_info.get('password'),
                                        virtual_host=virtual_host,
                                        socket_timeout=socket_timeout,
                                        hb_interval=heartbeat_interval)
        amqp_instance.set_using_outside_ioloop(True)

        amqp_instance.tracker_queue_name = self._tracker_queue_name
        amqp_instance.tracker_message_content = self._tracker_message_content
        self._instances[virtual_host] = amqp_instance
        if not self._default_virtual_host:
            self._default_virtual_host = virtual_host

        return amqp_instance

    def set_custom_ioloop(self, custom_ioloop):
        """Specifies a custom ioloop, this method should be called before run

        :param None | asyncio.AbstractEventLoop |
            nbio_interface.AbstractIOServices custom_ioloop:
                Defaults to asyncio.get_event_loop().

        """
        self._custom_ioloop = custom_ioloop

    def set_tracker_queue_name(self, queue_name: str):
        """Setup global tracker queue name, this would affect all workers
        """
        self._tracker_queue_name = queue_name
        for inst in self._instances.values():
            inst.tracker_queue_name = self._tracker_queue_name

    def enable_tracker_message_content(self, enabled: bool):
        """Setup global tracker queue name, this would affect all workers
        """
        self._tracker_message_content = True if enabled else False
        for inst in self._instances.values():
            inst.tracker_message_content = self._tracker_message_content

    def consume(self, virtual_host: str, exchange: str, exchange_type: str, binding_key: str, queue: str, durable: bool, callback: callable, auto_ack: bool = True, exchange_durable: bool = None, prefetch_count=20):
        """Consumes a message

        :param str virtual_host: The destination connection virtual host
        :param str exchange: The exchange name of destination rabbitmq
        :param str exchange_type: The exchange type of destination rabbitmq
        :param str binding_key: The routing key of destination rabbitmq
        :param str queue: The destination queue
        :param bool durable: If the queue is durable
        :param callable callback: callback(pika.frame.Method) for method
          Basic.ConsumeOk.
        :param bool auto_ack: Enable manually ack when set to False
        :param bool exchange_durable: if the exchange is durable

        """
        self._instances[virtual_host].consume(exchange, exchange_type, binding_key, queue, durable, callback, auto_ack, exchange_durable, prefetch_count=prefetch_count)

    def initialize_publisher(self, virtual_host: str, exchange: str, exchange_type: str, binding_key: str, queue: str, durable: bool, exchange_durable: bool = None):
        """Initialize a publishing queue and exchange

        :param str virtual_host: The destination connection virtual host
        :param str exchange: The exchange name of destination rabbitmq
        :param str exchange_type: The exchange type of destination rabbitmq
        :param str binding_key: The routing key of destination rabbitmq
        :param str queue: The destination queue
        :param bool durable: If the queue is durable
        :param bool exchange_durable: if the exchange is durable

        """
        self._instances[virtual_host].initialize_publisher(exchange, exchange_type, binding_key, queue, durable, exchange_durable)

    def publish(self, virtual_host: str, exchange: str, routing_key: str, message: bytes, properties: Optional[pika.BasicProperties] = None, callback: Optional[callable] = None):
        """publishing a message

        :param str virtual_host: The destination connection virtual host
        :param str exchange: The exchange name of destination rabbitmq
        :param str routing_key: The routing key of destination rabbitmq
        :param str|bytes body: The message content
        :param pika.BasicProperties properties: The rabbitmq message properties

        """
        self._instances[virtual_host].publish(exchange, routing_key, message, properties, callback)

    def query_mq(self, virtual_host: str, exchange: str, routing_key: str, message: bytes, properties: Optional[pika.BasicProperties] = None):
        """publishing a message and waiting response

        :param str virtual_host: The destination connection virtual host
        :param str exchange: The exchange name of destination rabbitmq
        :param str routing_key: The routing key of destination rabbitmq
        :param str|bytes body: The message content
        :param pika.BasicProperties properties: The rabbitmq message properties

        :return tornado.gen.Future of PublishesResponse

        """
        waiter = tornado.gen.Future()
        callback = lambda ch, delivery, properties, body: waiter.set_result(PublishesResponse(ch, delivery, properties, body))
        # todo: waiter timeout
        self._instances[virtual_host].publish(exchange, routing_key, message, properties, callback)
        return waiter

    def run(self):
        # asyncio.set_event_loop(asyncio.new_event_loop())
        for amqp_instance in self._instances.values():
            amqp_instance.run()

    def stop(self):
        for amqp_instance in self._instances.values():
            amqp_instance.stop()
