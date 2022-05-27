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
Tuya connector protocol module local protocol
"""

# Python base dependencies
import binascii
import json
import logging
import time
from hashlib import md5
from typing import Dict, Generator, Optional, Union

# Library dependencies
from bitstring import BitArray
from tuyaface import aescipher
from tuyaface.const import CMD_TYPE
from tuyaface.helper import hex2bytes

# Library libs
from fastybird_tuya_connector.logger import Logger
from fastybird_tuya_connector.types import DeviceProtocolVersion


class TuyaLocalProtocol:
    """
    Tuya device local protocol

    @package        FastyBird:TuyaConnector!
    @module         protocol/local

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __device_identifier: str
    __gateway_identifier: str
    __device_key: str
    __protocol_version: DeviceProtocolVersion

    __logger: Union[Logger, logging.Logger]

    # -----------------------------------------------------------------------------

    def __init__(  # pylint: disable=too-many-arguments
        self,
        gateway_identifier: str,
        device_identifier: str,
        device_key: str,
        protocol_version: DeviceProtocolVersion,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        self.__device_identifier = device_identifier
        self.__gateway_identifier = gateway_identifier
        self.__device_key = device_key
        self.__protocol_version = protocol_version

        self.__logger = logger

    # -----------------------------------------------------------------------------

    def build_payload(
        self,
        sequence_nr: int,
        command: CMD_TYPE,
        data: Optional[Dict[Union[str, int], Union[int, float, bool, str]]] = None,
    ) -> bytes:
        """Generate the payload to send"""
        payload_json = (
            self.__generate_json_data(
                gateway_identifier=self.__gateway_identifier,
                device_identifier=self.__device_identifier,
                command=command,
                data=data,
            )
            .replace(" ", "")
            .encode("utf-8")
        )

        header_payload_hb: bytes = b""

        payload_hb = payload_json

        if self.__protocol_version == DeviceProtocolVersion.V31:
            if command == CMD_TYPE.CONTROL:
                payload_crypt = aescipher.encrypt(self.__device_key, payload_json)

                pre_md5_string = b"data=" + payload_crypt + b"||lpv=" + b"3.1||" + self.__device_key.encode()

                md5_hash = md5()
                md5_hash.update(pre_md5_string)

                hex_digest = md5_hash.hexdigest()

                header_payload_hb = b"3.1" + hex_digest[8:][:16].encode("latin1")

                payload_hb = header_payload_hb + payload_crypt

            return self.__stitch_payload(sequence_nr=sequence_nr, payload=payload_hb, command=command)

        if self.__protocol_version == DeviceProtocolVersion.V33:
            if command != CMD_TYPE.DP_QUERY:
                header_payload_hb = b"3.3" + b"\0\0\0\0\0\0\0\0\0\0\0\0"

            payload_crypt = aescipher.encrypt(self.__device_key, payload_json, False)

            return self.__stitch_payload(
                sequence_nr=sequence_nr,
                payload=(header_payload_hb + payload_crypt),
                command=command,
            )

        raise Exception(f"Unknown protocol {self.__protocol_version.value}")

    # -----------------------------------------------------------------------------

    def decode_payload(self, raw_reply: bytes) -> Generator:
        """Split the raw reply(s) into chunks and decrypts it"""
        for splitted in BitArray(raw_reply).split("0x000055aa", bytealigned=True):
            s_bytes = splitted.tobytes()
            payload = None

            # Skip invalid messages
            if len(s_bytes) < 28 or not splitted.endswith("0x0000aa55"):
                continue

            # Parse header
            seq = int.from_bytes(s_bytes[4:8], byteorder="big")
            cmd = int.from_bytes(s_bytes[8:12], byteorder="big")
            size = int.from_bytes(s_bytes[12:16], byteorder="big")
            return_code = int.from_bytes(s_bytes[16:20], byteorder="big")
            has_return_code = (return_code & 0xFFFFFF00) == 0
            crc = int.from_bytes(s_bytes[-8:-4], byteorder="big")

            # Check CRC
            if crc != binascii.crc32(s_bytes[:-8]):
                continue

            if self.__protocol_version == DeviceProtocolVersion.V31:
                data = s_bytes[20:-8]

                if s_bytes[20:21] == b"{":
                    if not isinstance(data, str):
                        payload = data.decode()

                elif s_bytes[20:23] == b"3.1":
                    self.__logger.info("we've got a 3.1 reply, code untested")

                    data = data[3:]  # remove version header

                    # remove (what I'm guessing, but not confirmed is) 16-bytes of MD5 hex digest of payload
                    data = data[16:]
                    payload = aescipher.decrypt(self.__device_key, data)

            elif self.__protocol_version == DeviceProtocolVersion.V33:
                if size > 12:
                    data = s_bytes[20 : 8 + size]

                    if cmd == CMD_TYPE.STATUS:
                        data = data[15:]

                    payload = aescipher.decrypt(self.__device_key, data, False)

            msg = {"cmd": cmd, "seq": seq, "data": payload}

            if has_return_code:
                msg["rc"] = return_code

            self.__logger.debug(
                "Received msg (seq %s): [%x:%s] rc: [%s] payload: [%s]",
                msg["seq"],
                msg["cmd"],
                CMD_TYPE(int(str(msg["cmd"]))).name,
                return_code if has_return_code else "-",
                msg.get("data", ""),
            )

            yield msg

    # -----------------------------------------------------------------------------

    @staticmethod
    def __generate_json_data(
        gateway_identifier: str,
        device_identifier: str,
        command: CMD_TYPE,
        data: Optional[Dict[Union[str, int], Union[int, float, bool, str]]] = None,
    ) -> str:
        """Fill the data structure for the command with the given values"""
        payload_dict: Dict[int, Dict] = {
            CMD_TYPE.CONTROL: {"devId": "", "uid": "", "t": ""},
            CMD_TYPE.STATUS: {"gwId": "", "devId": ""},
            CMD_TYPE.HEART_BEAT: {},
            CMD_TYPE.DP_QUERY: {"gwId": "", "devId": "", "uid": "", "t": ""},
            CMD_TYPE.CONTROL_NEW: {"devId": "", "uid": "", "t": ""},
            CMD_TYPE.DP_QUERY_NEW: {"devId": "", "uid": "", "t": ""},
        }

        json_data: Dict[str, Union[str, Dict[Union[str, int], Union[int, float, bool, str]]]] = payload_dict.get(
            command, {}
        )

        if "gwId" in json_data:
            json_data["gwId"] = gateway_identifier

        if "devId" in json_data:
            json_data["devId"] = device_identifier

        if "uid" in json_data:
            json_data["uid"] = device_identifier  # still use id, no separate uid

        if "t" in json_data:
            json_data["t"] = str(int(time.time()))

        if command == CMD_TYPE.CONTROL_NEW:
            json_data["dps"] = {"1": "", "2": "", "3": ""}

        if data is not None:
            json_data["dps"] = data

        return json.dumps(json_data)

    # -----------------------------------------------------------------------------

    @staticmethod
    def __stitch_payload(sequence_nr: int, payload: bytes, command: CMD_TYPE) -> bytes:
        """Join the payload request parts together."""
        command_hb = command.to_bytes(4, byteorder="big")
        request_cnt_hb = sequence_nr.to_bytes(4, byteorder="big")

        payload_hb = payload + hex2bytes("000000000000aa55")

        payload_hb_len_hs = len(payload_hb).to_bytes(4, byteorder="big")

        header_hb = hex2bytes("000055aa") + request_cnt_hb + command_hb + payload_hb_len_hs
        buffer_hb = header_hb + payload_hb

        # calc the CRC of everything except where the CRC goes and the suffix
        hex_crc = format(binascii.crc32(buffer_hb[:-8]) & 0xFFFFFFFF, "08X")

        return buffer_hb[:-8] + hex2bytes(hex_crc) + buffer_hb[-4:]
