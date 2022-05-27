#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Tuya connector API module local device client
"""

# Python base dependencies
import json
import logging
import socket
import time
from typing import Dict, Generator, List, Optional, Tuple, Union

# Library dependencies
from tuyaface.const import CMD_TYPE

# Library libs
from fastybird_tuya_connector.logger import Logger
from fastybird_tuya_connector.protocol.local import TuyaLocalProtocol
from fastybird_tuya_connector.types import DeviceProtocolVersion


class DeviceLocalApi:  # pylint: disable=too-many-instance-attributes
    """
    Tuya device local UDP client

    @package        FastyBird:TuyaConnector!
    @module         api/localapi

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __ip_address: str

    __last_reconnect: float = 0.0

    __sequence_nr: int = 0

    __tuya_protocol: TuyaLocalProtocol

    __connection: Optional[socket.socket] = None

    __logger: Union[Logger, logging.Logger]

    __RECONNECT_COOL_DOWN_TIME: float = 5.0

    __SOCKET_TIMEOUT: float = 0.5
    __SOCKET_PORT: int = 6668

    __MAX_RECONNECT: int = 5

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        device_identifier: str,
        local_key: str,
        ip_address: str,
        gateway_identifier: Optional[str] = None,
        protocol_version: DeviceProtocolVersion = DeviceProtocolVersion.V33,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__ip_address = ip_address

        self.__last_reconnect = 0.0

        self.__tuya_protocol = TuyaLocalProtocol(
            device_identifier=device_identifier,
            device_key=local_key,
            gateway_identifier=gateway_identifier if gateway_identifier is not None else device_identifier,
            protocol_version=protocol_version,
            logger=logger,
        )

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def connect(self) -> None:
        """Connect to local device"""
        if self.__connection is None:
            try:
                self.__logger.info("(%s) Connecting to %s", self.__ip_address, self.__ip_address)

                self.__connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                self.__connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.__connection.settimeout(self.__SOCKET_TIMEOUT)

                self.__connection.connect((self.__ip_address, self.__SOCKET_PORT))

                self.__logger.info("(%s) connected", self.__ip_address)

            except socket.error:
                self.__logger.error("(%s) exception when opening socket", self.__ip_address)

    # -----------------------------------------------------------------------------

    def disconnect(self) -> None:
        """Disconnect from local device"""
        if self.__connection is not None:
            try:
                self.__connection.shutdown(socket.SHUT_RDWR)
                self.__connection = None

            except socket.error:
                pass

    # -----------------------------------------------------------------------------

    def is_connected(self) -> bool:
        """Check if we are connected to local device"""
        return self.__connection is not None

    # -----------------------------------------------------------------------------

    def read_states(
        self,
        reconnect_cnt: Optional[int] = None,
    ) -> Optional[Dict[str, Union[str, int, Dict[str, Union[int, float, bool, str]]]]]:
        """Get device status"""
        if not self.is_connected():
            self.connect()

        try:
            response, _ = self.__read_from_device(command=CMD_TYPE.DP_QUERY)

            if response is None:
                response = {"data": "{}"}

            data = json.loads(str(response.get("data")))

            return data  # type: ignore[no-any-return]

        except socket.error as ex:
            self.__logger.debug("(%s) exception when reading status", self.__ip_address)
            self.__logger.exception(ex)

            if reconnect_cnt is None or reconnect_cnt < self.__MAX_RECONNECT:
                self.__reconnect()

                return self.read_states(
                    reconnect_cnt=(self.__MAX_RECONNECT if reconnect_cnt is None else (int(str(reconnect_cnt)) - 1)),
                )

        return None

    # -----------------------------------------------------------------------------

    def write_states(
        self,
        value: Dict[Union[str, int], Union[int, float, bool, str]],
        reconnect_cnt: Optional[int] = None,
    ) -> bool:
        """Set device status"""
        if not self.is_connected():
            self.connect()

        try:
            response, _ = self.__write_to_device(dps=value)

            if not response or ("rc" in response and response.get("rc") != 0):
                return False

            return True

        except socket.error:
            self.__logger.debug("(%s) exception when writing status", self.__ip_address)

            if reconnect_cnt is None or reconnect_cnt < self.__MAX_RECONNECT:
                self.__reconnect()

                return self.write_states(
                    value=value,
                    reconnect_cnt=(self.__MAX_RECONNECT if reconnect_cnt is None else (int(str(reconnect_cnt)) - 1)),
                )

        return False

    # -----------------------------------------------------------------------------

    def write_state(self, value: Union[int, float, bool, str], idx: int = 1) -> bool:
        """Set state"""
        return self.write_states({idx: value})

    # -----------------------------------------------------------------------------

    def __read_from_device(
        self,
        command: CMD_TYPE,
        recurse_cnt: int = 0,
    ) -> Tuple[Optional[Dict[str, Union[int, str]]], List[Dict[str, Union[int, str]]]]:
        """Send current status request to the Tuya device and waits for status update"""
        request_cnt = self.__send_request(command=command)

        replies: List[Dict[str, Union[int, str]]] = []
        request_reply: Optional[Dict[str, Union[int, str]]] = None
        status_reply: Optional[Dict[str, Union[int, str]]] = None

        # There might already be data waiting in the socket, e.g. a heartbeat reply, continue reading until
        # the expected response has been received or there is a timeout
        # If status is triggered by DP_QUERY, the status is in a DP_QUERY message
        # If status is triggered by CONTROL_NEW, the status is a STATUS message
        while request_reply is None or (command == CMD_TYPE.CONTROL_NEW and status_reply is None):
            received_replies = list(reply for reply in self.__receive_replies(max_receive_cnt=1))

            replies = replies + received_replies

            request_reply = self.__select_reply(replies=replies, command=command, seq=request_cnt)
            status_reply = self.__select_reply(replies=replies, command=CMD_TYPE.STATUS)

            if len(received_replies) == 0:
                break

        # If there is valid reply to CMD_TYPE.DP_QUERY, use it as status reply
        if (
            command == CMD_TYPE.DP_QUERY
            and request_reply is not None
            and "data" in request_reply
            and request_reply["data"] != "json obj data invalid"
        ):
            status_reply = request_reply

        if not status_reply and recurse_cnt < 3:
            if request_reply and request_reply["data"] == "json obj data invalid":
                # Some devices (ie LSC Bulbs) only offer partial status with CONTROL_NEW instead of DP_QUERY
                status_reply, new_replies = self.__read_from_device(
                    command=CMD_TYPE.CONTROL_NEW,
                    recurse_cnt=(recurse_cnt + 1),
                )

            else:
                status_reply, new_replies = self.__read_from_device(
                    command=command,
                    recurse_cnt=(recurse_cnt + 1),
                )

            replies = replies + new_replies

        return status_reply, replies

    # -----------------------------------------------------------------------------

    def __write_to_device(
        self,
        dps: Dict[Union[str, int], Union[int, float, bool, str]],
    ) -> Tuple[Optional[Dict[str, Union[int, str]]], List[Dict[str, Union[int, str]]]]:
        """Send state update request to the Tuya device and waits response"""
        request_cnt = self.__send_request(command=CMD_TYPE.CONTROL, payload={str(k): v for k, v in dps.items()})

        replies: List[Dict[str, Union[int, str]]] = []
        request_reply: Optional[Dict[str, Union[int, str]]] = None

        # There might already be data waiting in the socket, e.g. a heartbeat reply, continue reading until
        # the expected response has been received or there is a timeout
        while request_reply is None:
            received_replies = list(reply for reply in self.__receive_replies(max_receive_cnt=1))

            replies = replies + received_replies

            request_reply = self.__select_reply(replies=replies, command=CMD_TYPE.CONTROL, seq=request_cnt)

            if len(received_replies) == 0:
                break

        return request_reply, replies

    # -----------------------------------------------------------------------------

    def __send_request(
        self,
        command: CMD_TYPE = CMD_TYPE.DP_QUERY,
        payload: Optional[Dict[Union[str, int], Union[int, float, bool, str]]] = None,
    ) -> int:
        """Connect to the Tuya device and send a request"""
        if self.__connection is None:
            raise Exception("Connection to device isn't established")

        self.__sequence_nr = self.__sequence_nr + 1

        request = self.__tuya_protocol.build_payload(
            sequence_nr=self.__sequence_nr,
            command=command,
            data=payload,
        )

        self.__logger.debug(
            "(%s) sending msg (seq %s): [%x:%s] payload: [%s]",
            self.__ip_address,
            self.__sequence_nr,
            command,
            CMD_TYPE(command).name,
            payload,
        )

        try:
            self.__connection.send(request)

        except Exception as ex:
            raise ex

        return self.__sequence_nr

    # -----------------------------------------------------------------------------

    def __receive_replies(self, max_receive_cnt: int) -> Generator:
        if max_receive_cnt <= 0:
            return

        if self.__connection is None:
            raise Exception("Connection to device isn't established")

        try:
            data = self.__connection.recv(4096)

            for reply in self.__tuya_protocol.decode_payload(raw_reply=data):
                yield reply

        except socket.timeout:
            pass

        except Exception as ex:
            raise ex

        yield from self.__receive_replies(max_receive_cnt=(max_receive_cnt - 1))

    # -----------------------------------------------------------------------------

    def __select_reply(
        self,
        replies: List[Dict[str, Union[int, str]]],
        command: CMD_TYPE,
        seq: Optional[int] = None,
    ) -> Optional[Dict[str, Union[int, str]]]:
        """Find a valid command reply"""
        filtered_replies = list(filter(lambda x: x["cmd"] == command, replies))

        if seq is not None:
            filtered_replies = list(filter(lambda x: x["seq"] == seq, filtered_replies))

        if len(filtered_replies) == 0:
            return None

        if len(filtered_replies) > 1:
            self.__logger.info(
                "Got multiple replies %s for request [%x:%s]",
                filtered_replies,
                command,
                CMD_TYPE(command).name,
            )

        return filtered_replies[0]

    # -----------------------------------------------------------------------------

    def __reconnect(self) -> None:
        self.__logger.warning("(%s) reconnecting", self.__ip_address)

        now = time.time()

        if now - self.__last_reconnect < self.__RECONNECT_COOL_DOWN_TIME:
            self.__logger.debug("(%s) waiting before reconnecting", self.__ip_address)

            time.sleep(self.__RECONNECT_COOL_DOWN_TIME)

        self.__last_reconnect = time.time()

        if self.__connection is not None:
            try:
                self.__connection.close()

            except socket.error:
                self.__logger.error("(%s) exception when closing socket", self.__ip_address)

            self.__connection = None

        self.connect()
