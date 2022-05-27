import json
import os

from confluent_kafka import TopicPartition, KafkaException, DeserializingConsumer
from nubium_utils.general_utils import parse_headers, log_and_raise_error
from nubium_utils.custom_exceptions import NoMessageError, SignalRaise, RetryTopicSend, FailureTopicSend, MaxRetriesReached
from nubium_utils.metrics import MetricsManager
from nubium_utils.yaml_parser import load_yaml_fp
from .consumer_utils import consume_message
from .producer_utils import produce_message, get_producers
from .message_utils import shutdown_cleanup
from .rocksdb_utils import RDB, RdbTableInUse
from .confluent_runtime_vars import env_vars
from .confluent_configs import init_transactional_consumer_configs, init_schema_registry_configs, get_kafka_configs, init_metrics_pushing
import logging
from time import sleep
from json import dumps, loads
from copy import deepcopy
from os import environ, remove
from datetime import datetime
# TODO: consider using orjson for changelog speed increases?
# from orjson import dumps, loads
# changelog_schema = {"type": "bytes"}
changelog_schema = {"type": "string"}

LOGGER = logging.getLogger(__name__)


class RunTableRecovery(Exception):
    def __init__(self):
        pass


class Transaction:
    def __init__(self, producer, consumer, metrics_manager=None, auto_consume=True, timeout=None, message=None):
        self.producer = producer
        self.consumer = consumer
        self.message = message
        self.metrics_manager = metrics_manager
        if not timeout:
            timeout = int(env_vars()['NU_CONSUMER_POLL_TIMEOUT'])
        self._timeout = timeout
        self.auto_consume(self.message, auto_consume)

        # mostly used for signaling to GtfoApp that there's currently a transaction and handling automatic committing
        self._committed = False
        self._active_transaction = False

    def auto_consume(self, has_input, should_consume):
        """ Consume message if initialized without one (and allowed to) """
        if not has_input and should_consume:
            self.consume()

    def messages(self):  # here for a consistent way to access message(s) currently being managed for when you subclass
        """ For a standardized way to access message(s) consumed pertaining to this transaction """
        return self.message

    def consume(self):
        self.message = consume_message(self.consumer, self.metrics_manager, self._timeout)

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
    
    def _init_transaction(self):
        """ Mark that a transaction is now underway. Triggered by trying to produce or commit a message """
        if not self._active_transaction and not self._committed:
            self.producer.begin_transaction()
            self._active_transaction = True

    def produce(self, producer_kwargs, headers_passthrough=None):
        if not headers_passthrough:
            headers_passthrough = self.headers()
        self.producer.poll(0)
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
            if self.message:
                self.producer.send_offsets_to_transaction(
                    [TopicPartition(self.topic(), self.partition(), self.offset() + 1)], self.consumer.consumer_group_metadata())
            self.producer.commit_transaction()
            self.producer.poll(0)
            self._committed = mark_committed
            if self._committed:
                self._active_transaction = False
                LOGGER.debug('Transaction Committed!')


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

    def _get_cluster_name(self, consume_topics_list):
        topic = consume_topics_list[0] if isinstance(consume_topics_list, list) else consume_topics_list
        return load_yaml_fp(env_vars()['NU_TOPIC_CONFIGS_YAML'])[topic]['cluster']

    def _get_transactional_producer(self, topic_schema_dict, schema_registry, cluster_name):
        LOGGER.debug('Setting up Kafka Transactional Producer')
        producer = get_producers(topic_schema_dict, cluster_name, schema_registry, transactional=True)
        producer.init_transactions()
        LOGGER.debug('Producer setup complete.')
        return producer

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
        LOGGER.debug('App - Attempting to consume')
        self.transaction = self.transaction_type(self.producer, self.consumer, *args, metrics_manager=self.metrics_manager, timeout=timeout, **kwargs)
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

    def kafka_cleanup(self):
        """ Public method in the rare cases where you need to do some cleanup on the consumer object manually. """
        shutdown_cleanup(consumer=self.consumer)

    def _app_shutdown(self):
        LOGGER.info('App is shutting down...')
        try:
            if self.transaction._active_transaction:
                self.producer.abort_transaction(10)
        except:
            pass
        finally:
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


