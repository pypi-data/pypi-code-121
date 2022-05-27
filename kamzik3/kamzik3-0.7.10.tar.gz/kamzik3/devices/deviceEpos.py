import time
from _ctypes import byref
from ctypes import (
    Array,
    create_string_buffer,
    c_uint32,
    CDLL,
    c_uint16,
    c_int,
    c_int8,
    c_uint8,
    c_int64,
)
from typing import Optional

import bidict
import numpy as np
from pint import UndefinedUnitError

from kamzik3.snippets.snippetsUnits import device_units

from kamzik3 import DeviceError, DeviceUnitError
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.deviceOsLibrary import DeviceOsLibrary
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsTimer import PreciseCallbackTimer

MODE_PROFILE_POSITION = 1
MODE_PROFILE_VELOCITY = 3
MODE_HOMING = 6
MODE_POSITION = 8
MODE_VELOCITY = 9
MODE_CURRENT = 10

GROUP_VELOCITY_PROFILE = "Velocity profile"
GROUP_POSITION_PROFILE = "Position profile"

_DEVICE_DISCONNECTED = 268435459


class DeviceEpos(Device):
    def __init__(
        self,
        library,
        device_name,
        protocol,
        interface,
        port,
        device_id=None,
        config=None,
    ):
        self.device_name = (
            create_string_buffer(device_name.encode())
            if not isinstance(device_name, Array)
            else device_name
        )
        self.protocol = (
            create_string_buffer(protocol.encode())
            if not isinstance(protocol, Array)
            else protocol
        )
        self.interface = (
            create_string_buffer(interface.encode())
            if not isinstance(interface, Array)
            else interface
        )
        self.port = (
            create_string_buffer(port.encode()) if not isinstance(port, Array) else port
        )
        self.handle = 0
        self.pError = c_uint32()

        if not hasattr(self, "os_library"):
            self.os_library = library
        if not hasattr(self, "library"):
            self.library = None
        super().__init__(device_id, config)
        self.connect()

    def _init_attributes(self):
        Device._init_attributes(self)
        self.create_attribute(
            ATTR_LIBRARY, default_value=self.os_library, readonly=True
        )

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.start_polling()
            self.set_status(STATUS_IDLE)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        _finish_configuration()

    def connect(self, *args):
        """
        Call only this function to connect devices to port / socket / library / ...

        :param args: connect attributes
        """
        self.connecting = True
        try:
            self.library = CDLL(self.os_library)
            self.handle = self.check_error(
                self.library.VCS_OpenDevice(
                    byref(self.device_name),
                    byref(self.protocol),
                    byref(self.interface),
                    byref(self.port),
                    byref(self.pError),
                )
            )
        except OSError as e:
            raise DeviceError("Error loading library {}. {}".format(self.os_library, e))

        self.handle_configuration_event()
        self.connected = True
        self.connecting = False
        self.set_status(STATUS_IDLE)

    def check_error(self, error_code, raise_exception=True):
        """
        Check error response for executed command.

        :param error_code: error code response
        :param raise_exception: raise exception if True
        :return:
        """
        if error_code == 0:
            error_message, error_code = self.get_error()
            if raise_exception:
                if error_code != 0 and error_code != _DEVICE_DISCONNECTED:
                    raise DeviceError("Error: %s" % error_message)
        return error_code

    def get_error(self, pError=None):
        """
        Get error description of given code.

        :param pError: error code
        :return:
        """
        if pError is None:
            pError = self.pError
        pErrorInfo = create_string_buffer(255)
        if self.library.VCS_GetErrorInfo(pError, byref(pErrorInfo), 255) != 0:
            return "Code: %s, %s" % (pError.value, pErrorInfo.value), pError.value
        else:
            return "Code: %s, %s" % (pError.value, "Unknown error"), pError.value

    def disconnect(self):
        self.library.VCS_CloseDevice(self.handle, byref(self.pError))
        return super().disconnect()


class DeviceEposLinux(DeviceEpos):
    def __init__(
        self, device_name, protocol, interface, port, device_id=None, config=None
    ):
        DeviceEpos.__init__(
            self,
            "libEposCmd.so",
            device_name,
            protocol,
            interface,
            port,
            device_id,
            config,
        )


