
import abc
import logging
import struct

from typing import Any, Dict, List

from qtoggleserver.lib import ble

from . import constants
from . import ports as mppsolarports
from .inverter import MPPSolarInverter
from .typing import Property


logger = logging.getLogger(__name__)


class BluetoothPort(ble.BLEPort, metaclass=abc.ABCMeta):
    READ_INTERVAL_MAX = 86400
    READ_INTERVAL_STEP = 1
    READ_INTERVAL_MULTIPLIER = 1


class BooleanPort(mppsolarports.BooleanPort, BluetoothPort):
    pass


class NumberPort(mppsolarports.NumberPort, BluetoothPort):
    pass


class StringPort(mppsolarports.StringPort, BluetoothPort):
    pass


class BluetoothMPPSolarInverter(MPPSolarInverter, ble.BLEPeripheral):
    STATUS1_HANDLE = 0x001D
    STATUS2_HANDLE = 0x0020
    PV1_STATUS_HANDLE = 0x0042

    logger = logger

    async def read_properties(self) -> None:
        data = await self.read(self.STATUS1_HANDLE)
        self.parse_status1_data(data)

        data = await self.read(self.STATUS2_HANDLE)
        self.parse_status2_data(data)

        data = await self.read(self.PV1_STATUS_HANDLE)
        self.parse_pv1_status_data(data)

    async def set_property(self, name: str, value: Property) -> None:
        pass  # TODO: implement me

    def parse_status1_data(self, data: bytes) -> None:
        (
            grid_voltage, grid_frequency, ac_output_voltage, ac_output_frequency,
            ac_output_apparent_power, ac_output_active_power, ac_output_load,
            bus_voltage, battery_voltage, battery_charging_current
        ) = struct.unpack('<HHHHHHHHHH', data)

        self._properties['grid_voltage'] = grid_voltage / 10
        self._properties['grid_frequency'] = grid_frequency / 10
        self._properties['ac_output_voltage'] = ac_output_voltage / 10
        self._properties['ac_output_frequency'] = ac_output_frequency / 10
        self._properties['ac_output_apparent_power'] = ac_output_apparent_power
        self._properties['ac_output_active_power'] = ac_output_active_power
        self._properties['ac_output_load'] = ac_output_load
        self._properties['bus_voltage'] = bus_voltage
        self._properties['battery_voltage'] = battery_voltage / 100
        self._properties['battery_charging_current'] = battery_charging_current

    def parse_status2_data(self, data: bytes) -> None:
        battery_soc, heat_sink_temp, _, _, _, _, mode, _, _, _ = struct.unpack('<HHHHHHHHHH', data)

        self._properties['battery_state_of_charge'] = battery_soc
        self._properties['heat_sink_temperature'] = heat_sink_temp
        self._properties['mode'] = chr(mode)

    def parse_pv1_status_data(self, data: bytes) -> None:
        _, _, _, _, _, pv_current, pv_voltage, pv_power, _, _ = struct.unpack('<HHHHHHHHHH', data)

        self._properties['pv_current'] = pv_current / 10
        self._properties['pv_voltage'] = pv_voltage / 10
        self._properties['pv_power'] = pv_power

    async def make_port_args(self) -> List[Dict[str, Any]]:
        return [
            {
                'driver': NumberPort,
                'property_name': 'grid_voltage',
                'display_name': 'Grid Voltage',
                'unit': 'V'
            },
            {
                'driver': NumberPort,
                'property_name': 'grid_frequency',
                'display_name': 'Grid Frequency',
                'unit': 'Hz'
            },
            {
                'driver': NumberPort,
                'property_name': 'ac_output_voltage',
                'display_name': 'AC Output Voltage',
                'unit': 'V'
            },
            {
                'driver': NumberPort,
                'property_name': 'ac_output_frequency',
                'display_name': 'AC Output Frequency',
                'unit': 'Hz'
            },
            {
                'driver': NumberPort,
                'property_name': 'ac_output_apparent_power',
                'display_name': 'AC Output Apparent Power',
                'unit': 'VA'
            },
            {
                'driver': NumberPort,
                'property_name': 'ac_output_active_power',
                'display_name': 'AC Output Active Power',
                'unit': 'W'
            },
            {
                'driver': NumberPort,
                'property_name': 'ac_output_load',
                'display_name': 'AC Output Load',
                'unit': '%'
            },
            {
                'driver': NumberPort,
                'property_name': 'battery_voltage',
                'display_name': 'Battery Voltage',
                'unit': 'V'
            },
            {
                'driver': NumberPort,
                'property_name': 'battery_charging_current',
                'display_name': 'Battery Charging Current',
                'unit': 'A'
            },
            {
                'driver': NumberPort,
                'property_name': 'battery_state_of_charge',
                'display_name': 'Battery State Of Charge',
                'unit': '%'
            },
            {
                'driver': NumberPort,
                'property_name': 'heat_sink_temperature',
                'display_name': 'Heat Sink Temperature',
                'unit': 'C'
            },
            {
                'driver': StringPort,
                'property_name': 'mode',
                'display_name': 'Inverter Mode',
                'choices': [{'value': c[0], 'display_name': c[1]} for c in constants.MODE_CHOICES]
            },
            {
                'driver': NumberPort,
                'property_name': 'pv_current',
                'display_name': 'PV Current',
                'unit': 'A'
            },
            {
                'driver': NumberPort,
                'property_name': 'pv_voltage',
                'display_name': 'PV Voltage',
                'unit': 'V'
            },
            {
                'driver': NumberPort,
                'property_name': 'pv_power',
                'display_name': 'PV Power',
                'unit': 'W'
            }
        ]
