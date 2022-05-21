
import asyncio
import contextlib
import logging
import math
import re

from typing import Any, Dict, List, Optional, Set, Type

from qtoggleserver.utils import json as json_utils

from . import commands, constants
from .io import BaseIO, HIDRawIO, SerialIO
from .inverter import MPPSolarInverter
from .ports import BooleanPort, NumberPort, StringPort
from .typing import Properties, Property


logger = logging.getLogger(__name__)


class SerialMPPSolarInverter(MPPSolarInverter):
    DEFAULT_BAUD = 2400
    CMD_WAIT = 0.5  # seconds
    BATTERY_FORCE_WAIT = 5  # seconds

    # Filter out properties that we don't really want exposed
    BLACKLISTED_PROPERTIES = {
        'has_sbu_priority',
        'is_configuration_status_changed',
        'is_scc_firmware_updated',
        'is_battery_voltage_too_steady_while_charging',
        'is_battery_charging',  # is_battery_charging* properties appear to be broken
        'is_battery_charging_from_scc',
        'is_battery_charging_from_grid',
        'is_battery_float_charging',
        'is_battery_low',
        'is_battery_present',
        'is_grid_present',
        'is_scc_active',
        'battery_voltage_offset_fans',
        'eeprom_version',
        'is_dustproof_installed',
        'is_turned_on',
        'is_scc_firmware_updated',
    }

    logger = logger

    def __init__(
        self,
        *,
        serial_port: str,
        serial_baud: int = DEFAULT_BAUD,
        blacklist_properties: Optional[List[str]] = None,
        force_battery_discharge_min_soc: Optional[int] = None,
        force_battery_charge_grid_min_voltage: Optional[int] = None,
        **kwargs
    ) -> None:

        self._serial_port: str = serial_port
        self._serial_baud: int = serial_baud
        self._blacklist_properties: Set[str] = set(blacklist_properties or [])
        self._force_battery_discharge_min_soc: Optional[int] = force_battery_discharge_min_soc
        self._force_battery_charge_min_grid_voltage: Optional[int] = force_battery_charge_grid_min_voltage
        self._setter_command_classes_by_property: Dict[str, List[Type[commands.Command]]] = {}
        self._choices_by_property: Dict[str, List[Dict[str, Any]]] = {}
        self._command_lock: asyncio.Lock = asyncio.Lock()

        super().__init__(**kwargs)

        for cls in commands.get_command_classes(self._model):
            for name in cls.get_request_property_definitions():
                self._setter_command_classes_by_property.setdefault(name, []).append(cls)

    def make_io(self) -> BaseIO:
        if re.match(r'.*hidraw\d+', self._serial_port):
            return HIDRawIO(self._serial_port)
        else:
            return SerialIO(self._serial_port, self._serial_baud)

    async def run_command(self, io: BaseIO, cls: Type[commands.Command], **params) -> Properties:
        params = dict(params, **self.prepare_command_params(cls))
        if params:
            params_str = ', '.join(f'{k}={json_utils.dumps(v)}' for k, v in params.items())
            self.debug('running command %s(%s)', cls.get_name(), params_str)
        else:
            self.debug('running command %s', cls.get_name())

        cmd = cls(**params)
        # Don't run empty commands
        if not cmd.REQUEST_FMT:
            return {}

        request = cmd.prepare_request()
        async with self._command_lock:
            self.debug('sending "%s"', repr(request)[2:-1])
            io.write(request)
            response = await io.read(self.TIMEOUT)
            await asyncio.sleep(self.CMD_WAIT)
            self.debug('received "%s"', repr(response)[2:-1])

        parsed_response = cmd.parse_response(response)

        return parsed_response

    def prepare_command_params(self, cmd: Type[commands.Command]) -> Properties:
        return cmd.REQUEST_DEFAULT_VALUES

    async def read_properties(self) -> None:
        with contextlib.closing(self.make_io()) as io:
            for cls in commands.get_command_classes(self._model):
                if cls.has_response_properties():
                    try:
                        self._properties.update(await self.run_command(io, cls))
                    except Exception as e:
                        self.error('command %s failed: %s', cls.get_name(), e)
                        continue

    async def set_property(self, name: str, value: Property) -> None:
        cmd_classes = self._setter_command_classes_by_property[name]
        params = {name: value}
        old_value = self._properties.get(name)

        if old_value == value:
            return

        self.debug('setting property "%s" from %s to %s', name, json_utils.dumps(old_value), json_utils.dumps(value))

        with contextlib.closing(self.make_io()) as io:
            for cls in cmd_classes:
                await self.run_command(io, cls, **params)

            await self._handle_post_set_property(io, name, old_value, value)

    async def _handle_post_set_property(
        self,
        io: BaseIO, name: str,
        old_value: Optional[Property],
        new_value: Property
    ) -> None:
        # When changing output source priority, the user normally expects the inverter to switch to battery
        # charging/discharging mode right away, depending on the new setting. The inverter doesn't do this automatically
        # as it attempts to preserve the current charging/discharging battery phase, so we need to force it by
        # temporarily adjusting back-to-(dis)charging battery parameters.
        if name == 'output_source_priority':
            mode = self._properties.get('mode')
            soc = self._properties.get('battery_state_of_charge', 0)
            grid_voltage = self._properties.get('grid_voltage', 0)
            if (
                new_value == constants.OUTPUT_SOURCE_PRIORITY_SBG and
                mode == constants.MODE_GRID and
                self._force_battery_discharge_min_soc is not None and
                soc >= self._force_battery_discharge_min_soc
            ):
                self.info('forcing battery discharge')
                await self._force_battery_discharge(io)
            elif (
                old_value == constants.OUTPUT_SOURCE_PRIORITY_SBG and
                mode == constants.MODE_BATTERY and
                self._force_battery_charge_min_grid_voltage is not None and
                grid_voltage > self._force_battery_charge_min_grid_voltage
            ):
                self.info('forcing battery charge')
                await self._force_battery_charge(io)

    async def _force_battery_discharge(self, io: BaseIO) -> None:
        cmd_classes = self._setter_command_classes_by_property.get('battery_back_to_discharging_voltage', [])
        if not cmd_classes:
            self.warning('cannot force battery mode: command not available')
            return
        cls = cmd_classes[0]

        battery_voltage = self._properties.get('battery_voltage')
        if battery_voltage is None:
            self.warning('cannot force battery mode: battery voltage not available')
            return

        battery_back_to_discharging_voltage = self._properties.get('battery_back_to_discharging_voltage')
        if battery_back_to_discharging_voltage is None:
            self.warning('cannot force battery mode: battery back-to-discharging voltage not available')
            return

        temp_value = int(battery_voltage)
        if temp_value == battery_voltage:
            temp_value -= 1

        if temp_value >= battery_back_to_discharging_voltage:
            self.debug('adjusting battery back-to-discharging voltage not needed')
            return

        try:
            await self.run_command(io, cls, battery_back_to_discharging_voltage=temp_value)
            await asyncio.sleep(self.BATTERY_FORCE_WAIT)
        finally:
            await self.run_command(io, cls, battery_back_to_discharging_voltage=battery_back_to_discharging_voltage)

    async def _force_battery_charge(self, io: BaseIO) -> None:
        cmd_classes = self._setter_command_classes_by_property.get('battery_back_to_charging_voltage', [])
        if not cmd_classes:
            self.warning('cannot force battery mode: command not available')
            return
        cls = cmd_classes[0]

        battery_voltage = self._properties.get('battery_voltage')
        if battery_voltage is None:
            self.warning('cannot force battery mode: battery voltage not available')
            return

        battery_back_to_charging_voltage = self._properties.get('battery_back_to_charging_voltage')
        if battery_back_to_charging_voltage is None:
            self.warning('cannot force battery mode: battery back-to-charging voltage not available')
            return

        temp_value = int(math.ceil(battery_voltage))
        if temp_value == battery_voltage:
            temp_value += 1

        if temp_value <= battery_back_to_charging_voltage:
            self.debug('adjusting battery back-to-charging voltage not needed')
            return

        try:
            await self.run_command(io, cls, battery_back_to_charging_voltage=temp_value)
            await asyncio.sleep(self.BATTERY_FORCE_WAIT)
        finally:
            await self.run_command(io, cls, battery_back_to_charging_voltage=battery_back_to_charging_voltage)

    async def make_port_args(self) -> List[Dict[str, Any]]:
        # All available command classes for this inverter model
        cmd_classes = commands.get_command_classes(self._model)

        # Fetch property choices
        with contextlib.closing(self.make_io()) as io:
            for cls in cmd_classes:
                response_property_definitions = cls.get_response_property_definitions()
                for name, details in response_property_definitions.items():
                    if not details['is_choices']:
                        continue

                    response = await self.run_command(io, cls)
                    self._choices_by_property[name] = [
                        {
                            'value': c,
                            'label': str(c)
                        }
                        for c in response[name]
                    ]

        # Create port args
        blacklisted_properties = self.BLACKLISTED_PROPERTIES | self._blacklist_properties
        port_args_list = []
        for cls in cmd_classes:
            response_property_definitions = cls.get_response_property_definitions()
            for name, details in response_property_definitions.items():
                if (name in blacklisted_properties) or details['is_choices']:
                    continue

                type_ = details['type']
                port_args = {
                    'property_name': name,
                    'display_name': details['display_name'],
                    'writable': name in self._setter_command_classes_by_property
                }
                if type_ == 'bool':
                    port_args['driver'] = BooleanPort
                elif type_ in ('int', 'float'):
                    port_args['driver'] = NumberPort
                elif type_ == 'str':
                    port_args['driver'] = StringPort
                else:
                    continue

                if type_ in ('int', 'str'):
                    port_args.update({
                        'unit': details['unit'],
                        'choices': details['choices'] or self._choices_by_property.get(name),
                    })

                port_args_list.append(port_args)

        return port_args_list
