import logging
import time
from serial import Serial
from enum import Enum


class MessageCommand(Enum):
    NONE = 0
    CHUTE = 1
    FEEDER = 2

class KnikkerSorteerMachine:
    """
    A control class for the knikker sorteer machine.
    """

    _serial: Serial = None

    def __init__(self, serial: Serial, log_level: int = logging.INFO):
        self._serial = serial
        logging.basicConfig(level=log_level)

        while self._serial.readline().decode('utf-8').strip() != "READY":
            logging.debug('Waiting for Arduino to become ready...')
            time.sleep(1)

        logging.debug("KnikkerSorteerMachine has initialized")

    def move_chute(self, position: int):
        logging.debug(f"KnikkerSorteerMachine sending CHUTE command with value {position}")
        if position > 6:
            raise ValueError("KnikkerSorteerMachine.move_chute -> position bigger than 6")
        data = bytearray([MessageCommand.CHUTE.value, position])
        self._serial.write(data)

    def feed(self, amount: int = 1):
        logging.debug(f"KnikkerSorteerMachine sending FEEDER command with value {amount}")
        data = bytearray([MessageCommand.FEEDER.value, amount])
        self._serial.write(data)

    def feed_one(self):
        logging.debug(f"KnikkerSorteerMachine sending FEEDER command")
        data = bytearray([MessageCommand.FEEDER.value, 0x0])
        self._serial.write(data)
