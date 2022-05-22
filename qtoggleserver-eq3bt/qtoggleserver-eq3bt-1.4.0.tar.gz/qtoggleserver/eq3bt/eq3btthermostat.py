
import datetime

from typing import List, Optional, Type

from qtoggleserver.core import ports as core_ports
from qtoggleserver.lib import ble

from .exceptions import EQ3Exception


class EQ3BTThermostat(ble.BLEPeripheral):
    WRITE_HANDLE = 0x0410
    NOTIFY_HANDLE = 0x0420

    STATUS_SEND_HEADER = 0x03
    STATUS_RECV_HEADER = 0x02

    STATUS_MANUAL_MASK = 0x01
    STATUS_BOOST_MASK = 0x04
    STATUS_LOCKED_MASK = 0x20

    STATUS_BITS_INDEX = 2
    STATUS_TEMP_INDEX = 5

    WRITE_TEMP_HEADER = 0x41
    WRITE_MANUAL_HEADER = 0x40
    WRITE_BOOST_HEADER = 0x45
    WRITE_LOCKED_HEADER = 0x80

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._temp: Optional[float] = None
        self._manual: Optional[bool] = False
        self._boost: Optional[bool] = False
        self._locked: Optional[bool] = False

    async def set_temp(self, temp: float) -> None:
        self.debug('setting temperature to %.1f degrees', temp)

        await self.write(self.WRITE_HANDLE, bytes([self.WRITE_TEMP_HEADER, int(temp * 2)]))
        self.debug('successfully set temperature')
        self._temp = temp

    def get_temp(self) -> Optional[float]:
        return self._temp

    async def set_manual(self, manual: bool) -> None:
        self.debug('%s manual mode', ['disabling', 'enabling'][manual])

        await self.write(self.WRITE_HANDLE, bytes([self.WRITE_MANUAL_HEADER, 0x40 if manual else 0x00]))
        self.debug('successfully set manual mode')
        self._manual = manual

    def get_manual(self) -> Optional[bool]:
        return self._manual

    async def set_boost(self, boost: bool) -> None:
        self.debug('%s boost', ['disabling', 'enabling'][boost])

        await self.write(self.WRITE_HANDLE, bytes([self.WRITE_BOOST_HEADER, int(boost)]))
        self.debug('successfully set boost')
        self._boost = boost

    def get_boost(self) -> Optional[bool]:
        return self._boost

    async def set_locked(self, locked: bool) -> None:
        self.debug(['unlocked', 'locked'][locked])

        await self.write(self.WRITE_HANDLE, bytes([self.WRITE_LOCKED_HEADER, int(locked)]))
        self.debug('successfully set locked')
        self._locked = locked

    def get_locked(self) -> Optional[bool]:
        return self._locked

    async def make_port_args(self) -> List[Type[core_ports.BasePort]]:
        from .ports import Temperature, Manual, Boost, Locked

        return [
            Temperature,
            Manual,
            Boost,
            Locked
        ]

    async def poll(self) -> None:
        await self._read_config()

    async def _read_config(self) -> None:
        # Reset polled values so that, in case of error, old values aren't reused
        self._temp = None
        self._boost = None

        data = await self.write_wait_notify(
            self.WRITE_HANDLE,
            self.NOTIFY_HANDLE,
            bytes([self.STATUS_SEND_HEADER] + self._make_status_value()),
        )

        if not data:
            raise EQ3Exception('Null notification data')

        if len(data) < 6:
            raise EQ3Exception(f'Notification data too short {self.pretty_data(data)}')

        if data[0] != self.STATUS_RECV_HEADER:
            raise EQ3Exception(f'Unexpected notification data header: {data[0]:02X}')

        self._temp = data[self.STATUS_TEMP_INDEX] / 2.0
        self._manual = bool(data[self.STATUS_BITS_INDEX] & self.STATUS_MANUAL_MASK)
        self._boost = bool(data[self.STATUS_BITS_INDEX] & self.STATUS_BOOST_MASK)
        self._locked = bool(data[self.STATUS_BITS_INDEX] & self.STATUS_LOCKED_MASK)

        self.debug('temperature is %.1f degrees', self._temp)
        self.debug('manual mode is %s', ['disabled', 'enabled'][self._manual])
        self.debug('boost mode is %s', ['disabled', 'enabled'][self._boost])
        self.debug('thermostat is %s', ['unlocked', 'locked'][self._locked])

    @staticmethod
    def _make_status_value() -> List[int]:
        now = datetime.datetime.now()

        return [
            now.year - 2000,
            now.month,
            now.day,
            now.hour,
            now.minute,
            now.second
        ]
