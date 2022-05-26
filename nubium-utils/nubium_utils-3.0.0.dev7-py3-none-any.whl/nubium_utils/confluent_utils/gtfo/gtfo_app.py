import json
from confluent_kafka import TopicPartition, DeserializingConsumer, KafkaException
from nubium_utils.general_utils import parse_headers, log_and_raise_error
from nubium_utils.custom_exceptions import NoMessageError, SignalRaise, RetryTopicSend, FailureTopicSend, MaxRetriesReached
from nubium_utils.metrics import MetricsManager
from nubium_utils.yaml_parser import load_yaml_fp
from nubium_utils.confluent_utils.consumer_utils import consume_message
from nubium_utils.confluent_utils.producer_utils import produce_message, get_producers
from nubium_utils.confluent_utils.message_utils import shutdown_cleanup
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from nubium_utils.confluent_utils.confluent_configs import init_transactional_consumer_configs, init_schema_registry_configs, get_kafka_configs, init_metrics_pushing
import logging
from os import remove

LOGGER = logging.getLogger(__name__)


class GracefulTransactionFailure(Exception):
    def __init__(self):
        pass


class FatalTransactionFailure(Exception):
    def __init__(self):
        pass


def handle_kafka_exception(kafka_error):
    retriable = kafka_error.args[0].retriable()
    abort = kafka_error.args[0].txn_requires_abort()
    LOGGER.debug(f'KafkaException: is retriable? - {retriable}, should abort? - {abort}')
    if retriable or abort:
        raise GracefulTransactionFailure
    else:
        raise FatalTransactionFailure