class BatchTransaction(Transaction):
    def __init__(self, producer, consumer, metrics_manager=None, auto_consume=True, timeout=None, message_batch=None):
        self._default_consume_max_count = int(env_vars()['NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_COUNT'])
        self._default_consume_max_time = int(env_vars()['NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_TIME_SECONDS'])
        self.message_batch_partition_offset_msg = {}

        if not message_batch:
            message_batch = []
        message = message_batch[-1] if message_batch else None

        self.message_batch = message_batch
        super().__init__(producer, consumer, metrics_manager=metrics_manager, auto_consume=False, timeout=timeout, message=message)
        if self._timeout > self._default_consume_max_time:
            self._timeout = self._default_consume_max_time
        self.auto_consume(self.message_batch, auto_consume)

    def messages(self):
        return self.message_batch

    def consume(self, time_elapse_max_seconds=None, consume_max_count=None):
        """
        Allows you to (additionally) consume more messages on demand via the consume_max_count.
        Usually only necessary with more complex consumption patterns where bulk is swapped between.

        Note the "max count" is the max size you allow self.message_batch to be, which includes all previous consumes
        on this transaction.
        """
        if not time_elapse_max_seconds:
            time_elapse_max_seconds = self._default_consume_max_time
        if not consume_max_count:
            consume_max_count = self._default_consume_max_count

        if time_elapse_max_seconds:
            time_elapse_start = datetime.now().timestamp()

        def max_time_elapsed():
            if time_elapse_max_seconds:
                return datetime.now().timestamp() - time_elapse_start > time_elapse_max_seconds
            return False
            
        def keep_consuming():
            if not consume_max_count or max_time_elapsed():
                return True
            return len(self.message_batch) < consume_max_count

        LOGGER.debug(f'While messages, consuming up to {consume_max_count} messages for up to {time_elapse_max_seconds} seconds!')
        while keep_consuming():
            try:
                super().consume()
                self.message_batch.append(self.message)
                self.message_batch_partition_offset_msg[self.message.partition()] = self.message
            except NoMessageError:
                if not self.message_batch:
                    raise
                else:
                    break
        LOGGER.info(f'Finished batch consumption; total messages in batch: {len(self.message_batch)}')

    def produce(self, producer_kwargs, headers_passthrough):
        """Since we can consume more than 1 message at a time,
        you also need to specify the headers since it normally operates on the self.message attribute"""
        super().produce(producer_kwargs, headers_passthrough=headers_passthrough)

    def produce_retry(self, exception=None, message=None):
        if message:
            self.message = message
            super().produce_retry(exception=exception)
        else:
            for msg in self.message_batch:
                self.message = msg
                super().produce_retry(exception=exception)

    def produce_failure(self, exception=None, message=None):
        if message:
            self.message = message
            super().produce_failure(exception=exception)
        else:
            for msg in self.message_batch:
                self.message = msg
                super().produce_failure(exception=exception)

    def commit(self, mark_committed=True):
        offsets_to_commit = [TopicPartition(msg.topic(), msg.partition(), msg.offset() + 1) for msg in self.message_batch_partition_offset_msg.values()]
        self._init_transaction()
        if self._active_transaction:
            LOGGER.debug('Committing per partition...')
            if offsets_to_commit:
                self.producer.send_offsets_to_transaction(offsets_to_commit, self.consumer.consumer_group_metadata())
            self.producer.commit_transaction()
            self.producer.poll(0)
            self._committed = mark_committed
            if self._committed:
                self._active_transaction = False
                LOGGER.debug('All partition transactions committed!')


class GtfoBatchApp(GtfoApp):
    def __init__(self, app_function, consume_topics_list, produce_topic_schema_dict=None, transaction_type=BatchTransaction,
                 app_function_arglist=None, metrics_manager=None, schema_registry=None, cluster_name=None, consumer=None, producer=None):
        super().__init__(app_function, consume_topics_list, produce_topic_schema_dict=produce_topic_schema_dict, transaction_type=transaction_type,
                         app_function_arglist=app_function_arglist, metrics_manager=metrics_manager, schema_registry=schema_registry, cluster_name=cluster_name, consumer=consumer, producer=producer)


