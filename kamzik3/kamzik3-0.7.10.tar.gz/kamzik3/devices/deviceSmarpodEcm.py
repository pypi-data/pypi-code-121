""" Example of yaml configuration
Smarpod0: &Smarpod0 !Device:kamzik3.devices.deviceSmarpodEcm.DeviceSmarpodEcm
    device_id: Smarpod0
    host: 192.168.83.82
    config:
      attributes:
        !!python/tuple [Velocity, Value]: 0
        !!python/tuple [Step frequency, Value]: 12500
        !!python/tuple [Pivot X, Value]: 0
        !!python/tuple [Pivot Y, Value]: 2876e4
        !!python/tuple [Pivot Z, Value]: 2358e4
Smarpod0_axis_0: !Device:kamzik3.devices.deviceSmarpodEcm.DeviceSmarpodEcmChannel
    device: *Smarpod0
    channel: 0
    device_id: MotorAxis0
    config:
      attributes:
        !!python/tuple [Position +limit, Value]: 23.5 mm
        !!python/tuple [Position -limit, Value]: -23.5 mm
        !!python/tuple [Position, Tolerance]: [10um, 10um]
"""
import time

import numpy as np
from bidict import frozenbidict
from pint import UndefinedUnitError

import kamzik3
from kamzik3 import units, DeviceUnitError
from kamzik3.constants import *
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceSocket import DeviceSocket
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units


