
from confluent_kafka import TopicPartition
from nubium_utils.custom_exceptions import NoMessageError
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
import logging
from datetime import datetime
from .gtfo_app import GtfoApp, Transaction, GracefulTransactionFailure, FatalTransactionFailure, KafkaException, handle_kafka_exception


LOGGER = logging.getLogger(__name__)


class AutoBatchTransaction(Transaction):
    def __init__(self, producer, consumer, metrics_manager=None, auto_consume=False, timeout=None, parent_app=None):
        self._message_offsets = {}
        self.message_count = 0
        super().__init__(producer, consumer, metrics_manager=metrics_manager, auto_consume=auto_consume, timeout=timeout,
                         message=None, parent_app=parent_app)

    def consume(self):
        super().consume()
        self._message_offsets[self.partition()] = {"topic": self.topic(), "partition": self.partition(), "offset": self.offset()}
        self.message_count += 1

    def _init_transaction(self):
        try:
            if not self._active_transaction and not self._committed:
                self.producer.begin_transaction()
                self._active_transaction = True
                self.producer.poll(0)
        except KafkaException as kafka_error:
            handle_kafka_exception(kafka_error)

    def commit(self, mark_committed=True):
        print(self._message_offsets)
        offsets_to_commit = [TopicPartition(msg['topic'], msg['partition'], msg['offset'] + 1) for msg in
                             self._message_offsets.values()]
        self._init_transaction()
        if self._active_transaction:
            LOGGER.debug(f'Committing {self.message_count} messages...')
            self.producer.send_offsets_to_transaction(offsets_to_commit, self.consumer.consumer_group_metadata())
            self.producer.commit_transaction()
            self.producer.poll(0)
            self._committed = mark_committed
            self._message_offsets = {}
            self.message_count = 0
            if self._committed:
                self._active_transaction = False
                LOGGER.debug('All partition transactions committed!')


class GtfoAutoBatchApp(GtfoApp):
    def __init__(self, app_function, consume_topics_list, produce_topic_schema_dict=None,
                 transaction_type=AutoBatchTransaction,
                 app_function_arglist=None, metrics_manager=None, schema_registry=None, cluster_name=None,
                 consumer=None, producer=None, time_elapse_max_seconds=None, consume_max_count=None):
        self.message_batch_partition_offset_msg = {}
        self._time_elapse_start = None

        if not time_elapse_max_seconds:
            time_elapse_max_seconds = int(env_vars()['NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_TIME_SECONDS'])
        if not consume_max_count:
            consume_max_count = int(env_vars()['NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_COUNT'])

        self._time_elapse_max_seconds = time_elapse_max_seconds
        self._consume_max_count = consume_max_count

        super().__init__(app_function, consume_topics_list, produce_topic_schema_dict=produce_topic_schema_dict,
                         transaction_type=transaction_type,
                         app_function_arglist=app_function_arglist, metrics_manager=metrics_manager,
                         schema_registry=schema_registry, cluster_name=cluster_name, consumer=consumer,
                         producer=producer)

    def prepare_transaction(self, *args, **kwargs):
        return super().consume(*args, **kwargs)

    def _max_consume_time_elapsed(self):
        if self._time_elapse_max_seconds:
            return datetime.now().timestamp() - self._time_elapse_start > self._time_elapse_max_seconds
        return False

    def _keep_consuming(self):
        if not self._consume_max_count or self._max_consume_time_elapsed():
            return True
        return self.transaction.message_count < self._consume_max_count

    def _app_run_loop(self, *args, **kwargs):
        try:
            self.prepare_transaction(*args, **kwargs)
            if self._time_elapse_max_seconds:
                self._time_elapse_start = datetime.now().timestamp()
            LOGGER.debug(
                f'Processing up to {self._consume_max_count} messages for up to {self._time_elapse_max_seconds} seconds!')
            try:
                while self._keep_consuming():
                    self.transaction.consume()
                    self.app_function(self.transaction, *self.app_function_arglist)
            except NoMessageError:
                self.producer.poll(0)
                LOGGER.debug('No messages!')
                pass
            if self.transaction._active_transaction and not self.transaction._committed:
                self.transaction.commit()
        except GracefulTransactionFailure:
            self.transaction.abort_active_transaction()
        except FatalTransactionFailure:
            self.transaction.abort_active_transaction()
            raise
