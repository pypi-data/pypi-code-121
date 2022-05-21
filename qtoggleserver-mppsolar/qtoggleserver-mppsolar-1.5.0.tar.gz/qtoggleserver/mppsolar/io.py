
import asyncio
import abc
import os
import serial


class BaseIO(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read_available(self) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def write(self, data: bytes) -> None:
        raise NotImplementedError

    async def read(self, timeout: int) -> bytes:
        data = b''
        for _ in range(timeout * 10):
            data += self.read_available()
            if data.endswith(b'\r'):
                break

            await asyncio.sleep(0.1)

        return data

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class HIDRawIO(BaseIO):
    def __init__(self, device_path: str) -> None:
        self._fd: int = os.open(device_path, flags=os.O_RDWR | os.O_NONBLOCK)

    def read_available(self) -> bytes:
        return os.read(self._fd, 1024)

    def write(self, data: bytes) -> None:
        os.write(self._fd, data)

    def close(self) -> None:
        os.close(self._fd)


class SerialIO(BaseIO):
    def __init__(self, serial_port: str, serial_baud: int) -> None:
        self._serial: serial.Serial = serial.Serial(serial_port, serial_baud)

    def read_available(self) -> bytes:
        in_waiting = self._serial.in_waiting
        if in_waiting:
            return self._serial.read(in_waiting)

        return b''

    def write(self, data: bytes) -> None:
        self._serial.write(data)

    def close(self) -> None:
        self._serial.close()
