from asynchat import find_prefix_at_end  # type: ignore
from typing import Union

import serial

from kamzik3 import WriteException
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsControlLoops import control_port_read_loop


# The method is handle_configuration, and it's not in DevicePort,
# but since multiple inheritance is used here we better disable the pylint warning.
# pylint: disable=abstract-method
class DevicePort(Device):
    terminator: Union[bytes, str, int, None] = b"\r\n"
    ac_in_buffer_size = 4096
    ac_out_buffer_size = 4096
    port = None
    baud_rate = None
    parity = None
    stop_bits = None
    byte_size = None
    BAUDRATES = [
        50,
        75,
        110,
        134,
        150,
        200,
        300,
        600,
        1200,
        1800,
        2400,
        4800,
        9600,
        19200,
        38400,
        57600,
        115200,
    ]

    def __init__(
        self,
        port,
        baud_rate=None,
        parity=None,
        stop_bits=None,
        byte_size=None,
        device_id=None,
        config=None,
    ):
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.stop_bits = stop_bits
        self.byte_size = byte_size
        self.port_read_loop = control_port_read_loop
        Device.__init__(self, device_id, config)
        self.ac_in_buffer = b""
        self.incoming = []
        self.buffer = []
        try:
            self.serial_port = serial.serial_for_url(
                self.port,
                baudrate=self.baud_rate,
                parity=self.parity,
                stopbits=self.stop_bits,
                bytesize=self.byte_size,
                timeout=0,
            )

            self.connect()
        except serial.SerialException:
            self.logger.error("Serial port connection exception")
            self.connecting = True
            self.serial_port = None
            self.device_connection_poller.add_connecting_device(self)

    # pylint: disable=unused-argument
    def connect(self, *args):
        Device.connect(self)
        self.port_read_loop.add_device(self)

    def handshake(self):
        self.logger.info("Handshake initiated")
        return True

    def read_all(self):
        if self.serial_port.in_waiting > 0:
            if self.command_encoding is not None:
                return self.serial_port.read(self.serial_port.in_waiting).decode(
                    self.command_encoding
                )
            else:
                return self.serial_port.read(self.serial_port.in_waiting)
        else:
            return None

    def handle_connect_event(self):
        if self.handshake():
            Device.handle_connect_event(self)

    def push(self, data: Union[str, bytes]):
        if self.serial_port.write(data) != len(data):
            raise WriteException(
                "Size of written data and written length is not equal."
            )

    def close_connection(self):
        Device.close_connection(self)

    def close(self):
        self.connected = False
        self.connecting = False
        self.closing = True
        self.port_read_loop.remove_device(self)

        if self.serial_port is not None:
            self.serial_port.close()

        self.closing = False
        self.closed = True
        self.set_status(STATUS_DISCONNECTED)
        # if self.response_error or self.connection_error:
        #     self.reconnect()

    def _collect_incoming_data(self, data):
        self.incoming.append(data)

    def _get_data(self):
        d = "".join(self.incoming)
        del self.incoming[:]
        return d

    def set_terminator(self, term: Union[bytes, str, int, None]) -> None:
        """
        Set the input delimiter.

        :param term: str, int, None
        :return:
        """
        self.terminator = term

    def get_terminator(self):
        return self.terminator

    # grab some more data from the socket,
    # throw it to the collector method,
    # check for the terminator,
    # if found, transition to the next state.

    def handle_read(self):

        if self.serial_port.in_waiting > 0:
            self.ac_in_buffer += self.serial_port.read(self.serial_port.in_waiting)
        else:
            return

        # Continue to search for self.terminator in self.ac_in_buffer,
        # while calling self.collect_incoming_data.  The while loop
        # is necessary because we might read several data+terminator
        # combos with a single recv(4096).

        while self.ac_in_buffer:
            lb = len(self.ac_in_buffer)
            terminator = self.get_terminator()
            if not terminator:
                # no terminator, collect it all
                self.collect_incoming_data(self.ac_in_buffer)
                self.ac_in_buffer = b""
            elif isinstance(terminator, int):
                # numeric terminator
                n = terminator
                if lb < n:
                    self.collect_incoming_data(self.ac_in_buffer)
                    self.ac_in_buffer = b""
                    self.terminator = self.terminator - lb
                else:
                    self.collect_incoming_data(self.ac_in_buffer[:n])
                    self.ac_in_buffer = self.ac_in_buffer[n:]
                    self.terminator = 0
                    self.found_terminator()
            else:
                # 3 cases:
                # 1) end of buffer matches terminator exactly:
                #    collect data, transition
                # 2) end of buffer matches some prefix:
                #    collect data to the prefix
                # 3) end of buffer does not match any prefix:
                #    collect data
                terminator_len = len(terminator)
                index = self.ac_in_buffer.find(terminator)
                if index != -1:
                    # we found the terminator
                    if index > 0:
                        # don't bother reporting the empty string
                        # (source of subtle bugs)
                        self.collect_incoming_data(self.ac_in_buffer[:index])
                    self.ac_in_buffer = self.ac_in_buffer[index + terminator_len :]
                    # This does the Right Thing if the terminator
                    # is changed here.
                    self.found_terminator()
                else:
                    # check for a prefix of the terminator
                    index = find_prefix_at_end(self.ac_in_buffer, terminator)
                    if index:
                        if index != lb:
                            # we found a prefix, collect up to the prefix
                            self.collect_incoming_data(self.ac_in_buffer[:-index])
                            self.ac_in_buffer = self.ac_in_buffer[-index:]
                        break
                    else:
                        # no prefix, collect it all
                        self.collect_incoming_data(self.ac_in_buffer)
                        self.ac_in_buffer = b""
