# Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
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

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import List

from google.protobuf.empty_pb2 import Empty
from google.protobuf.text_format import MessageToString
from th2_common.schema.message.message_listener import MessageListener
from th2_grpc_common.common_pb2 import MessageBatch, EventID
from th2_grpc_crawler_data_processor.crawler_data_processor_pb2 import Status, \
    MessageResponse, DataProcessorInfo, EventResponse
from th2_grpc_crawler_data_processor.crawler_data_processor_pb2_grpc import DataProcessorServicer

from th2_check2_recon.common import MessageUtils
from th2_check2_recon.reconcommon import ReconMessage

logger = logging.getLogger(__name__)


class AbstractHandler(MessageListener, ABC):
    def __init__(self, rule) -> None:
        self._rule = rule

    @abstractmethod
    def handler(self, attributes: tuple, batch):
        pass


class MessageHandler(AbstractHandler):
    def handler(self, attributes: tuple, batch: MessageBatch):
        try:
            for proto_message in batch.messages:
                message = ReconMessage(proto_message=proto_message)

                process_timer = self._rule.RULE_PROCESSING_TIME
                start_time = time.time()

                self._rule.process(message, attributes)

                process_timer.observe(time.time() - start_time)

                logger.debug("Processed '%s' id='%s'",
                             proto_message.metadata.message_type,
                             MessageUtils.str_message_id(proto_message))

            logger.debug("Cache size '%s': %s.", self._rule.get_name(), self._rule.log_groups_size())
        except Exception:
            logger.exception(f'Rule: {self._rule.get_name()}. '
                             f'An error occurred while processing the received message. '
                             f'Message: {MessageToString(batch, as_one_line=True)}')


class GRPCHandler(DataProcessorServicer):

    def __init__(self, rules: List, root_event_id: EventID) -> None:
        self._rules = rules
        self._recon_root_event_id = root_event_id

    def CrawlerConnect(self, request, context):
        logger.debug('CrawlerId {0} connected'.format(request.id.name))
        version = '1.0.0'
        return DataProcessorInfo(name='Recon Data Processor', version=version)

    def IntervalStart(self, request, context):
        logger.debug('Interval set from {0} to {1}'.format(request.start_time, request.end_time))
        return Empty()

    def SendEvent(self, request, context):
        logger.debug('CrawlerID {0} sent events {1}'.format(request.id.name,
                                                            MessageToString(request.event_data, as_one_line=True)))
        return EventResponse(id=self._recon_root_event_id, status=Status(handshake_required=False))

    def SendMessage(self, request, context):
        try:
            logger.debug('CrawlerID %s sent %s messages', request.id.name, len(request.message_data))
            messages = [data.message for data in request.message_data]
            for proto_message in messages:
                message = ReconMessage(proto_message=proto_message)
                for rule in self._rules:
                    process_timer = rule.RULE_PROCESSING_TIME
                    start_time = time.time()
                    try:
                        rule.process(message, ())
                    except Exception:
                        logger.exception(f'Rule: {rule.get_name()}. '
                                         f'An error occurred while processing the message. '
                                         f'Message: {MessageToString(proto_message, as_one_line=True)}')
                    finally:
                        process_timer.observe(time.time() - start_time)
                logger.debug("Processed '%s' id='%s'",
                             proto_message.metadata.message_type, MessageUtils.str_message_id(proto_message))
            return MessageResponse(ids=[msg.metadata.id for msg in messages], status=Status(handshake_required=False))
        except Exception as e:
            logger.exception('SendMessage request failed')
            return MessageResponse(ids=[], status=Status(handshake_required=True))