class TableTransaction(Transaction):
    def __init__(self, producer, consumer, app_changelog_topic, app_rdb_tables, metrics_manager=None, message=None, auto_consume=True, timeout=5):
        self.app_changelog_topic = app_changelog_topic
        self.app_rdb_tables = app_rdb_tables
        self._changelog_updated = False
        self._pending_table_write = None
        super().__init__(producer, consumer, metrics_manager=metrics_manager, message=message, auto_consume=auto_consume, timeout=timeout)

    def read_table_entry(self):
        return self._rdb_read()

    def update_table_entry(self, value):
        self._pending_table_write = deepcopy(value)
        if isinstance(self._pending_table_write, (list, dict)):
            # LOGGER.debug(f'attempting json dumps of {self._pending_table_write}')
            self._pending_table_write = dumps(self._pending_table_write)

    def delete_table_entry(self):
        self._pending_table_write = '-DELETED-'

    def _update_changelog(self):
        self.produce(dict(
            topic=self.app_changelog_topic,
            key=self.key(),
            value=self._pending_table_write
        ))
        self._changelog_updated = True
        self.producer.poll(0)

    def _recover_table_via_changelog(self):
        value = self.value()
        try:
            value = loads(value)
        except:
            pass
        if value == '-DELETED-':
            self.delete_table_entry()
        else:
            self.update_table_entry(value)
        super().commit()
        self._rdb_write()

    def _rdb_write(self):
        if self._pending_table_write == '-DELETED-':
            LOGGER.debug('Finalizing table entry delete...')
            self.app_rdb_tables[self.partition()].delete(self.key())
            self.app_rdb_tables[self.partition()].write('offset', str(self._rdb_offset() + 2))
        else:
            LOGGER.debug(f'Finalizing table entry write:\npartition{self.partition()},\nkey:{self.key()}')
            self.app_rdb_tables[self.partition()].write_batch(
                {self.key(): self._pending_table_write,
                 'offset': str(self._rdb_offset() + 2)})

    def _rdb_read(self):
        value = self.app_rdb_tables[self.partition()].read(self.key())
        try:
            value = loads(value)
        except:
            pass
        LOGGER.debug(f'Read table value: {value}')
        return value

    def _rdb_offset(self):
        value = self.app_rdb_tables[self.partition()].read('offset')
        if not value:
            value = self.offset() if self.offset() else 0
        return int(value)

    def commit(self, mark_committed=True):
        if not self._changelog_updated and self._pending_table_write:
            self._update_changelog()
        super().commit(mark_committed=False)
        if self._pending_table_write:
            self._rdb_write()
        if mark_committed:
            self._committed = True
            self._active_transaction = False
        self._pending_table_write = None
        LOGGER.debug('Transaction Committed!')