class DeviceSmarpodEcm(DeviceSocket):
    terminator = b"\n"
    sensor_modes = frozenbidict({"Disabled": 0, "Enabled": 1, "Power safe": 2})
    referencing_method = ["sequential", "z-safe", "x-safe", "y-safe", "xy-safe"]
    referencing_direction = ["pos", "neg", "pos-reverse", "neg-reverse"]
    pivot_mode = ["relative", "fixed"]
    push_commands_max = 1
    error_descriptions = {
        0: "ok",
        1: "other error",
        2: "controller system not initialized",
        3: "no controller systems found",
        4: "invalid parameter",
        5: "communication error",
        6: "unknown property",
        7: "resource too old",
        8: "feature unavailable",
        500: "status code unknown",
        501: "invalid smarpod id",
        502: "smarpod initialized",
        503: "hardware model unknown",
        504: "wrong communication mode",
        505: "smarpod not initialized",
        506: "invalid system id",
        507: "not enough channels",
        508: "invalid channel index",
        509: "channel used",
        510: "smarpod sensors disabled",
        511: "wrong sensor type",
        512: "system configuration",
        513: "sensor not found",
        514: "smarpod stopped",
        515: "moving",
        550: "smarpod not referenced",
        551: "pose unreachable",
        552: "command overridden",
        553: "endstop reached",
        554: "not stopped",
        555: "could not reference",
    }

    def __init__(self, host, port=2000, device_id=None, config=None):
        super().__init__(host, port, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(ATTR_SERIAL_NUMBER, readonly=True)
        self.create_attribute(
            ATTR_CHANNELS, default_value=6, readonly=True, default_type=np.uint16
        )
        self.create_attribute(ATTR_ACTIVE_UNIT, readonly=True, default_type=np.uint16)
        self.create_attribute(
            ATTR_STEP_FREQUENCY,
            default_type=np.uint32,
            min_value=1,
            max_value=20e3,
            unit="Hz",
            set_function=self.set_step_frequency,
        )
        self.create_attribute(ATTR_REFERENCED, readonly=True, default_type=np.bool)
        self.create_attribute(
            ATTR_SENSOR_MODE,
            default_type=self.sensor_modes.keys(),
            set_function=self.set_sensor_mode,
        )
        self.create_attribute(
            ATTR_REFERENCING_METHOD,
            default_type=self.referencing_method,
            set_function=self.set_referencing_method,
        )
        self.create_attribute(
            ATTR_REFERENCING_DIRECTION_X,
            default_type=self.referencing_direction,
            set_function=self.set_referencing_direction_x,
        )
        self.create_attribute(
            ATTR_REFERENCING_DIRECTION_Y,
            default_type=self.referencing_direction,
            set_function=self.set_referencing_direction_y,
        )
        self.create_attribute(
            ATTR_REFERENCING_DIRECTION_Z,
            default_type=self.referencing_direction,
            set_function=self.set_referencing_direction_z,
        )
        self.create_attribute(
            ATTR_PIVOT_MODE,
            default_type=self.pivot_mode,
            set_function=self.set_pivot_mode,
        )
        self.create_attribute(
            ATTR_VELOCITY,
            default_type=np.float64,
            unit="m/s",
            set_function=self.set_velocity,
            decimals=9,
        )
        self.create_attribute(
            ATTR_PIVOT_X,
            default_type=np.int64,
            unit="nm",
            set_function=self.set_pivot_x,
        )
        self.create_attribute(
            ATTR_PIVOT_Y,
            default_type=np.int64,
            unit="nm",
            set_function=self.set_pivot_y,
        )
        self.create_attribute(
            ATTR_PIVOT_Z,
            default_type=np.int64,
            unit="nm",
            set_function=self.set_pivot_z,
        )
        self.create_attribute(ATTR_POSITIONS, readonly=True)
        self.create_attribute(ATTR_CALIBRATING, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_REFERENCING, readonly=True, default_type=np.bool)

    def valid_command_format(self, command):
        return command is not None and command.endswith("\r\n")

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.start_polling()
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.command("%set lineend-format 1\r\n")
        self.command("%set number-format 1\r\n")
        self.command("%unit?\r\n")
        self.command("sen?\r\n")
        self.command("ref?\r\n")
        self.command("piv?\r\n")
        self.command("frq?\r\n")
        self.command("vel?\r\n")
        self.command("get fref-method\r\n")
        self.command("get fref-x-direction\r\n")
        self.command("get fref-y-direction\r\n")
        self.command("get fref-z-direction\r\n")
        self.command("get pivot-mode\r\n", callback=_finish_configuration)

    def found_terminator(self):
        if len(self.buffer) == 0:
            return
        elif self.buffer[-1][-1] == ":":
            self.buffer[-1] += self.terminator.decode()
        else:
            super().found_terminator()

    def handle_readout(self, readout_buffer):
        command, output, callback, token = super().handle_readout(readout_buffer)
        if output[0] == "!":
            error_code = int(output[1:])
            if error_code != 0:
                readout_buffer = "Error code: {}.\nError description: {}".format(
                    error_code, self.error_descriptions.get(error_code, "Unknown error")
                )
                self.handle_command_error(command, readout_buffer)
                command = RESPONSE_ERROR
        elif command == "mst?\r\n":
            if int(output) <= 1:
                # Motor is stopped or holding
                motor_status = STATUS_IDLE
            else:
                # Motor is moving
                motor_status = STATUS_BUSY
            self.set_status(motor_status)
            for channel in range(self.get_value(ATTR_CHANNELS)):
                self.notify((channel, ATTR_STATUS), motor_status)
        elif command == "%unit?\r\n":
            self.set_raw_value(ATTR_ACTIVE_UNIT, int(output))
        elif command == "sen?\r\n":
            self.set_raw_value(ATTR_SENSOR_MODE, self.sensor_modes.inv[int(output)])
        elif command == "piv?\r\n":
            pivot_x, pivot_y, pivot_z = output.split(" ")
            pivot_x = device_units(
                self, ATTR_PIVOT_X, units.Quantity(float(pivot_x), "m")
            ).m
            pivot_y = device_units(
                self, ATTR_PIVOT_Y, units.Quantity(float(pivot_y), "m")
            ).m
            pivot_z = device_units(
                self, ATTR_PIVOT_Z, units.Quantity(float(pivot_z), "m")
            ).m
            self.set_raw_value(ATTR_PIVOT_X, pivot_x)
            self.set_raw_value(ATTR_PIVOT_Y, pivot_y)
            self.set_raw_value(ATTR_PIVOT_Z, pivot_z)
        elif command == "pos?\r\n":
            self.set_raw_value(ATTR_POSITIONS, output)
            for channel, position in enumerate(map(float, output.split(" "))):
                self.notify((channel, ATTR_POSITION), position)
        elif command == "ref?\r\n":
            self.set_raw_value(ATTR_REFERENCED, bool(int(output)))
        elif command == "vel?\r\n":
            self.set_raw_value(ATTR_VELOCITY, float(output))
        elif command == "get fref-method\r\n":
            self.set_raw_value(ATTR_REFERENCING_METHOD, output)
        elif command == "get fref-x-direction\r\n":
            self.set_raw_value(ATTR_REFERENCING_DIRECTION_X, output)
        elif command == "get fref-y-direction\r\n":
            self.set_raw_value(ATTR_REFERENCING_DIRECTION_Y, output)
        elif command == "get fref-z-direction\r\n":
            self.set_raw_value(ATTR_REFERENCING_DIRECTION_Z, output)
        elif command == "get pivot-mode\r\n":
            self.set_raw_value(ATTR_PIVOT_MODE, output)
        elif command == "frq?\r\n":
            self.set_raw_value(ATTR_STEP_FREQUENCY, int(float(output)))

        if callback is not None:
            self.handle_readout_callback(callback, command, readout_buffer)
        if token:
            kamzik3.session.publisher.push_message(
                self.device_id, [command, readout_buffer], token
            )
            for observer in self._observers[:]:
                if isinstance(observer, DeviceSmarpodEcmChannel):
                    kamzik3.session.publisher.push_message(
                        observer.device_id, [command, readout_buffer], token
                    )

    def start_polling(self):
        super().start_polling()
        self.poll_command("mst?\r\n", 300)
        if self.get_value(ATTR_REFERENCED):
            self.poll_command("pos?\r\n", 300)

    def set_sensor_mode(self, mode, callback=None):
        self.logger.info("Set sensor mode to {}".format(mode))
        return self.command(
            "sen {}\r\n".format(self.sensor_modes[mode]), callback, with_token=True
        )

    def set_referencing_method(self, method, callback=None):
        self.logger.info("Set referencing method to {}".format(method))
        return self.command(
            "set fref-method {}\r\n".format(method), callback, with_token=True
        )

    def set_referencing_direction_x(self, direction, callback=None):
        self.logger.info("Set x referencing direction to {}".format(direction))
        return self.command(
            "set fref-x-direction {}\r\n".format(direction), callback, with_token=True
        )

    def set_referencing_direction_y(self, direction, callback=None):
        self.logger.info("Set y referencing direction to {}".format(direction))
        return self.command(
            "set fref-y-direction {}\r\n".format(direction), callback, with_token=True
        )

    def set_referencing_direction_z(self, direction, callback=None):
        self.logger.info("Set z referencing direction to {}".format(direction))
        return self.command(
            "set fref-z-direction {}\r\n".format(direction), callback, with_token=True
        )

    def set_pivot_mode(self, mode, callback=None):
        self.logger.info("Set pivot mode {}".format(mode))
        return self.command(
            "set pivot-mode {}\r\n".format(mode), callback, with_token=True
        )

    def set_step_frequency(self, value, callback=None):
        self.logger.info("Set step frequency to {} Hz".format(value))
        return self.command("frq {}\r\n".format(int(value)), callback, with_token=True)

    def set_velocity(self, value, callback=None):
        self.logger.info("Set velocity to {}".format(value))
        return self.command(
            "vel {}\r\n".format(float(value)), callback, with_token=True
        )

    def set_pivot_x(self, value, callback=None):
        self.logger.info("Set pivot pivot point x to {} nm".format(value))
        pivot_x = device_units(self, ATTR_PIVOT_X, value).to("m")
        pivot_y = device_units(self, ATTR_PIVOT_Y, self.get_value(ATTR_PIVOT_Y)).to("m")
        pivot_z = device_units(self, ATTR_PIVOT_Z, self.get_value(ATTR_PIVOT_Z)).to("m")
        return self.command(
            "piv {} {} {}\r\n".format(pivot_x.m, pivot_y.m, pivot_z.m),
            callback,
            with_token=True,
        )

    def set_pivot_y(self, value, callback=None):
        self.logger.info("Set pivot pivot point y to {} nm".format(value))
        pivot_x = device_units(self, ATTR_PIVOT_X, self.get_value(ATTR_PIVOT_X)).to("m")
        pivot_y = device_units(self, ATTR_PIVOT_Y, value).to("m")
        pivot_z = device_units(self, ATTR_PIVOT_Z, self.get_value(ATTR_PIVOT_Z)).to("m")
        return self.command(
            "piv {} {} {}\r\n".format(pivot_x.m, pivot_y.m, pivot_z.m),
            callback,
            with_token=True,
        )

    def set_pivot_z(self, value, callback=None):
        self.logger.info("Set pivot pivot point z to {} nm".format(value))
        pivot_x = device_units(self, ATTR_PIVOT_X, self.get_value(ATTR_PIVOT_X)).to("m")
        pivot_y = device_units(self, ATTR_PIVOT_Y, self.get_value(ATTR_PIVOT_Y)).to("m")
        pivot_z = device_units(self, ATTR_PIVOT_Z, value).to("m")
        return self.command(
            "piv {} {} {}\r\n".format(pivot_x.m, pivot_y.m, pivot_z.m),
            callback,
            with_token=True,
        )

    @expose_method()
    def stop(self, callback=None):
        self.logger.info("Stop movement")
        return self.command("stop\r\n", callback, with_token=True)

    @expose_method()
    def calibrate(self, callback=None):
        self.logger.info("Calibrate")
        self.stop_polling()

        # FIXME: Can't we just delete the arguments?
        # Check back after the "callback" argument to self.command(...) has a type
        def start_calibration(key, value):
            self.set_value(ATTR_CALIBRATING, True)
            self.set_value(ATTR_STATUS, STATUS_BUSY)
            for channel in range(self.get_value(ATTR_CHANNELS)):
                self.notify((channel, ATTR_STATUS), STATUS_BUSY)
                self.notify((channel, ATTR_CALIBRATING), True)

        self.command("mst?\r\n", callback=start_calibration)

        # FIXME: Can't we just delete the arguments?
        # Check back after the "callback" argument to self.command(...) has a type
        def stop_calibration(key, value, callback=callback):
            self.set_value(ATTR_CALIBRATING, False)
            for channel in range(self.get_value(ATTR_CHANNELS)):
                self.notify((channel, ATTR_CALIBRATING), False)

            if callback is not None:
                callback()
            self.command(
                "ref?\r\n", callback=lambda *args, **kwargs: self.start_polling()
            )

        return self.command("cal\r\n", callback=stop_calibration, with_token=True)

    @expose_method()
    def reference(self, callback=None):
        self.logger.info("Reference")
        self.stop_polling()

        # FIXME: Can't we just delete the arguments?
        # Check back after the "callback" argument to self.command(...) has a type
        def start_referencing(key, value):
            self.set_value(ATTR_REFERENCING, True)
            self.set_value(ATTR_REFERENCED, False)
            self.set_value(ATTR_STATUS, STATUS_BUSY)
            for channel in range(self.get_value(ATTR_CHANNELS)):
                self.notify((channel, ATTR_STATUS), STATUS_BUSY)
                self.notify((channel, ATTR_CALIBRATING), True)

        self.command("mst?\r\n", callback=start_referencing)

        # FIXME: Can't we just delete the arguments?
        # Check back after the "callback" argument to self.command(...) has a type
        def stop_referencing(key, value, callback=callback):
            self.set_value(ATTR_REFERENCING, False)
            for channel in range(self.get_value(ATTR_CHANNELS)):
                self.notify((channel, ATTR_CALIBRATING), False)

            if callback is not None:
                callback()
            self.command(
                "ref?\r\n", callback=lambda *args, **kwargs: self.start_polling()
            )

        return self.command("ref\r\n", callback=stop_referencing, with_token=True)

    def move_channel(self, channel, position, callback=None):
        positions = list(self.get_value(ATTR_POSITIONS).split(" "))
        positions[channel] = str(position)
        token = self.command(
            "mov {}\r\n".format(" ".join(positions)), callback, with_token=True
        )
        self.command("mst?\r\n")
        return token


class DeviceSmarpodEcmChannel(DeviceChannel):
    def __init__(self, device, channel, device_id=None, config=None):
        self.default_unit = "nm"
        self.base_unit = "m"
        super().__init__(device, channel, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        if self.channel > 2:
            self.default_unit = "ndeg"
            self.base_unit = "deg"

        self.create_attribute(
            ATTR_POSITION,
            default_type=np.float64,
            decimals=9,
            set_function=self._move_absolute,
            set_value_when_set_function=False,
            unit=self.default_unit,
        )
        self.create_attribute(
            ATTR_POSITION_UPPER_LIMIT,
            default_type=np.float64,
            decimals=9,
            set_function=self.set_position_upper_limit,
            unit=self.default_unit,
        )
        self.create_attribute(
            ATTR_POSITION_LOWER_LIMIT,
            default_type=np.float64,
            decimals=9,
            set_function=self.set_position_lower_limit,
            unit=self.default_unit,
        )
        self.create_attribute(ATTR_CALIBRATING, readonly=True, default_type=np.bool)
        self.create_attribute(ATTR_REFERENCING, readonly=True, default_type=np.bool)

    def handle_configuration(self):
        if self.configured:
            return
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.configured = True
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        _finish_configuration()

    def subject_update(self, key, value, subject):
        super().subject_update(key, value, subject)

        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            attribute = key[1]

            if attribute == ATTR_POSITION:
                value = device_units(
                    self, ATTR_POSITION, units.Quantity(float(value), self.base_unit)
                ).m

            self.set_raw_value(ATTR_LATENCY, self.device.get_value(ATTR_LATENCY))
            self.set_raw_value(attribute, value)

    def _move_absolute(self, position, callback=None):
        position = device_units(self, ATTR_POSITION, position).to(self.base_unit)
        self.logger.info("Move to absolute position {:~}".format(position))  # type: ignore
        # ~ is a pint format specification
        return self.device.move_channel(self.channel, position.m, callback)

    @expose_method({"position": ATTR_POSITION})
    def move_relative(self, position, callback=None):
        try:
            position = device_units(self, ATTR_POSITION, position)
            current_position = self[ATTR_POSITION].value()
            return self.set_value(ATTR_POSITION, current_position + position, callback)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position, callback=None):
        try:
            position = device_units(self, ATTR_POSITION, position)
            return self.set_value(ATTR_POSITION, position.m, callback)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method()
    def stop(self, callback=None):
        self.logger.info("Stop movement")
        return self.device.stop(callback)

    def set_position_upper_limit(self, position, callback=None):
        self.logger.info("Set upper position limit to {}".format(position))
        position = self[ATTR_POSITION].remove_offset_factor(position)
        return self.set_attribute((ATTR_POSITION, MAX), position, callback=callback)

    def set_position_lower_limit(self, position, callback=None):
        self.logger.info("Set lower position limit to {}".format(position))
        position = self[ATTR_POSITION].remove_offset_factor(position)
        return self.set_attribute((ATTR_POSITION, MIN), position, callback=callback)
