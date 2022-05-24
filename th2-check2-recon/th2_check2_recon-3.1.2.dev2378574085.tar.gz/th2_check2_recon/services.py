# Copyright 2020-2020 Exactpro (Exactpro Systems Limited)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import collections
import itertools
import logging
from abc import ABC, abstractmethod
from threading import Lock, Timer
from typing import Optional, Dict, List

import sortedcollections
from google.protobuf import text_format
from th2_common.schema.event.event_batch_router import EventBatchRouter
from th2_grpc_common.common_pb2 import EventStatus, Event, EventBatch, EventID, Message
from th2_grpc_util.util_pb2 import CompareMessageVsMessageRequest, ComparisonSettings, \
    CompareMessageVsMessageTask, CompareMessageVsMessageResult

from th2_check2_recon.common import EventUtils, MessageComponent, VerificationComponent
from th2_check2_recon.reconcommon import ReconMessage, MessageGroupType

logger = logging.getLogger(__name__)


class AbstractService(ABC):

    @abstractmethod
    def stop(self):
        pass


class EventsBatchCollector(AbstractService):

    def __init__(self, event_router, max_batch_size: int, timeout: int) -> None:
        self.max_batch_size = max_batch_size
        self.timeout = timeout  # Send interval

        self.__batches = {}  # {event_id: (event_batch, batch_timer)}
        self.__lock = Lock()
        self.__event_router: EventBatchRouter = event_router

    def put_event(self, event: Event):
        with self.__lock:
            if event.parent_id.id in self.__batches:
                event_batch, batch_timer = self.__batches[event.parent_id.id]
            else:
                event_batch = EventBatch(parent_event_id=event.parent_id)
                batch_timer = self._create_timer(event_batch)
                self.__batches[event.parent_id.id] = (event_batch, batch_timer)

            event_batch.events.append(event)
            if len(event_batch.events) == self.max_batch_size:
                del self.__batches[event.parent_id.id]
                batch_timer.cancel()
                self._send_batch(event_batch)

    def _timer_handle(self, batch: EventBatch):
        with self.__lock:
            if batch.parent_event_id.id in self.__batches:
                del self.__batches[batch.parent_event_id.id]
            else:
                return
        self._send_batch(batch)

    def _send_batch(self, batch: EventBatch):
        try:
            self.__event_router.send(batch)
        except Exception as e:
            logger.exception(F"Error while send EventBatch: {e}")

    def _create_timer(self, batch: EventBatch):
        timer = Timer(self.timeout, self._timer_handle, [batch])
        timer.start()
        return timer

    def stop(self):
        with self.__lock:
            for id, values in self.__batches.items():
                event_batch, batch_timer = values
                batch_timer.cancel()
        with self.__lock:
            for id, values in self.__batches.items():
                event_batch, batch_timer = values
                self._send_batch(event_batch)
            self.__batches.clear()


