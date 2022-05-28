from .gtfo_table_app import GtfoTableApp, TableTransaction, GracefulTransactionFailure, FatalTransactionFailure
from .gtfo_app import NoMessageError
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from confluent_kafka import TopicPartition
import logging
from copy import deepcopy
from json import loads
from datetime import datetime


LOGGER = logging.getLogger(__name__)


class AutoBatchTableTransaction(TableTransaction):
    def __init__(self, producer, consumer, app_changelog_topic, app_tables, metrics_manager=None, message=None, auto_consume=True, timeout=5, parent_app=None):
        self._pending_table_offset_increase = 0
        self._commit_offsets = {}
        self.message_count = 0
        super().__init__(producer, consumer, app_changelog_topic=app_changelog_topic, app_tables=app_tables, metrics_manager=metrics_manager, message=message, auto_consume=auto_consume, timeout=timeout, parent_app=parent_app)
        self._pending_table_writes = {p: {} for p in self.app_tables}

    def _refresh_transaction_fields(self):
        super()._refresh_transaction_fields()
        self._pending_table_writes = {p: {} for p in self.app_tables}
        self._pending_table_offset_increase = 0
        self._commit_offsets = {}
        self.message_count = 0

    def read_table_entry(self):
        pending_update = self._pending_table_writes.get(self.partition(), {}).get(self.key())
        if pending_update:
            return deepcopy(loads(pending_update))
        return super().read_table_entry()

    def update_table_entry(self, value):
        super().update_table_entry(value)
        self._update_changelog()
        self._update_pending_table_writes()

    def delete_table_entry(self):
        super().delete_table_entry()
        self._update_pending_table_writes()

    def _update_pending_table_writes(self):
        self._pending_table_writes[self.partition()][self.key()] = self._pending_table_write
        self._pending_table_offset_increase += 1

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

    def _table_write(self):
        for p, msgs in self._pending_table_writes.items():
            writes = {}
            for key, msg in msgs.items():
                if msg == '-DELETED-':
                    LOGGER.debug('Finalizing table entry delete...')
                    self.app_tables[p].delete(key)
                else:
                    writes[key] = msg
            if writes:
                writes['offset'] = str(self._table_offset() + 2)
                LOGGER.debug(f'Finalizing table entry batch write for p{p}')
                self.app_tables[p].write_batch(writes)

    def _table_offset(self):
        return super()._table_offset() + 2*self._pending_table_offset_increase

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
            LOGGER.info('All partition transactions committed!')
            self._committed = mark_committed
            self._commit_offsets = {}
            self.message_count = 0
            self._retry_offsets = {}
            if self._committed:
                self._active_transaction = False
        if self._pending_table_writes:
            self._table_write()
            self._pending_table_write = None
            self._pending_table_writes = {}
            self._pending_table_offset_increase = 0


class GtfoAutoBatchTableApp(GtfoTableApp):
    def __init__(self, app_function, consume_topic, produce_topic_schema_dict=None, transaction_type=AutoBatchTableTransaction,
                 app_function_arglist=None, metrics_manager=None, schema_registry=None, cluster_name=None, consumer=None, producer=None,
                 time_elapse_max_seconds=None, consume_max_count=None):

        self._time_elapse_start = None

        if not time_elapse_max_seconds:
            time_elapse_max_seconds = int(env_vars()['NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_TIME_SECONDS'])
        if not consume_max_count:
            consume_max_count = int(env_vars()['NU_CONSUMER_DEFAULT_BATCH_CONSUME_MAX_COUNT'])

        self._time_elapse_max_seconds = time_elapse_max_seconds
        self._consume_max_count = consume_max_count

        super().__init__(
            app_function, consume_topic, produce_topic_schema_dict, transaction_type=transaction_type,
            app_function_arglist=app_function_arglist, metrics_manager=metrics_manager, schema_registry=schema_registry, cluster_name=cluster_name, consumer=consumer, producer=producer)

    def prepare_transaction(self, *args, **kwargs):
        return super().consume(*args, auto_consume=False, **kwargs)

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

    def _table_recovery_loop(self, checks=2):
        while self._pending_table_recoveries and checks:
            try:
                LOGGER.info(f'Consuming from changelog partitions: {list(self._active_table_changelog_partitions.keys())}')
                self.prepare_transaction()
                if self._time_elapse_max_seconds:
                    self._time_elapse_start = datetime.now().timestamp()
                LOGGER.debug(f'Processing up to {self._consume_max_count} messages for up to {self._time_elapse_max_seconds} seconds!')
                try:
                    while self._keep_consuming() and self._pending_table_recoveries and checks:
                        self.transaction.consume()
                        self.transaction._recover_table_via_changelog()
                        p = self.transaction.partition()
                        LOGGER.info(
                            f"transaction_offset - {self.transaction.offset() + 2}, watermark - {self._pending_table_recoveries[p]['watermarks'][1]}")
                        if self._pending_table_recoveries[p]['watermarks'][1] - (self.transaction.offset() + 2) <= 0:
                            LOGGER.info(f'table partition {p} fully recovered!')
                            del self._pending_table_recoveries[p]
                except NoMessageError:
                    checks -= 1
                    LOGGER.debug(f'No changelog messages, checks remaining: {checks}')
                self.commit()
            except GracefulTransactionFailure:
                self.transaction.abort_active_transaction()
            except FatalTransactionFailure:
                self.transaction.abort_active_transaction()
                raise

    def _app_run(self, *args, **kwargs):
        LOGGER.debug(f'Consuming from partitions: {list(self._active_primary_partitions.keys())}')
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
        if self.transaction._pending_table_offset_increase or self.transaction._commit_offsets:
            self.transaction.commit()