class Transaction:
    def __init__(self, producer, consumer, metrics_manager=None, auto_consume=True, auto_consume_init=False, timeout=None, message=None, parent_app=None):
        self.producer = producer
        self.consumer = consumer
        self.message = message
        self.metrics_manager = metrics_manager
        self.auto_consume_init = auto_consume_init
        self._committed = False  # mostly used for signaling to GtfoApp that there's currently a transaction and handling automatic committing
        self._active_transaction = False
        if not timeout:
            timeout = int(env_vars()['NU_CONSUMER_POLL_TIMEOUT'])
        self._timeout = timeout
        self.auto_consume(self.message, auto_consume)

        # this optional attribute should never be referenced/used by class methods here to keep transactions independent of the app
        # only intended for runtime access of the app instance by the transaction
        self.app = parent_app

    def auto_consume(self, has_input, should_consume):
        """ Consume message if initialized without one (and allowed to) """
        if not has_input and should_consume:
            self.consume()

    def messages(self):  # here for a consistent way to access message(s) currently being managed for when you subclass
        """ For a standardized way to access message(s) consumed pertaining to this transaction """
        return self.message

    def consume(self):
        self.message = consume_message(self.consumer, self.metrics_manager, self._timeout)
        if self.auto_consume_init:
            self._init_transaction()

    def key(self):
        return self.message.key()

    def value(self):
        return self.message.value()

    def headers(self):
        return parse_headers(self.message.headers())

    def topic(self):
        return self.message.topic()

    def partition(self):
        return self.message.partition()

    def offset(self):
        return self.message.offset()

    def abort_active_transaction(self, partitions=None, topics=None):
        LOGGER.debug('Aborting any open transactions, if needed.')
        abort = False
        if self._active_transaction:
            if isinstance(partitions, str):
                partitions = [partitions]
            if isinstance(topics, str):
                topics = [topics]
            abort = True
            if partitions:
                if self.partition() in partitions:
                    LOGGER.debug(f'Requested message partition {self.partition()}: abortion match')
                    abort = True
                else:
                    abort = False
            if topics:
                if self.topic() in topics:
                    LOGGER.debug(f'Requested message topic {self.topic()}: abortion match')
                    abort = True
                else:
                    abort = False
        if abort:
            try:
                LOGGER.info('Aborting transaction.')
                self._active_transaction = False
                self._committed = False
                self.producer.abort_transaction(10)
                self.producer.poll(0)
                LOGGER.info('Abortion complete!')
            except KafkaException as kafka_error:
                LOGGER.debug(f"Failed to abort transaction: {kafka_error}")
                pass

    def _init_transaction(self):
        """ Mark that a transaction is now underway. Triggered by trying to produce or commit a message """
        try:
            if not self._active_transaction and not self._committed:
                self.producer.begin_transaction()
                self._active_transaction = True
                if self.message:
                    self.producer.send_offsets_to_transaction(
                        [TopicPartition(self.topic(), self.partition(), self.offset() + 1)],
                        self.consumer.consumer_group_metadata(), 8)
                self.producer.poll(0)
        except KafkaException as kafka_error:
            handle_kafka_exception(kafka_error)

    def produce(self, producer_kwargs, headers_passthrough=None):
        if not headers_passthrough:
            headers_passthrough = self.headers()
        self._init_transaction()
        produce_message(self.producer, producer_kwargs, self.metrics_manager, headers_passthrough)
        self.producer.poll(0)

    def produce_retry(self, exception=None):
        retry_topic = None
        headers = self.headers()
        guid = headers['guid']
        kafka_retry_count = int(headers.get('kafka_retry_count', '0'))

        if kafka_retry_count < int(env_vars()['NU_RETRY_COUNT_MAX']):
            headers['kafka_retry_count'] = str(kafka_retry_count + 1)
            retry_topic = env_vars()['NU_CONSUME_TOPICS']
        else:
            headers['kafka_retry_count'] = '0'
            retry_topic = env_vars().get('NU_PRODUCE_RETRY_TOPICS', '')

        if retry_topic:
            if not exception:
                exception = RetryTopicSend()
            LOGGER.warning('; '.join([str(exception), f'retrying GUID {guid}']))
            self.produce(dict(
                topic=retry_topic,
                value=self.value(),
                key=self.key(),
                headers=headers))
        else:
            if not exception:
                exception = FailureTopicSend()
            LOGGER.error('; '.join([str(exception), f'GUID {guid}']))
            self.produce_failure(exception=MaxRetriesReached())

    def produce_failure(self, exception=None):
        headers = self.headers()
        guid = headers['guid']
        headers['kafka_retry_count'] = '0'
        failure_topic = env_vars()['NU_PRODUCE_FAILURE_TOPICS']

        if not exception:
            exception = FailureTopicSend()
        LOGGER.error('; '.join([type(exception).__name__, str(exception), f'failing GUID {guid}']))
        headers["exception"] = json.dumps({"name": type(exception).__name__, "description": str(exception)})

        LOGGER.debug(f'Adding a message to the produce queue for deadletter/failure topic {env_vars()["NU_PRODUCE_FAILURE_TOPICS"]}')
        self.produce(dict(
            topic=failure_topic,
            value=self.value(),
            key=self.key(),
            headers=headers))
        LOGGER.info(f'Message added to the deadletter/failure topic produce queue; GUID {guid}')

    def commit(self, mark_committed=True):
        """ Allows manual commits (safety measures in place so that you cant commit the same message twice)."""
        self._init_transaction()
        if self._active_transaction:
            try:
                self.producer.commit_transaction(8)
                self.producer.poll(0)
                self._committed = mark_committed
                if self._committed:
                    self._active_transaction = False
                    LOGGER.debug('Transaction Committed!')
            except KafkaException as kafka_error:
                handle_kafka_exception(kafka_error)