class EventStore(AbstractService):
    MATCHED_FAILED = 'Matched failed'
    MATCHED_PASSED = 'Matched passed'
    MATCHED_OUT_OF_TIMEOUT = 'Matched out of timeout'
    NO_MATCH_WITHIN_TIMEOUT = 'No match within timeout'
    NO_MATCH = 'No match'
    ERRORS = 'Errors'

    def __init__(self, event_router: EventBatchRouter, report_name: str, event_batch_max_size: int,
                 event_batch_send_interval: int) -> None:
        self.event_router = event_router
        self.__events_batch_collector = EventsBatchCollector(event_router, event_batch_max_size,
                                                             event_batch_send_interval)
        self.__group_event_by_rule_id = dict()

        self.root_event: Event = EventUtils.create_event(name='Recon: ' + report_name, type=EventUtils.EventType.ROOT)
        logger.debug('Created root report Event for Recon: %s',
                     text_format.MessageToString(self.root_event, as_one_line=True))
        self.send_parent_event(self.root_event)

    def send_event(self, event: Event, rule_event_id: EventID, group_event_name: str):
        try:
            if rule_event_id.id not in self.__group_event_by_rule_id:
                self.__group_event_by_rule_id[rule_event_id.id] = dict()
            if group_event_name not in self.__group_event_by_rule_id[rule_event_id.id]:
                group_event = EventUtils.create_event(parent_id=rule_event_id,
                                                      name=group_event_name,
                                                      type=EventUtils.EventType.STATUS)
                logger.debug(f"Create group Event '%s' for rule Event '%s'", group_event_name, rule_event_id)
                self.__group_event_by_rule_id[rule_event_id.id][group_event_name] = group_event
                self.send_parent_event(group_event)

            group_event = self.__group_event_by_rule_id[rule_event_id.id][group_event_name]
            event.id.CopyFrom(EventUtils.new_event_id())
            event.parent_id.CopyFrom(group_event.id)
            self.__events_batch_collector.put_event(event)
        except Exception:
            logger.exception(f'Error while sending event')

    def send_parent_event(self, event: Event):
        event_batch = EventBatch()
        event_batch.events.append(event)
        self.event_router.send(event_batch)

    def store_no_match_within_timeout(self, rule_event_id: EventID, recon_message: ReconMessage,
                                      actual_timestamp: int, timeout: int):
        name = f'{recon_message.all_info}'

        units = ['sec', 'ms', 'mcs', 'ns']
        factor_units = [1_000_000_000, 1_000_000, 1_000, 1]
        for unit, factor_unit in zip(units, factor_units):
            if not any((actual_timestamp % factor_unit, recon_message.timestamp % factor_unit, timeout % factor_unit)):
                break

        actual_timestamp = int(actual_timestamp / factor_unit)
        message_timestamp = int(recon_message.timestamp / factor_unit)
        timeout = int(timeout / factor_unit)

        event_message = f"Timestamp of the last received message: '{actual_timestamp:,}' {unit}\n" \
                        f"Timestamp this message: '{message_timestamp:,}' {unit}\n" \
                        f"Timeout: '{timeout:,}' {unit}"
        body = EventUtils.create_event_body(MessageComponent(event_message))
        attached_message_ids = self._get_attached_message_ids(recon_message)
        event = EventUtils.create_event(name=name,
                                        body=body,
                                        attached_message_ids=attached_message_ids,
                                        type=EventUtils.EventType.EVENT)
        logger.debug("Create '%s' Event for rule Event '%s'", self.NO_MATCH_WITHIN_TIMEOUT, rule_event_id)
        self.send_event(event, rule_event_id, self.NO_MATCH_WITHIN_TIMEOUT)

    def store_message_removed(self, rule_event_id: EventID, message: ReconMessage, event_message: str):
        name = f"Remove {message.all_info}"
        event_message += f"\n Message {'not' if not message.is_matched else ''} matched"
        body = EventUtils.create_event_body(MessageComponent(event_message))
        attached_message_ids = self._get_attached_message_ids(message)
        event = EventUtils.create_event(name=name,
                                        body=body,
                                        status=EventStatus.SUCCESS if message.is_matched else EventStatus.FAILED,
                                        attached_message_ids=attached_message_ids,
                                        type=EventUtils.EventType.EVENT)
        logger.debug("Create '%s' Event for rule Event '%s'", self.NO_MATCH, rule_event_id)
        self.send_event(event, rule_event_id, self.NO_MATCH)

    def store_error(self, rule_event_id: EventID, event_name: str, error_message: str,
                    messages: List[ReconMessage] = None):
        body = EventUtils.create_event_body(MessageComponent(error_message))
        attached_message_ids = self._get_attached_message_ids(*messages)
        event = EventUtils.create_event(name=event_name,
                                        status=EventStatus.FAILED,
                                        attached_message_ids=attached_message_ids,
                                        body=body,
                                        type=EventUtils.EventType.EVENT)
        logger.debug("Create '%s' Event for rule Event '%s'", self.ERRORS, rule_event_id)
        self.send_event(event, rule_event_id, self.ERRORS)

    def store_matched_out_of_timeout(self, rule_event_id: EventID, check_event: Event):
        self.send_event(check_event, rule_event_id, self.MATCHED_OUT_OF_TIMEOUT)

    def store_matched(self, rule_event_id: EventID, check_event: Event):
        if check_event.status == EventStatus.SUCCESS:
            self.send_event(check_event, rule_event_id, self.MATCHED_PASSED)
        else:
            self.send_event(check_event, rule_event_id, self.MATCHED_FAILED)

    def stop(self):
        self.__events_batch_collector.stop()

    def _get_attached_message_ids(self, *recon_msgs):
        try:
            return [message.proto_message.metadata.id for message in recon_msgs]
        except AttributeError:
            return []


