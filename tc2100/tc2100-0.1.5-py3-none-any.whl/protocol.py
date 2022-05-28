""" Twisted Protocol for the TC2100

To use the Protocol, subclass :py:class:`ThermometerProtocol` and implement
its ``observation_received()`` method to handle messages.
"""
from abc import abstractmethod
from typing import TextIO
from csv import DictWriter
import struct

from twisted.internet.protocol import Protocol

from tc2100.observation import Observation


class ThermometerProtocol(Protocol):
    """ Twisted Protocol for the TC2100

    Subclasses should override the
    :py:meth:`ThermometerProtocol.observation_received` method, which is
    called once for each observation received.
    """
    _header = b"\x65\x14"
    _num_padbytes = 3
    _trailer = b"\x0d\x0a"
    _msglen = 2 + 3 + 2 + Observation.size()
    _data_start = 2 + 3
    _data_len = Observation.size()

    def __init__(self):
        super().__init__()
        self._buf = b""

    @abstractmethod
    def observation_received(self, observation: Observation) -> None:
        """ Callback for received Observation

        :param observation: Temperature update
        """

    def dataReceived(self, data: bytes) -> None:
        self._buf += data

        while self._framing_detector():
            try:
                msg = Observation.from_bytes(
                    self._buf[self._data_start:self._data_start +
                              self._data_len])
                self._buf = self._buf[self._msglen:]
            except (ValueError, struct.error):
                # if we failed to decode, our framing is off
                self._buf = self._buf[1:]
                continue

            self.observation_received(msg)

    def connectionLost(self, reason=None):
        self._buf = b""

    def _framing_detector(self) -> bool:
        """ Perform message boundary detection

        Serial protocols lack inherent framing---divisions between message
        boundaries. Reads might begin in the middle of a message. This
        method synchronizes to the message boundary by advancing `octets`
        until the start of message is found.

        :param data: bytes which may contain a message, not necessarily at
               start
        """

        while len(self._buf) >= self._msglen:
            dstart = self._buf[0:len(self._header)]
            dend = self._buf[self._msglen-len(self._trailer):self._msglen]
            if dstart == self._header and dend == self._trailer:
                return True

            self._buf = self._buf[1:]

        return False


class ThermometerToCSVProtocol(ThermometerProtocol):
    """ Output thermometer measurements as CSV

    .. py:attribute:: file_handle

        An open text stream where output will be written. Files must be
        opened with the ``newline=''`` option.
    """
    def __init__(self, file_handle: TextIO):
        super().__init__()
        self._writer = DictWriter(file_handle,
                                  fieldnames=Observation.field_names())
        self._writer.writeheader()

    def observation_received(self, observation: Observation) -> None:
        self._writer.writerow(observation.as_dict())