class GtfoApp:
    """ The main class to use for most GTFO apps. See README for initialization/usage details. """
    def __init__(self, app_function, consume_topics_list, produce_topic_schema_dict=None, transaction_type=Transaction,
                 app_function_arglist=None, metrics_manager=None, schema_registry=None, cluster_name=None, consumer=None, producer=None):
        self.transaction = None
        if not app_function_arglist:
            app_function_arglist = []
        if not metrics_manager:
            metrics_manager = MetricsManager()
        init_metrics_pushing(metrics_manager)
        if isinstance(consume_topics_list, str):
            consume_topics_list = consume_topics_list.split(',')
        if not produce_topic_schema_dict:  # for when the app is consume-only
            produce_topic_schema_dict = {topic: None for topic in consume_topics_list}
        if not schema_registry:
            schema_registry = init_schema_registry_configs(as_registry_object=True)
        if not cluster_name:
            topic_list = consume_topics_list if consume_topics_list else list(produce_topic_schema_dict.keys())
            cluster_name = self._get_cluster_name(topic_list)
        if not consumer:
            consumer = self._get_transactional_consumer(consume_topics_list, schema_registry, cluster_name)
        if not producer:
            producer = self._get_transactional_producer(produce_topic_schema_dict, schema_registry, cluster_name)

        self.transaction_type = transaction_type
        self.app_function = app_function
        self.app_function_arglist = app_function_arglist
        self.metrics_manager = metrics_manager
        self.produce_topic_schema_dict = produce_topic_schema_dict
        self.schema_registry = schema_registry
        self.cluster_name = cluster_name
        self.consumer = consumer
        self.producer = producer
        self.consume(auto_consume=False)  # gives you a transaction object to use at init, if you need it

    def _get_cluster_name(self, consume_topics_list):
        topic = consume_topics_list[0] if isinstance(consume_topics_list, list) else consume_topics_list
        return load_yaml_fp(env_vars()['NU_TOPIC_CONFIGS_YAML'])[topic]['cluster']

    def _get_transactional_producer(self, topic_schema_dict, schema_registry, cluster_name):
        LOGGER.debug('Setting up Kafka Transactional Producer')
        producer = get_producers(topic_schema_dict, cluster_name, schema_registry, transactional=True)
        producer.init_transactions()
        LOGGER.debug('Producer setup complete.')
        return producer

    def set_gtfo_producer(self):
        self.producer = self._get_transactional_producer(self.produce_topic_schema_dict, self.schema_registry, self.cluster_name)

    def _get_transactional_consumer(self, topics, schema_registry, cluster_name, default_schema=None, auto_subscribe=True):
        LOGGER.debug('Setting up Kafka Transactional Consumer')
        consumer = DeserializingConsumer(
            init_transactional_consumer_configs(topics, schema_registry, get_kafka_configs(cluster_name)[0], cluster_name, default_schema))
        if auto_subscribe:
            consumer.subscribe(topics)  # in case multiple topics are read from
            LOGGER.info(f'Transactional consumer subscribed to topics:\n{topics}')
        return consumer

    def consume(self, *args, timeout=10, **kwargs):
        """
        Accepts *args and **kwargs to make it easy to alter functionality of this function in subclasses.
        Public method so that you can manually consume messages if you desire; helpful for debugging.
        """
        self.transaction = self.transaction_type(self.producer, self.consumer, *args, metrics_manager=self.metrics_manager, timeout=timeout, parent_app=self, **kwargs)
        return self.transaction

    def _app_run_loop(self, *args, **kwargs):
        try:
            self.consume(*args, **kwargs)
            self.app_function(self.transaction, *self.app_function_arglist)
            if not self.transaction._committed:
                self.transaction.commit()
        except NoMessageError:
            self.producer.poll(0)
            LOGGER.debug('No messages!')
        except GracefulTransactionFailure:
            self.transaction.abort_active_transaction()
        except FatalTransactionFailure:
            self.transaction.abort_active_transaction()
            raise

    def kafka_cleanup(self):
        """ Public method in the rare cases where you need to do some cleanup on the consumer object manually. """
        shutdown_cleanup(consumer=self.consumer)

    def _app_shutdown(self):
        LOGGER.info('App is shutting down...')
        self.transaction.abort_active_transaction()
        self.kafka_cleanup()

    def run(self, *args, health_path='/tmp', as_loop=True, **kwargs):
        """
        # as_loop is really only for rare apps that don't follow the typical consume-looping behavior
        (ex: async apps) and don't seem to raise out of the True loop as expected.
        """
        with open(f'{health_path}/health', 'w') as health_file:
            health_file.write('Healthy')
        try:
            if as_loop:
                while True:
                    self._app_run_loop(*args, **kwargs)
            else:
                self._app_run_loop(*args, **kwargs)
        except SignalRaise:
            LOGGER.info('Shutdown requested!')
        except Exception as e:
            LOGGER.error(e)
            if self.metrics_manager:
                log_and_raise_error(self.metrics_manager, e)
        finally:
            self._app_shutdown()
            remove(f'{health_path}/health')