class MessageComparator(AbstractService):

    def __init__(self, comparator_service) -> None:
        self.__comparator_service = comparator_service

    def compare(self, expected: Message, actual: Message,
                settings: ComparisonSettings) -> CompareMessageVsMessageResult:
        return self.comparing(expected, actual, settings)

    def comparing(self, expected: Message, actual: Message,
                  settings: ComparisonSettings) -> CompareMessageVsMessageResult:
        request = CompareMessageVsMessageRequest(
            comparison_tasks=[CompareMessageVsMessageTask(first=expected, second=actual,
                                                          settings=settings)])
        try:
            compare_response = self.__comparator_service.compareMessageVsMessage(request)
            for compare_result in compare_response.comparison_results:  # TODO  fix it
                return compare_result
        except Exception:
            logger.exception(f'Error while comparing. CompareMessageVsMessageRequest: {request}')

    def compare_messages(self, messages: [ReconMessage],
                         ignore_fields: [str] = None) -> Optional[VerificationComponent]:
        if len(messages) != 2:
            logger.exception(f'The number of messages to compare must be 2.')
            return
        settings = ComparisonSettings()
        if ignore_fields is not None:
            settings.ignore_fields.extend(ignore_fields)

        compare_result = self.compare(messages[0].proto_message, messages[1].proto_message, settings)
        return VerificationComponent(compare_result.comparison_result)

    def stop(self):
        pass


