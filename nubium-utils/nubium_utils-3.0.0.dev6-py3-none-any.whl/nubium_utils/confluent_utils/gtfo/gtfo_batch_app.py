
from confluent_kafka import TopicPartition
from nubium_utils.custom_exceptions import NoMessageError
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
import logging
from datetime import datetime
from .gtfo_app import GtfoApp, Transaction


LOGGER = logging.getLogger(__name__)


class BatchTransaction(Transaction):
    def __init__(self, producer, consumer, metrics_manager=None, auto_consume=True, timeout=None, message_batch=None, parent_app=None):
        self._default_consume_max_count = int(env_vars()['NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_COUNT'])
        self._default_consume_max_time = int(env_vars()['NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_TIME_SECONDS'])
        self.message_batch_partition_offset_msg = {}

        if not message_batch:
            message_batch = []
        message = message_batch[-1] if message_batch else None

        self.message_batch = message_batch
        super().__init__(producer, consumer, metrics_manager=metrics_manager, auto_consume=False, timeout=timeout,
                         message=message, parent_app=parent_app)
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

        LOGGER.debug(
            f'While messages, consuming up to {consume_max_count} messages for up to {time_elapse_max_seconds} seconds!')
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
        offsets_to_commit = [TopicPartition(msg.topic(), msg.partition(), msg.offset() + 1) for msg in
                             self.message_batch_partition_offset_msg.values()]
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
    def __init__(self, app_function, consume_topics_list, produce_topic_schema_dict=None,
                 transaction_type=BatchTransaction,
                 app_function_arglist=None, metrics_manager=None, schema_registry=None, cluster_name=None,
                 consumer=None, producer=None):
        super().__init__(app_function, consume_topics_list, produce_topic_schema_dict=produce_topic_schema_dict,
                         transaction_type=transaction_type,
                         app_function_arglist=app_function_arglist, metrics_manager=metrics_manager,
                         schema_registry=schema_registry, cluster_name=cluster_name, consumer=consumer,
                         producer=producer)
