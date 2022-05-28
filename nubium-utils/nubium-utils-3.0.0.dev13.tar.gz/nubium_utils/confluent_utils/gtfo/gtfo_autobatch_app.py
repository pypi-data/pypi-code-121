
from confluent_kafka import TopicPartition
from nubium_utils.custom_exceptions import NoMessageError
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
import logging
from datetime import datetime
from .gtfo_app import GtfoApp, Transaction


LOGGER = logging.getLogger(__name__)


class AutoBatchTransaction(Transaction):
    def __init__(self, producer, consumer, metrics_manager=None, auto_consume=False, timeout=None, parent_app=None):
        self._commit_offsets = {}
        self.message_count = 0
        super().__init__(producer, consumer, metrics_manager=metrics_manager, auto_consume=auto_consume, timeout=timeout,
                         message=None, parent_app=parent_app)

    def _refresh_transaction_fields(self):
        super()._refresh_transaction_fields()
        self._commit_offsets = {}
        self.message_count = 0

    def consume(self):
        super().consume()
        self._commit_offsets[self.partition()] = {"topic": self.topic(), "partition": self.partition(), "offset": self.offset()}
        self.message_count += 1

    def commit(self, mark_committed=True):
        # TODO: Confirm there aren't commits from old partition assignments (not sure how that's handled...it may not rebalance
        #  while doing a transaction?)
        offsets_to_commit = [TopicPartition(msg['topic'], msg['partition'], msg['offset'] + 1) for msg in
                             self._commit_offsets.values()]
        if offsets_to_commit:
            LOGGER.debug(f'Offsets to commit: {offsets_to_commit}')
            self._init_transaction()
        if self._active_transaction:
            LOGGER.info(f'Committing {self.message_count} messages...')
            self.producer.send_offsets_to_transaction(offsets_to_commit, self.consumer.consumer_group_metadata())
            self.producer.commit_transaction(30)
            self.producer.poll(0)
            LOGGER.debug('All partition transactions committed!')
            self._committed = mark_committed
            self._commit_offsets = {}
            self.message_count = 0
            self._retry_offsets = {}
            if self._committed:
                self._active_transaction = False


class GtfoAutoBatchApp(GtfoApp):
    def __init__(self, app_function, consume_topics_list, produce_topic_schema_dict=None,
                 transaction_type=AutoBatchTransaction,
                 app_function_arglist=None, metrics_manager=None, schema_registry=None, cluster_name=None,
                 consumer=None, producer=None, time_elapse_max_seconds=None, consume_max_count=None):
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

    def _max_consume_time_continue(self):
        if self._time_elapse_max_seconds:
            seconds_elapsed = datetime.now().timestamp() - self._time_elapse_start
            return seconds_elapsed < self._time_elapse_max_seconds
        return True

    def _max_consume_count_countinue(self):
        if self._consume_max_count:
            return self.transaction.message_count < self._consume_max_count
        return True

    def _keep_consuming(self):
        return self._max_consume_count_countinue() and self._max_consume_time_continue()

    def commit(self):
        # TODO: remove once base class one is changed back to this
        if not self.transaction._committed:
            self.transaction.commit()

    def _app_run(self, *args, **kwargs):
        self.prepare_transaction(*args, **kwargs)
        if self._time_elapse_max_seconds:
            self._time_elapse_start = datetime.now().timestamp()
        LOGGER.debug(
            f'Processing up to {self._consume_max_count} messages for up to {self._time_elapse_max_seconds} seconds!')
        try:
            if not self.transaction._committed:
                while self._keep_consuming():
                    self.transaction.consume()
                    self.app_function(self.transaction, *self.app_function_arglist)
        except NoMessageError:
            self.producer.poll(0)
            LOGGER.debug('No messages!')
            pass
        if self.transaction._commit_offsets:
            self.commit()
