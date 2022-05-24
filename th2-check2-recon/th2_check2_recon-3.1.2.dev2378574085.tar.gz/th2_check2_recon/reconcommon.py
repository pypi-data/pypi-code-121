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

from enum import Enum

from th2_check2_recon.common import MessageUtils


class ReconMessage:
    __slots__ = ("proto_message", "group_info", "group_id", "hash_info", "hash", "is_matched",
                 "is_check_no_match_within_timeout", "_timestamp", "in_shared_groups", '_info')

    def __init__(self, proto_message) -> None:
        self.proto_message = proto_message
        self.group_info = dict()
        self.group_id = None
        self.hash_info = dict()
        self.hash = None
        self.is_matched = False
        self.is_check_no_match_within_timeout = False
        self.in_shared_groups = set()
        self._timestamp = None
        self._info = None

    @property
    def timestamp(self):
        if self._timestamp is None:
            self._timestamp = MessageUtils.get_timestamp_ns(self.proto_message)
        return self._timestamp

    @staticmethod
    def get_info(info_dict: dict) -> str:
        return '[' + ', '.join(f"'{key}': {value}" for key, value in info_dict.items()) + ']'

    @property
    def all_info(self) -> str:
        if self._info is None:
            result = f"'{self.proto_message.metadata.message_type if self.proto_message.metadata.message_type else 'None type '}" \
                     f"' id='{MessageUtils.str_message_id(self.proto_message)}'"
            self._info = result
        else:
            result = self._info
        if self.hash is not None:
            result += f" Hash='{self.hash}'"
        if self.group_id is not None:
            result += f" Group='{self.group_id}'"
        if len(self.hash_info) > 0:
            result += f' Hash{self.get_info(self.hash_info)}'
        if len(self.group_info) > 0:
            result += f' GroupID{self.get_info(self.group_info)}'
        return result


def _get_msg_timestamp(msg: ReconMessage):
    """Used instead of lambda in Rule.__check_and_store_event"""
    return msg.timestamp


class MessageGroupType(Enum):
    single = 1
    multi = 2
    shared = 3
    multi_match_all = 4