class Cache(AbstractService):

    __slots__ = 'rule', 'capacity', 'event_store', 'rule_event', '_message_groups'

    def __init__(self, rule, cache_size) -> None:
        self.rule = rule
        self.capacity = cache_size
        self.event_store = self.rule.event_store
        self.rule_event = self.rule.rule_event
        message_group_types = self.rule.description_of_groups_bridge()

        self._message_groups = dict()

        for message_group_id, message_group_type in message_group_types.items():
            if MessageGroupType.shared not in message_group_type:
                self._message_groups[message_group_id] = Cache.MessageGroup(id=message_group_id,
                                                                            capacity=cache_size,
                                                                            type=message_group_type,
                                                                            event_store=self.event_store,
                                                                            parent_event=self.rule_event)
            else:
                if message_group_id not in self.rule.recon.shared_message_groups:
                    self.rule.recon.shared_message_groups[message_group_id] = Cache.MessageGroup(id=message_group_id,
                                                                                             capacity=cache_size,
                                                                                             type=message_group_type,
                                                                                             event_store=self.event_store,
                                                                                             parent_event=self.rule_event)
                self._message_groups[message_group_id] = self.rule.recon.shared_message_groups[message_group_id]
        has_multi = any(MessageGroupType.multi in group.type for group in self.message_groups.values())
        for group in self.message_groups.values():
            if has_multi:
                if MessageGroupType.single in group.type:
                    group.is_cleanable = False

    @property
    def message_groups(self):
        return self._message_groups

    def stop(self):
        for group in self.message_groups.values():
            group.clear()

    class MessageGroup:

        __slots__ = 'id', 'capacity', 'size', 'type', 'event_store', 'parent_event', 'is_cleanable', 'data', 'hash_by_sorted_timestamp'

        def __init__(self, id: str, capacity: int, type: {MessageGroupType}, event_store: EventStore,
                     parent_event: Event) -> None:
            self.id = id
            self.capacity = capacity
            self.size = 0
            self.type: {MessageGroupType} = type
            self.event_store = event_store
            self.parent_event: Event = parent_event

            self.is_cleanable = True
            self.data: Dict[int, List[ReconMessage]] = collections.defaultdict(list)  # {ReconMessage.hash: [ReconMessage]}
            self.hash_by_sorted_timestamp: Dict[
                int, List[int]] = sortedcollections.SortedDict()  # {timestamp: [ReconMessage.hash]}

        def put(self, message: ReconMessage):
            if self.size < self.capacity:
                if message.hash in self.data and MessageGroupType.single in self.type:
                    cause = f"The message was deleted because a new one came with the same hash '{message.hash}' " \
                            f"in message group '{self.id}'"
                    self.remove(message.hash, cause)

                self.data[message.hash].append(message)
                self.hash_by_sorted_timestamp.setdefault(message.timestamp, []).append(message.hash)
                self.size += 1
            else:
                timestamp_for_remove = next(iter(self.hash_by_sorted_timestamp.keys()))
                hash_for_remove = self.hash_by_sorted_timestamp[timestamp_for_remove][0]
                cause = f"The message was deleted because there was no free space in the message group '{self.id}'"
                self.remove(hash_for_remove, cause, remove_all=False)
                self.put(message)

        def check_no_match_within_timeout(self, actual_timestamp: int, timeout: int):
            lower_bound_timestamp = actual_timestamp - timeout
            for timestamp, hashes in self.hash_by_sorted_timestamp.items():
                if timestamp < lower_bound_timestamp:
                    old_hash = hashes[0]
                    for recon_message in self.data[old_hash]:
                        if not recon_message.is_matched and not recon_message.is_check_no_match_within_timeout:
                            recon_message.is_check_no_match_within_timeout = True
                            self.event_store.store_no_match_within_timeout(self.parent_event.id, recon_message,
                                                                           actual_timestamp, timeout)
                else:
                    break

        def remove(self, hash_of_message: int, cause=None, remove_all=True):
            message_for_remove = None
            if remove_all:
                for message_for_remove in self.data[hash_of_message]:
                    timestamp_for_remove = message_for_remove.timestamp
                    self.hash_by_sorted_timestamp[timestamp_for_remove].remove(hash_of_message)
                    if len(self.hash_by_sorted_timestamp[timestamp_for_remove]) == 0:
                        del self.hash_by_sorted_timestamp[timestamp_for_remove]
                    self.size -= 1
                del self.data[hash_of_message]
            else:
                message_for_remove = self.data[hash_of_message][0]
                timestamp_for_remove = message_for_remove.timestamp

                self.data[hash_of_message].remove(message_for_remove)
                if len(self.data[hash_of_message]) == 0:
                    del self.data[hash_of_message]

                self.hash_by_sorted_timestamp[timestamp_for_remove].remove(hash_of_message)
                if len(self.hash_by_sorted_timestamp[timestamp_for_remove]) == 0:
                    del self.hash_by_sorted_timestamp[timestamp_for_remove]
                self.size -= 1

            if cause is not None:
                self.event_store.store_message_removed(rule_event_id=self.parent_event.id,
                                                       message=message_for_remove,
                                                       event_message=cause)

        def clear(self):
            cause = "The message was deleted because the Recon stopped"
            while len(self.data) != 0:
                hash_for_remove = next(iter(self.data.keys()))
                while hash_for_remove in self.data and len(self.data[hash_for_remove]) != 0:
                    self.remove(hash_for_remove, cause, remove_all=False)

        def wipe(self):
            self.data.clear()
            self.hash_by_sorted_timestamp.clear()
            self.size = 0

        def clear_out_of_timeout(self, clean_timestamp):
            hashes_to_removal = list()
            for timestamp, hashes in self.hash_by_sorted_timestamp.items():
                if timestamp < clean_timestamp:
                    hashes_to_removal.append(hashes)
                else:
                    break
            for hash_to_remove in itertools.chain.from_iterable(hashes_to_removal):
                self.remove(hash_to_remove, remove_all=False)

        def __iter__(self):
            """Generator that yields all messages in the group"""
            for recon_mgs_lst in self.data.values():
                for msg in recon_mgs_lst:
                    yield msg

        def __contains__(self, hash_of_message: int):
            return hash_of_message in self.data