class DeviceEposChannel(DeviceChannel):
    polling = False
    operation_modes = bidict.frozenbidict(
        {
            MODE_PROFILE_POSITION: "Profile position",
            MODE_PROFILE_VELOCITY: "Profile velocity",
            MODE_HOMING: "Homing",
            MODE_POSITION: "Position",
            MODE_VELOCITY: "Velocity",
            MODE_CURRENT: "Current",
        }
    )
    velocity_units = bidict.frozenbidict(
        {
            "Standard": 0,
            "Deci": -1,
            "Centi": -2,
            "Milli": -3,
        }
    )

    def __init__(self, device, channel, device_id=None, config=None) -> None:
        super().__init__(device, channel, device_id, config)
        self.polling_timer: Optional[PreciseCallbackTimer] = None

    def _init_attributes(self):
        DeviceChannel._init_attributes(self)

        self.create_attribute(
            ATTR_HARDWARE_VERSION,
            default_value=None,
            readonly=True,
            default_type=np.uint16,
        )
        self.create_attribute(
            ATTR_SOFTWARE_VERSION,
            default_value=None,
            readonly=True,
            default_type=np.uint16,
        )
        self.create_attribute(
            ATTR_APPLICATION_NUMBER,
            default_value=None,
            readonly=True,
            default_type=np.uint16,
        )
        self.create_attribute(
            ATTR_APPLICATION_VERSION,
            default_value=None,
            readonly=True,
            default_type=np.uint32,
        )
        self.create_attribute(
            ATTR_AUTO_STOP, default_value=True, readonly=False, default_type=bool
        )
        self.create_attribute(
            ATTR_ON_TARGET, default_value=True, readonly=True, default_type=bool
        )
        self.create_attribute(ATTR_REVOLUTIONS, readonly=True, default_type=np.int64)
        self.create_attribute(
            ATTR_OPERATION_MODE,
            default_value=None,
            readonly=True,
            default_type=self.operation_modes.inverse.keys(),
            set_function=self.set_operation_mode,
        )
        self.create_attribute(
            ATTR_MOTOR_EXCITATION,
            default_value=False,
            default_type=bool,
            set_function=self.set_motor_enabled,
        )
        self.create_attribute(
            ATTR_VELOCITY_UNITS,
            default_value=None,
            readonly=True,
            default_type=self.velocity_units.keys(),
            set_function=self.set_velocity_units,
        )
        self.create_attribute(
            ATTR_VELOCITY,
            default_value=None,
            readonly=False,
            unit="rpm",
            default_type=float,
            set_function=self.set_velocity,
        )
        self.create_attribute(
            ATTR_ABSOLUTE_POSITION,
            default_value=None,
            readonly=False,
            unit="deg",
            default_type=float,
            set_function=self.set_absolute_position,
        )
        self.create_attribute(
            ATTR_POSITION,
            default_value=None,
            readonly=False,
            unit="deg",
            default_type=float,
            set_function=self.set_position,
        )
        self.create_attribute(
            ATTR_ACCELERATION,
            default_value=None,
            readonly=False,
            group=GROUP_VELOCITY_PROFILE,
            default_type=float,
            set_function=lambda v: self.set_velocity_profile(acceleration=v),
        )
        self.create_attribute(
            ATTR_DECELERATION,
            default_value=None,
            readonly=False,
            group=GROUP_VELOCITY_PROFILE,
            default_type=float,
            set_function=lambda v: self.set_velocity_profile(deceleration=v),
        )
        self.create_attribute(
            ATTR_ACCELERATION,
            default_value=None,
            readonly=False,
            group=GROUP_POSITION_PROFILE,
            default_type=float,
            set_function=lambda v: self.set_position_profile(acceleration=v),
        )
        self.create_attribute(
            ATTR_DECELERATION,
            default_value=None,
            readonly=False,
            group=GROUP_POSITION_PROFILE,
            default_type=float,
            set_function=lambda v: self.set_position_profile(deceleration=v),
        )
        self.create_attribute(
            ATTR_VELOCITY,
            default_value=None,
            readonly=False,
            group=GROUP_POSITION_PROFILE,
            default_type=float,
            unit="rpm",
            decimals=4,
            set_function=lambda v: self.set_position_profile(velocity=v),
        )

    def handle_configuration(self):
        if self.configured:
            return

        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.configured = True
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.get_device_firmware_version()
        self.get_operation_mode()
        self.get_enabled_state()
        self.get_velocity_units()
        self.get_velocity_profile()
        self.get_position_profile()
        _finish_configuration()

    def get_device_firmware_version(self):
        """
        Get the device firmware version.

        VCS_GetVersion(
        HANDLE KeyHandle,
        WORD NodeId,
        WORD * pHardwareVersion,
        WORD * pSoftwareVersion,
        WORD * pApplicationNumber,
        WORD * pApplicationVersion,
        DWORD * pErrorCode
        )
        """
        hw_version = c_uint16()
        sw_version = c_uint16()
        app_number = c_uint16()
        app_version = c_uint32()
        error_code = self.device.check_error(
            self.device.library.VCS_GetVersion(
                self.device.handle,
                self.channel,
                byref(hw_version),
                byref(sw_version),
                byref(app_number),
                byref(app_version),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return (
                self.get_attribute(ATTR_HARDWARE_VERSION)[VALUE],
                self.get_attribute(ATTR_SOFTWARE_VERSION)[VALUE],
                self.get_attribute(ATTR_APPLICATION_NUMBER)[VALUE],
                self.get_attribute(ATTR_APPLICATION_VERSION)[VALUE],
            )

        self.set_value(ATTR_HARDWARE_VERSION, hw_version.value)
        self.set_value(ATTR_SOFTWARE_VERSION, sw_version.value)
        self.set_value(ATTR_APPLICATION_NUMBER, app_number.value)
        self.set_value(ATTR_APPLICATION_VERSION, app_version.value)

    def get_movement_state(self):
        state = c_int()
        error_code = self.device.check_error(
            self.device.library.VCS_GetMovementState(
                self.device.handle,
                self.channel,
                byref(state),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return self.get_attribute(ATTR_ON_TARGET)[VALUE]

        self.set_value(ATTR_ON_TARGET, bool(state.value))
        return state.value

    def get_state(self):
        state = c_uint32()
        error_code = self.device.check_error(
            self.device.library.VCS_GetState(
                self.device.handle,
                self.channel,
                byref(state),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            self.set_status(STATUS_DISCONNECTED)
            return state.value

        self.set_status(STATUS_BUSY if state.value else STATUS_IDLE)
        return state.value

    def get_enabled_state(self):
        state = c_int8()
        error_code = self.device.check_error(
            self.device.library.VCS_GetEnableState(
                self.device.handle,
                self.channel,
                byref(state),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return self.get_attribute(ATTR_MOTOR_EXCITATION)[VALUE]

        self.set_offsetted_value(ATTR_MOTOR_EXCITATION, state.value)
        return state.value

    def get_operation_mode(self):
        operation_mode = c_uint32()
        error_code = self.device.check_error(
            self.device.library.VCS_GetOperationMode(
                self.device.handle,
                self.channel,
                byref(operation_mode),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return self.get_attribute(ATTR_OPERATION_MODE)[VALUE]

        self.set_offsetted_value(
            ATTR_OPERATION_MODE, self.operation_modes.get(operation_mode.value, None)
        )
        return operation_mode.value

    def get_velocity_units(self):
        dimension = c_uint8()
        notation = c_int8()
        error_code = self.device.check_error(
            self.device.library.VCS_GetVelocityUnits(
                self.device.handle,
                self.channel,
                byref(dimension),
                byref(notation),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return self.get_attribute(ATTR_VELOCITY_UNITS)[VALUE]

        self.set_offsetted_value(
            ATTR_VELOCITY_UNITS, self.velocity_units.inverse.get(notation.value)
        )
        return self.velocity_units.inverse.get(notation.value)

    def get_velocity(self):
        velocity = c_int64()
        error_code = self.device.check_error(
            self.device.library.VCS_GetVelocityIsAveraged(
                self.device.handle,
                self.channel,
                byref(velocity),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return self.get_attribute(ATTR_VELOCITY)[VALUE]

        self.set_offsetted_value(ATTR_VELOCITY, velocity.value)
        return velocity.value

    def get_velocity_profile(self):
        acceleration = c_int()
        deceleration = c_int()
        error_code = self.device.check_error(
            self.device.library.VCS_GetVelocityProfile(
                self.device.handle,
                self.channel,
                byref(acceleration),
                byref(deceleration),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return (
                self.get_attribute(ATTR_ACCELERATION)[VALUE],
                self.get_attribute(ATTR_DECELERATION)[VALUE],
            )

        self.set_offsetted_value(
            [GROUP_VELOCITY_PROFILE, ATTR_ACCELERATION], acceleration.value
        )
        self.set_offsetted_value(
            [GROUP_VELOCITY_PROFILE, ATTR_DECELERATION], deceleration.value
        )
        return acceleration.value, deceleration.value

    def get_position(self):
        position = c_int64()
        error_code = self.device.check_error(
            self.device.library.VCS_GetPositionIs(
                self.device.handle,
                self.channel,
                byref(position),
                byref(self.device.pError),
            )
        )
        attribute = self.get_attribute(ATTR_ABSOLUTE_POSITION)

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return attribute[VALUE]

        self.set_offsetted_value(ATTR_ABSOLUTE_POSITION, position.value)
        self.set_offsetted_value(
            ATTR_POSITION, attribute.apply_offset_factor(position.value) % 360
        )
        self.set_offsetted_value(
            ATTR_REVOLUTIONS,
            int(attribute.apply_offset_factor(position.value) / 360),
        )
        return position.value

    def get_position_profile(self):
        velocity = c_int()
        acceleration = c_int()
        deceleration = c_int()
        error_code = self.device.check_error(
            self.device.library.VCS_GetPositionProfile(
                self.device.handle,
                self.channel,
                byref(velocity),
                byref(acceleration),
                byref(deceleration),
                byref(self.device.pError),
            )
        )

        if error_code == 0 or error_code == _DEVICE_DISCONNECTED:
            # EPOS is disconnected
            return (
                self.get_attribute(ATTR_VELOCITY)[VALUE],
                self.get_attribute(ATTR_ACCELERATION)[VALUE],
                self.get_attribute(ATTR_DECELERATION)[VALUE],
            )

        self.set_offsetted_value(
            [GROUP_POSITION_PROFILE, ATTR_VELOCITY], velocity.value
        )
        self.set_offsetted_value(
            [GROUP_POSITION_PROFILE, ATTR_ACCELERATION], acceleration.value
        )
        self.set_offsetted_value(
            [GROUP_POSITION_PROFILE, ATTR_DECELERATION], deceleration.value
        )
        return velocity.value, acceleration.value, deceleration.value

    def set_operation_mode(self, value):
        operation_mode = self.operation_modes.inverse[value]
        self.device.check_error(
            self.device.library.VCS_SetOperationMode(
                self.device.handle,
                self.channel,
                c_int8(operation_mode),
                byref(self.device.pError),
            )
        )
        self.get_operation_mode()

    def set_velocity(self, velocity):
        velocity = int(velocity)
        self.logger.debug("Set velocity to: {} RPM".format(velocity))
        self.set_motor_enabled(True)
        self.set_operation_mode(self.operation_modes[MODE_PROFILE_VELOCITY])
        self.device.check_error(
            self.device.library.VCS_MoveWithVelocity(
                self.device.handle,
                self.channel,
                c_int64(velocity),
                byref(self.device.pError),
            )
        )

    def set_absolute_position(self, position, absolute=True):
        position = int(position)
        self.logger.debug("Set absolute position to: {} deg".format(position))
        self.set_motor_enabled(True)
        self.set_operation_mode(self.operation_modes[MODE_PROFILE_POSITION])
        self.device.check_error(
            self.device.library.VCS_MoveToPosition(
                self.device.handle,
                self.channel,
                c_int64(position),
                c_int(absolute),
                c_int(True),
                byref(self.device.pError),
            )
        )

    def set_position(self, position):
        position = float(position)
        self.logger.debug("Set position to: {} deg".format(position))
        attribute = self.get_attribute(ATTR_ABSOLUTE_POSITION)
        self.set_absolute_position(
            attribute.remove_offset_factor(
                (self[ATTR_REVOLUTIONS].value().m * 360) + position
            )
        )

    def set_motor_enabled(self, value):
        """
        Enable motor for remote control.

        :param value: enable flag (0 - Off, 1 - On)
        :type value: int
        """
        if value:
            self.logger.info("Motor enabled")
            self.device.check_error(
                self.device.library.VCS_SetEnableState(
                    self.device.handle, self.channel, byref(self.device.pError)
                )
            )
        else:
            self.logger.info("Motor disabled")
            self.device.check_error(
                self.device.library.VCS_SetDisableState(
                    self.device.handle, self.channel, byref(self.device.pError)
                )
            )

    def set_velocity_units(self, value):
        self.set_motor_enabled(False)
        dimension = c_uint8()
        notation = c_int8()
        self.device.check_error(
            self.device.library.VCS_GetVelocityUnits(
                self.device.handle,
                self.channel,
                byref(dimension),
                byref(notation),
                byref(self.device.pError),
            )
        )
        notation = c_int8(self.velocity_units.get(value, 0))
        self.device.check_error(
            self.device.library.VCS_SetVelocityUnits(
                self.device.handle,
                self.channel,
                dimension,
                notation,
                byref(self.device.pError),
            )
        )

    def set_velocity_profile(self, acceleration=None, deceleration=None):
        acceleration = c_int(
            int(
                self.get_value([GROUP_VELOCITY_PROFILE, ATTR_ACCELERATION])
                if acceleration is None
                else acceleration
            )
        )
        deceleration = c_int(
            int(
                self.get_value([GROUP_VELOCITY_PROFILE, ATTR_DECELERATION])
                if deceleration is None
                else deceleration
            )
        )
        self.device.check_error(
            self.device.library.VCS_SetVelocityProfile(
                self.device.handle,
                self.channel,
                acceleration,
                deceleration,
                byref(self.device.pError),
            )
        )

    def set_position_profile(self, velocity=None, acceleration=None, deceleration=None):
        velocity = c_int(
            int(
                self.get_value([GROUP_VELOCITY_PROFILE, ATTR_VELOCITY])
                if velocity is None
                else velocity
            )
        )
        acceleration = c_int(
            int(
                self.get_value([GROUP_VELOCITY_PROFILE, ATTR_ACCELERATION])
                if acceleration is None
                else acceleration
            )
        )
        deceleration = c_int(
            int(
                self.get_value([GROUP_VELOCITY_PROFILE, ATTR_DECELERATION])
                if deceleration is None
                else deceleration
            )
        )
        self.device.check_error(
            self.device.library.VCS_SetPositionProfile(
                self.device.handle,
                self.channel,
                velocity,
                acceleration,
                deceleration,
                byref(self.device.pError),
            )
        )

    @expose_method()
    def stop(self):
        self.device.check_error(
            self.device.library.VCS_HaltVelocityMovement(
                self.device.handle, self.channel, byref(self.device.pError)
            )
        )
        self.set_motor_enabled(False)

    def poll_callback(self):
        self.get_velocity()
        self.get_position()
        self.get_enabled_state()
        self.get_state()
        if (
            self.get_value(ATTR_AUTO_STOP)
            and self.get_value(ATTR_OPERATION_MODE)
            == self.operation_modes[MODE_PROFILE_POSITION]
            and self.get_movement_state()
        ):
            self.stop()
        elif (
            self.get_value(ATTR_AUTO_STOP)
            and self.get_value(ATTR_OPERATION_MODE)
            == self.operation_modes[MODE_PROFILE_VELOCITY]
            and self.get_movement_state()
            and self.get_value(ATTR_VELOCITY) == 0
            and self.get_attribute([ATTR_VELOCITY, SETPOINT]) == 0
        ):
            self.stop()

    def start_polling(self):
        self.polling = True
        self.polling_timer = PreciseCallbackTimer(300, self.poll_callback)
        self.polling_timer.start()

    def stop_polling(self):
        self.polling = False
        if self.polling_timer is not None:
            self.polling_timer.stop()

    @expose_method({"position": ATTR_POSITION})
    def move_absolute(self, position):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info(
                "Move motor channel to absolute position {}".format(position)
            )
            return self.set_value(ATTR_POSITION, position.m)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method({"position": ATTR_POSITION})
    def move_relative(self, position):
        try:
            position = device_units(self, ATTR_POSITION, position)
            self.logger.info("Move by relative position {}".format(position))
            return self.set_value(ATTR_POSITION, self[ATTR_POSITION].value() + position)
        except (UndefinedUnitError, ValueError) as e:
            self.logger.exception(e)
            raise DeviceUnitError(e)

    @expose_method()
    def reset_position(self):
        self.set_operation_mode(self.operation_modes[MODE_HOMING])
        self.device.check_error(
            self.device.library.VCS_FindHome(
                self.device.handle, self.channel, c_uint8(35), byref(self.device.pError)
            )
        )
