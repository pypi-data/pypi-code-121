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
FastyBird BUS connector transporters module PJON transporter
"""

# Python base dependencies
import logging
import time
from typing import Dict, List, Optional, Union

# Library dependencies
from kink import inject

# Library libs
import fastybird_fb_bus_connector.pjon._pjon as pjon  # pylint: disable=no-name-in-module,import-error
from fastybird_fb_bus_connector.logger import Logger
from fastybird_fb_bus_connector.receivers.receiver import Receiver
from fastybird_fb_bus_connector.transporters.transporter import ITransporter
from fastybird_fb_bus_connector.types import Packet, PacketContent, ProtocolVersion


@inject(alias=ITransporter)
class PjonTransporter(ITransporter, pjon.ThroughSerialAsync):  # pylint: disable=no-member
    """
    PJON transporter

    @package        FastyBird:FbBusConnector!
    @module         transporters/pjon

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

    __receiver: Receiver

    __logger: Union[Logger, logging.Logger]

    __MASTER_ADDRESS: int
    __SERIAL_BAUD_RATE: int
    __SERIAL_INTERFACE: str

    __packet_to_be_sent = 0

    # -----------------------------------------------------------------------------

    @inject
    def __init__(  # pylint: disable=too-many-arguments
        self,
        receiver: Receiver,
        address: int,
        baud_rate: int,
        interface: str,
        logger: Union[Logger, logging.Logger] = logging.getLogger("dummy"),
    ) -> None:
        pjon.ThroughSerialAsync.__init__(  # pylint: disable=no-member
            self,
            address if address is not None else self.__MASTER_ADDRESS,
            (interface if interface is not None else self.__SERIAL_INTERFACE).encode("utf-8"),
            baud_rate if baud_rate is not None else self.__SERIAL_BAUD_RATE,
        )

        self.set_synchronous_acknowledge(False)
        self.set_asynchronous_acknowledge(False)

        self.__receiver = receiver

        self.__logger = logger

        self.__packet_to_be_sent = 0

    # -----------------------------------------------------------------------------

    @property
    def packet_to_be_sent(self) -> int:
        """Number of packets waiting in queue"""
        return self.__packet_to_be_sent

    # -----------------------------------------------------------------------------

    def broadcast_packet(self, payload: List[int], waiting_time: float = 0.0) -> bool:
        """Broadcast packet to all devices"""
        return self.send_packet(
            pjon.PJON_BROADCAST,  # pylint: disable=no-member
            payload,
            waiting_time,
        )

    # -----------------------------------------------------------------------------

    def send_packet(self, address: int, payload: List[int], waiting_time: float = 0.0) -> bool:
        """Send packet to specific device address"""
        # Be sure to set the null terminator!!!
        payload.append(PacketContent.TERMINATOR.value)

        self.send(address, bytes(payload))

        # if result != pjon.PJON_ACK:
        #     if result == pjon.PJON_BUSY:
        #         self.__logger.warning(
        #             "Sending packet: %s for device: %s failed, bus is busy",
        #             int(payload[0]),
        #             address
        #         )
        #
        #     elif result == pjon.PJON_FAIL:
        #         self.__logger.warning(
        #             "Sending packet: %s for device: %s failed"
        #             int(payload[0]),
        #             address
        #         )
        #
        #     else:
        #         self.__logger.warning(
        #             "Sending packet: %s for device: %s failed, unknown error"
        #             int(payload[0]),
        #             address
        #         )
        #
        #     return False

        if address == pjon.PJON_BROADCAST:  # pylint: disable=no-member
            self.__logger.debug(
                "Successfully sent broadcast packet: %s",
                payload[1],
                extra={
                    "device": {
                        "address": address,
                    },
                },
            )

        else:
            self.__logger.debug(
                "Successfully sent packet: %s for device with address: %d",
                payload[1],
                address,
                extra={
                    "device": {
                        "address": address,
                    },
                },
            )

        if waiting_time > 0:
            # Store start timestamp
            current_time = time.time()

            while (time.time() - current_time) <= waiting_time:
                _, send_packet_result = self.loop()

                if send_packet_result == pjon.PJON_ACK:  # pylint: disable=no-member
                    return True

            return False

        return True

    # -----------------------------------------------------------------------------

    def handle(self) -> None:
        """Process transporter"""
        try:
            result = self.loop()

            self.__packet_to_be_sent = int(result[0])

        except pjon.PJON_Connection_Lost:  # pylint: disable=no-member
            self.__logger.warning("Connection with device was lost")

        except pjon.PJON_Packets_Buffer_Full:  # pylint: disable=no-member
            self.__logger.warning("Buffer is full")

        except pjon.PJON_Content_Too_Long:  # pylint: disable=no-member
            self.__logger.warning("Content is long")

    # -----------------------------------------------------------------------------

    def receive(self, received_payload: bytes, length: int, packet_info: Dict) -> None:
        """Process received message by transporters"""
        sender_address: Optional[int] = None

        try:
            # Get sender address from header
            sender_address = int(str(packet_info.get("sender_id")))

        except KeyError:
            # Sender address is not present in header
            pass

        raw_payload: List[int] = []

        for char in bytearray(received_payload):
            raw_payload.append(int(char))

        if ProtocolVersion.has_value(int(raw_payload[0])) is False:
            self.__logger.warning(
                "Received unknown protocol version",
                extra={
                    "packet": {
                        "protocol_version": int(raw_payload[0]),
                    },
                },
            )

            return

        if Packet.has_value(int(raw_payload[1])) is False:
            self.__logger.warning(
                "Received unknown packet",
                extra={
                    "packet": {
                        "type": int(raw_payload[1]),
                    },
                },
            )

            return

        if raw_payload[-1] != PacketContent.TERMINATOR.value:
            self.__logger.warning("Missing packet terminator")

            return

        payload = raw_payload[0 : (length - 1)]

        # Get packet identifier from payload
        packet_id = Packet(int(payload[1]))

        self.__logger.debug(
            "Received packet: %s for device with address: %s",
            packet_id,
            sender_address,
        )

        self.__receiver.on_message(
            payload=bytearray(payload),
            length=len(payload),
            address=sender_address,
        )