class GtfoTableApp(GtfoApp):
    def __init__(self, app_function, consume_topic, produce_topic_schema_dict=None, transaction_type=TableTransaction,
                 app_function_arglist=None, metrics_manager=None, schema_registry=None, cluster_name=None, consumer=None, producer=None):
        self.changelog_topic = f"{environ['NU_APP_NAME']}__changelog"
        self.rdb_tables = {}
        self._pending_primary_partitions = {}
        self._pending_table_recoveries = {}

        if not produce_topic_schema_dict:
            produce_topic_schema_dict = {}
        if self.changelog_topic not in produce_topic_schema_dict:
            produce_topic_schema_dict.update({self.changelog_topic: changelog_schema})
        if not cluster_name:
            cluster_name = self._get_cluster_name(consume_topic)
        if not schema_registry:
            schema_registry = init_schema_registry_configs(as_registry_object=True)
        if not consumer:
            consumer = self._set_table_consumer(consume_topic, schema_registry, cluster_name=cluster_name)

        self.consume_topic = consume_topic

        super().__init__(
            app_function, self.consume_topic, produce_topic_schema_dict, transaction_type=transaction_type,
            app_function_arglist=app_function_arglist, metrics_manager=metrics_manager, schema_registry=schema_registry, cluster_name=cluster_name, consumer=consumer, producer=producer)

    def _rdb_close(self, partitions=None):
        full_shutdown = False
        if not partitions:
            partitions = list(self.rdb_tables.keys())
            full_shutdown = True
        LOGGER.debug(f'RocksDB - closing connections for partitions {partitions}')
        for p in partitions:
            try:
                self.rdb_tables[p].close()
                del self.rdb_tables[p]
                LOGGER.debug(f'p{p} RDB table connection closed.')
            except KeyError:
                if not full_shutdown:
                    LOGGER.debug(
                        f'RDB Table p{p} did not seem to be mounted and thus could not unmount,'
                        f' likely caused by multiple rebalances in quick succession.'
                        f' This is unliklely to cause issues as the client is in the middle of adjusting itself, '
                        f' but should be noted.')
        LOGGER.info(f'RocksDB - closed connections for partitions {partitions}')

    def _confirm_proper_assignment(self):
        assignments = self.consumer.assignment()
        if self.changelog_topic in [p_obj.topic for p_obj in assignments]:
            raise Exception('changelog topic was included in normal consumption assignment! ABANDON SHIP!!!')
        topic = set([p_obj.partition for p_obj in assignments])
        tables = set(self.rdb_tables)
        if topic != tables:
            LOGGER.warning(f"Partition/Table assignment mismatch!! topic: {topic}; tables: {tables}")

    def _resume_consumption(self, from_recovery=False):
        if from_recovery:
            changelog_unassign = [p_obj for p_obj in self.consumer.assignment() if p_obj.topic == self.changelog_topic]
            LOGGER.debug(f'unassigning changelog partitions: {changelog_unassign}')
            self.consumer.incremental_unassign(changelog_unassign)
            LOGGER.debug(f'Resuming consumption for partitions:\n{list(self._pending_primary_partitions.values())}')
            self.consumer.resume(list(self._pending_primary_partitions.values()))
        self._confirm_proper_assignment()
        self._pending_table_recoveries = {}  # for tracking all recovery partitions during rebalances (based on primary)
        self._pending_primary_partitions = {}  # for tracking all assigned partitions during rebalances
        LOGGER.info('Continuing normal consumption loop...')

    def _rdb_init(self, partition):
        self.rdb_tables[partition] = RDB(f'p{partition}')
        LOGGER.debug(f'RDB table for p{partition} initialized')

    def _get_changelog_watermarks(self, recovery_partitions):
        """
        Note: this is a separate function since it requires the consumer to communicate with the broker
        """
        LOGGER.debug(f'Recovery_items: {recovery_partitions.items()}')
        return {p: self.consumer.get_watermark_offsets(p_obj) for p, p_obj in recovery_partitions.items()}

    def _refresh_pending_table_recoveries(self):
        """
        confirms new recoveries and removes old ones if not applicable anymore
        """
        recovery_partitions = {p: TopicPartition(topic=self.changelog_topic, partition=p) for p, p_obj in self._pending_primary_partitions.items()}
        tables_to_recover = {}
        for partition, watermarks in self._get_changelog_watermarks(recovery_partitions).items():
            LOGGER.debug(f'(lowwater, highwater) for changelog p{partition}: {watermarks}')
            if watermarks[0] != watermarks[1]:
                table_offset = self.rdb_tables[partition].read('offset')
                if table_offset:
                    table_offset = int(table_offset)
                else:
                    table_offset = 0
                if table_offset < watermarks[1]:
                    tables_to_recover[partition] = {'table_offset': table_offset, 'watermarks': watermarks, 'partition_obj': recovery_partitions[partition]}
        self._pending_table_recoveries = tables_to_recover

    def _init_rdb_tables(self, partition_objs, max_retry=10):
        partitions_to_assign = [p.partition for p in partition_objs]
        partition_attempts = {p: 0 for p in partitions_to_assign}
        while partitions_to_assign:
            partition = partitions_to_assign.pop(0)
            try:
                if partition not in self.rdb_tables:
                    if partition_attempts[partition]:
                        sleep(partition_attempts[partition]*.25)
                    self._rdb_init(partition)
            except RdbTableInUse as e:  # waiting for other app instance to relinquish claim on rdb table
                partition_attempts[partition] += 1
                LOGGER.debug(e)
                if partition_attempts[partition] == max_retry:
                    raise Exception(f'Max RDB table assignment attempts reached for {partition}. Terminating app')
                else:
                    partitions_to_assign.append(partition)

    def _new_table_recoveries(self, new_partitions):
        """ Add new recovery partitions based on additional rebalances """
        self._refresh_pending_table_recoveries()
        return {p: table_meta for p, table_meta in self._pending_table_recoveries.items() if p in new_partitions}

    def _recover_or_resume(self):
        # TODO: check to see if handling it via exception is actually necessary anymore?
        """
        Due to confluent-kafka consumers asynchronous operations, the best way to force a desired
        control flow within the general app consumer loop is to raise an exception and
        interrupt whatever the app is currently doing and start recovering.
        """
        if self._pending_table_recoveries:
            LOGGER.debug(f'Table recovery required: {self._pending_table_recoveries}')
            raise RunTableRecovery
        else:
            LOGGER.debug('Preparing to resume consumption pattern...')
            self._resume_consumption()

    def _rocksdb_assign(self, consumer, add_partition_objs):
        """
        Called every time a rebalance happens and handles table assignment and recovery flow.
        NOTE: rebalances pass relevant partitions per rebalance call which can happen multiple times, especially when
        multiple apps join at once; we have objects to track all updated partitions received during the entire rebalance.
        NOTE: confluent-kafka expects this method to have exactly these two arguments ONLY
        NOTE: _rocksdb_assign will ALWAYS be called (even when no new assignments are required) after _rocksdb_unassign.
        """
        LOGGER.info('Rebalance Triggered - Assigment')
        LOGGER.debug(f'Consumer - Assigning additional partitions: {[p_obj.partition for p_obj in add_partition_objs]}')
        if add_partition_objs:
            new_partitions = {p_obj.partition: p_obj for p_obj in add_partition_objs}
            self._pending_primary_partitions.update(new_partitions)
            self._init_rdb_tables(list(self._pending_primary_partitions.values()))
            add_table_recovery = self._new_table_recoveries(new_partitions)
            self.consumer.incremental_assign(add_partition_objs)
            if add_table_recovery:
                LOGGER.debug('New partition assignment will require table recovery...')
                self.consumer.incremental_assign([v['partition_obj'] for k, v in self._pending_table_recoveries.items() if k in new_partitions])  # could do all of them, but less exception handling/cleaner this way
        else:
            has_assignments = self.consumer.assignment()
            if has_assignments:
                LOGGER.debug('No new/additional partitions assigned.')
                LOGGER.info(f'Resuming current assignment of: {[p_obj.partition for p_obj in has_assignments]}')
            else:
                LOGGER.info('Awaiting partition assignments from broker...')
        LOGGER.info('Consumer - Assignment request complete.')
        self._recover_or_resume()

    def _rocksdb_unassign(self, consumer, drop_partition_objs):
        """
        NOTE: confluent-kafka expects this method to have exactly these two arguments ONLY
        NOTE: _rocksdb_assign will always be called (even when no new assignments are required) after _rocksdb_unassign.
        """
        partitions = [p_obj.partition for p_obj in drop_partition_objs]
        LOGGER.debug(f'Consumer - Unassigning topic {self.consume_topic} partitions: {partitions}')
        self.consumer.incremental_unassign(drop_partition_objs)
        if self._pending_table_recoveries:
            LOGGER.debug(f'unassigning changelog partitions: {drop_partition_objs}')
            self.consumer.incremental_unassign([p_obj for p_obj in self.consumer.assignment() if p_obj.topic == self.changelog_topic and p_obj.partition in drop_partition_objs])
        self._pending_primary_partitions = {k: v for k, v in self._pending_primary_partitions.items() if k not in partitions}
        self._pending_table_recoveries = {k: v for k, v in self._pending_table_recoveries.items() if k not in partitions}
        LOGGER.debug(f'pending_primary_partitions after unassignment: {self._pending_primary_partitions}')
        LOGGER.debug(f'table_recovery_status after unassignment: {self._pending_table_recoveries}')
        self._rdb_close(partitions)

    def _set_table_consumer(self, topic, schema_registry, default_schema=None, cluster_name=None):
        if isinstance(topic, str):
            topic = [topic]
        consumer = self._get_transactional_consumer(topic, schema_registry, cluster_name, default_schema, False)
        consumer.subscribe(topic, on_assign=self._rocksdb_assign, on_revoke=self._rocksdb_unassign, on_lost=self._rocksdb_unassign)
        LOGGER.debug('Table consumer initialized')
        return consumer

    def _table_recovery_refresh_starting_offsets(self):
        """ Refresh the offsets of recovery partitions to account for updated recovery states during rebalancing """
        for p, offsets in self._pending_table_recoveries.items():
            new_offset = self._pending_table_recoveries[p]['table_offset']
            low_mark = self._pending_table_recoveries[p]['watermarks'][0]
            if low_mark > new_offset:  # handles offsets that have been removed/compacted. Should never happen, but ya know
                LOGGER.info(
                    f'p{p} table has an offset ({new_offset}) less than the changelog lowwater ({low_mark}), likely due to retention settings. Setting {low_mark} as offset start point.')
                new_offset = low_mark
            high_mark = self._pending_table_recoveries[p]['watermarks'][1]
            LOGGER.debug(f'p{p} table has an offset delta of {high_mark - new_offset}')
            self._pending_table_recoveries[p]['partition_obj'].offset = new_offset

    def _table_recovery_loop(self, checks=3):
        LOGGER.info('BEGINNING TABLE RECOVERY PROCEDURE')
        while checks and self._pending_table_recoveries:
            try:
                self.consume()
                LOGGER.debug(f'Recovery write is {self.transaction.value()}')
                self.transaction._recover_table_via_changelog()
                p = self.transaction.partition()
                LOGGER.debug(
                    f"transaction_offset - {self.transaction.offset() + 2}, watermark - {self._pending_table_recoveries[p]['watermarks'][1]}")
                if self._pending_table_recoveries[p]['watermarks'][1] - (self.transaction.offset() + 2) <= 0:
                    LOGGER.info(f'table partition {p} fully recovered!')
                    del self._pending_table_recoveries[p]
            except NoMessageError:
                checks -= 1
                LOGGER.debug(f'No changelog messages, checks remaining: {checks}')
        LOGGER.info("TABLE RECOVERY COMPLETE!")

    def _throwaway_poll(self):
        """ Have to poll (changelog topic) after first assignment to it to allow seeking """
        LOGGER.debug("Performing throwaway poll to allow assignments to properly initialize...")
        try:
            self.consume(timeout=8)
        except NoMessageError:
            pass

    def _table_recovery(self, resume_consumption_after=True):
        # TODO: check if below is necc (maybe if you don't do an exception interrupt)?
        # while self._pending_table_recoveries: # In case of rebalance interruptions
        try:
            self._table_recovery_refresh_starting_offsets()
            LOGGER.debug(f'table_recovery_status before recovery attempt: {self._pending_table_recoveries}')
            for table_meta in self._pending_table_recoveries.values():
                self.consumer.seek(table_meta['partition_obj'])
            self._table_recovery_loop()
            if resume_consumption_after:
                self._resume_consumption(from_recovery=True)
        except KafkaException as e:
            if 'Failed to seek to offset' in e.args[0].str():
                LOGGER.debug('Running a consumer poll to allow seeking to work on the changelog partitions...')
                self._throwaway_poll()
                self._table_recovery(resume_consumption_after=resume_consumption_after)
        except Exception as e:
            LOGGER.debug(f'{[arg for arg in e.args]}')
            LOGGER.debug('Table recovery interrupted due to rebalance...retrying')

    def consume(self, *args, **kwargs):
        super().consume(*args, app_changelog_topic=self.changelog_topic, app_rdb_tables=self.rdb_tables, **kwargs)

    def _app_run_loop(self, *args, **kwargs):
        try:
            self.consume(*args, **kwargs)
            self.app_function(self.transaction, *self.app_function_arglist)
            if not self.transaction._committed:
                self.transaction.commit()
        except NoMessageError:
            self.producer.poll(0)
            LOGGER.debug('No messages!')
        except RunTableRecovery:
            self._table_recovery()

    def kafka_cleanup(self):
        super().kafka_cleanup()
        self._rdb_close()
