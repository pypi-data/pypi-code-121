import copy
import time
from threading import Thread, Lock
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import bidict
import numpy as np
import smaract.picoscale as ps
from smaract import si

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.deviceChannel import DeviceChannel
from kamzik3.devices.subject import Subject
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsTimer import PreciseCallbackTimer

use_data_source_types = {
    si.DataSource.POSITION: "Position",
    si.DataSource.TEMPERATURE: "Temperature",
    si.DataSource.HUMIDITY: "Humidity",
    si.DataSource.PRESSURE: "Pressure",
    si.DataSource.SIN_QUALITY: "Sin quality",
}


datatypes = {
    si.DataType.INT8: np.int8,
    si.DataType.UINT8: np.uint8,
    si.DataType.INT16: np.int16,
    si.DataType.UINT16: np.uint16,
    si.DataType.INT32: np.int32,
    si.DataType.UINT32: np.uint32,
    si.DataType.INT48: np.int64,
    si.DataType.UINT48: np.uint64,
    si.DataType.INT64: np.int64,
    si.DataType.UINT64: np.uint64,
    si.DataType.FLOAT32: np.float32,
    si.DataType.FLOAT64: np.float64,
    si.DataType.STRING: str,
}

si_units = {
    si.BaseUnit.METRE: "m",
    si.BaseUnit.NO: None,
    si.BaseUnit.DEGREE: "deg",
    si.BaseUnit.DEGREE_CELSIUS: "degC",
    si.BaseUnit.AMPERE: "A",
    si.BaseUnit.HERTZ: "Hz",
    si.BaseUnit.KELVIN: "k",
    si.BaseUnit.KILOGRAM: "Kg",
    si.BaseUnit.PERCENT: "%",
    si.BaseUnit.SECOND: "s",
    si.BaseUnit.WATT: "W",
    si.BaseUnit.VOLT: "V",
    si.BaseUnit.PASCAL: "Pa",
}

streaming_modes = bidict.FrozenOrderedBidict(
    {
        si.StreamingMode.DIRECT: "Direct",
        si.StreamingMode.TRIGGERED: "Triggered",
    }
)

DISABLED = 0
ENABLED = 1
GROUP_STREAMING = "Streaming"


class DevicePicoscale(Device):
    # Increase connection timeout, since this Device takes it's time.
    # Usually it takes about 20 seconds.
    # To be safe, set connection timeout to 25 seconds
    connection_timeout = 25000
    polling = False
    polling_timer = None

    def __init__(
        self,
        locator: str,
        device_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Locator defines where to find Picoscale unit.

        From documentation some examples:
            usb:ix:0
            network:192.168.1.100:55555

        :param locator: locator address
        :type locator: str
        :param device_id: device ID
        :type device_id: str
        :param config: config dict
        :type config: dict
        """
        self.locator = locator
        self.handle = None
        self.polled_functions: List[Callable] = []
        self.stream_sources: List[Tuple[Any, Any]] = []
        self.stream_buffers: Dict[Tuple[Any, Any], Any] = {}
        self.available_head_types: bidict.OrderedBidict[
            str, Tuple[int, int]
        ] = bidict.OrderedBidict()
        self.readout_lock = Lock()
        Device.__init__(self, device_id, config)
        self.connect()

    def connect(self, *args) -> None:
        """
        Use si.Open to connect to PicoScale.

        It returns a handle to the device. According to what we observe, only one client
        can be connected at the same time. It's also taking a long time to connect.
        In some cases close to 20 seconds.

        :param args: connect attributes
        """
        try:
            self.connecting = True
            self.connected = False
            self.device_connection_poller.add_connecting_device(self)
            self.handle = si.Open(self.locator)
            self.handle_connect_event()
        except si.Error as e:
            self.logger.exception(f"Connection exception: {self.get_exception(e)}")
        except DeviceError:
            self.logger.exception("Connection exception")
            return

    def _init_attributes(self) -> None:
        Device._init_attributes(self)
        self.create_attribute(ATTR_SERIAL_NUMBER, readonly=True)
        self.create_attribute(ATTR_CHANNELS, readonly=True, default_type=np.uint16)
        self.create_attribute(
            ATTR_FULL_ACCESS,
            default_value=True,
            default_type=bool,
            set_function=self.set_full_access,
        )
        self.create_attribute(
            ATTR_PILOT_LASER,
            default_value=False,
            default_type=bool,
            set_function=self.set_pilot_laser,
        )
        self.create_attribute(ATTR_IS_STABLE, readonly=True, default_type=bool)
        self.create_attribute(
            ATTR_FRAME_AGGREGATION,
            group=GROUP_STREAMING,
            default_value=1,
            default_type=np.uint32,
            set_function=self.set_frame_aggregation,
            min_value=1,
            max_value=1,
        )
        self.create_attribute(
            ATTR_FRAMERATE,
            group=GROUP_STREAMING,
            default_value=1,
            default_type=np.uint32,
            set_function=self.set_frame_rate,
            unit="Hz",
            min_value=1,
            max_value=10e6,
        )
        self.create_attribute(
            ATTR_BUFFER_AGGREGATION,
            group=GROUP_STREAMING,
            default_value=0,
            default_type=np.uint32,
            set_function=self.set_buffer_aggregation,
            min_value=0,
        )
        self.create_attribute(
            ATTR_STREAMING_MODE,
            group=GROUP_STREAMING,
            default_value=streaming_modes[si.StreamingMode.DIRECT],
            default_type=list(streaming_modes.values()),
            set_function=self.set_streaming_mode,
        )
        self.create_attribute(
            ATTR_BUFFERS_INTERLEAVED,
            group=GROUP_STREAMING,
            default_value=False,
            default_type=bool,
            set_function=self.set_buffers_interleaved,
        )
        self.create_attribute(
            ATTR_FILTER_RATE,
            group=GROUP_STREAMING,
            default_value=10e6,
            default_type=np.float64,
            set_function=self.set_filter_rate,
            min_value=1,
            max_value=10e6,
            unit="Hz",
        )
        self.create_attribute(
            ATTR_BUFFERS_COUNT,
            group=GROUP_STREAMING,
            default_value=2,
            default_type=np.uint32,
            set_function=self.set_buffers_count,
            min_value=2,
            max_value=255,
        )
        self.create_attribute(
            ATTR_HEAD_FIBER_LENGTH,
            default_value=1660,
            default_type=np.float64,
            set_function=self.set_head_fiber_length,
            min_value=0,
            unit="mm",
            decimals=1,
        )
        self.create_attribute(
            ATTR_EXTENSION_FIBER_LENGTH,
            default_value=1660,
            default_type=np.float64,
            set_function=self.set_extension_fiber_length,
            min_value=0,
            unit="mm",
            decimals=1,
        )
        self.create_attribute(
            ATTR_MIN_WORKING_DISTANCE,
            default_value=1,
            default_type=np.float64,
            set_function=self.set_min_working_distance,
            min_value=1,
            max_value=500,
            unit="mm",
            decimals=1,
        )
        self.create_attribute(
            ATTR_MAX_WORKING_DISTANCE,
            default_value=1,
            default_type=np.float64,
            set_function=self.set_max_working_distance,
            min_value=1,
            max_value=500,
            unit="mm",
            decimals=1,
        )

        self.create_attribute(
            ATTR_PRECISION_MODE,
            default_value=0,
            min_value=0,
            max_value=5,
            readonly=False,
            set_function=self.set_precision_mode,
            default_type=int,
            unit="",
        )

    def handle_configuration(self) -> None:
        """
        Configure the Picoscale.

        Configuration requires full access.

        The method 'config_filtered_attributes' is called with a filtered config instead
        of the usual method '_config_attributes', because we don't want to go to the
        time_consuming manual adjustment mode at each connection of the server. Instead,
        the config attributes ATTR_MIN_WORKING_DISTANCE and ATTR_MAX_WORKING_DISTANCE
        are set on demand in the exposed method 'start_manual_adjustment'.

        ATTR_PRECISION_MODE must be set after loading the configuration slot
        (see in DeviceIfer.handle_configuration).
        """
        start_at = time.time()
        try:
            self.set_full_access(True)
        except DeviceError:
            self.logger.error("Full access could not be acquired!")

        self._config_commands()

        filtered_attributes = copy.deepcopy(self.config.get("attributes", {}))
        keys = list(filtered_attributes.keys())
        for key in keys:
            if key[0] in [
                ATTR_MIN_WORKING_DISTANCE,
                ATTR_MAX_WORKING_DISTANCE,
                ATTR_PRECISION_MODE,
            ]:
                del filtered_attributes[key]
        self.config_filtered_attributes(attributes=filtered_attributes)

        serial_number = si.GetProperty_s(
            self.handle, si.EPK(si.Property.DEVICE_SERIAL_NUMBER, 0, 0)
        )
        self.set_value(ATTR_SERIAL_NUMBER, serial_number)
        number_of_channels = si.GetProperty_i32(
            self.handle, si.EPK(si.Property.NUMBER_OF_CHANNELS, 0, 0)
        )
        self.set_value(ATTR_CHANNELS, number_of_channels)
        head_fiber_length = si.GetProperty_f64(
            self.handle, si.EPK(ps.Property.SYS_FIBERLENGTH_HEAD, 0, 0)
        )
        self.set_offsetted_value(ATTR_HEAD_FIBER_LENGTH, head_fiber_length)
        extension_fiber_length = si.GetProperty_f64(
            self.handle, si.EPK(ps.Property.SYS_FIBERLENGTH_EXTENSION, 0, 0)
        )
        self.set_offsetted_value(ATTR_EXTENSION_FIBER_LENGTH, extension_fiber_length)
        min_working_distance = si.GetProperty_f64(
            self.handle, si.EPK(ps.Property.SYS_WORKING_DISTANCE_MIN, 0, 0)
        )
        self.set_offsetted_value(ATTR_MIN_WORKING_DISTANCE, min_working_distance)
        max_working_distance = si.GetProperty_f64(
            self.handle, si.EPK(ps.Property.SYS_WORKING_DISTANCE_MAX, 0, 0)
        )
        self.set_offsetted_value(ATTR_MAX_WORKING_DISTANCE, max_working_distance)

        head_type_category_count = si.GetProperty_i32(
            self.handle, si.EPK(ps.Property.SYS_HEAD_TYPE_CATEGORY_COUNT, 0, 0)
        )
        for category_index in range(head_type_category_count):
            head_type_count = si.GetProperty_i32(
                self.handle, si.EPK(ps.Property.SYS_HEAD_TYPE_COUNT, category_index, 0)
            )
            _head_category_name = si.GetProperty_s(
                self.handle,
                si.EPK(ps.Property.SYS_HEAD_TYPE_CATEGORY_NAME, category_index, 0),
            )
            for head_type_index in range(head_type_count):
                head_type_name = si.GetProperty_s(
                    self.handle,
                    si.EPK(
                        ps.Property.SYS_HEAD_TYPE_NAME, category_index, head_type_index
                    ),
                )
                self.available_head_types[head_type_name] = (
                    category_index,
                    head_type_index,
                )
        self.get_pilot_laser()
        self.get_system_stable()
        self.start_polling()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def set_min_working_distance(self, value: float) -> None:
        self.logger.info(
            f"Setting min working distance to {value} "
            f"{self.get_attribute([ATTR_MIN_WORKING_DISTANCE, UNIT])}"
        )
        try:
            si.SetProperty_f64(
                self.handle, si.EPK(ps.Property.SYS_WORKING_DISTANCE_MIN, 0, 0), value
            )
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.SYS_WORKING_DISTANCE_ACTIVATE, 0, 0), 1
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_max_working_distance(self, value: float) -> None:
        self.logger.info(
            f"Setting max working distance to {value} "
            f"{self.get_attribute([ATTR_MAX_WORKING_DISTANCE, UNIT])}"
        )
        try:
            si.SetProperty_f64(
                self.handle, si.EPK(ps.Property.SYS_WORKING_DISTANCE_MAX, 0, 0), value
            )
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.SYS_WORKING_DISTANCE_ACTIVATE, 0, 0), 1
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_head_fiber_length(self, value: float) -> None:
        self.logger.info(
            f"Setting fiber length to {value} "
            f"{self.get_attribute([ATTR_HEAD_FIBER_LENGTH, UNIT])}"
        )
        try:
            si.SetProperty_f64(
                self.handle, si.EPK(ps.Property.SYS_FIBERLENGTH_HEAD, 0, 0), value
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_extension_fiber_length(self, value: float) -> None:
        self.logger.info(
            f"Setting extension fiber length to {value} "
            f"{self.get_attribute([ATTR_EXTENSION_FIBER_LENGTH, UNIT])}"
        )
        try:
            si.SetProperty_f64(
                self.handle, si.EPK(ps.Property.SYS_FIBERLENGTH_EXTENSION, 0, 0), value
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_buffers_count(self, value: int) -> None:
        """
        Set number of buffers we want to use for streaming.

        Usually we want to use maximum number 255.

        :param value: Number of buffers
        """
        self.logger.info(f"Setting buffers count to {value} ")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(si.Property.NUMBER_OF_STREAMBUFFERS, 0, 0),
                int(value),
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_buffers_interleaved(self, value: bool) -> None:
        """
        Set to True, when You want to interleave multiple sources into one buffer.

        :param value: flag
        """
        self.logger.info(f"Setting buffers interleaved to {value} ")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(si.Property.STREAMBUFFERS_INTERLEAVED, 0, 0),
                int(value),
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_filter_rate(self, value: float) -> None:
        """
        Set filtering rate self.configure_digital_outputs() of data.

        Usually we want to set same value as frame rate.
        :param value: Filter self.configure_digital_outputs() rate value
        """
        self.logger.info(f"Setting filter rate to {value} ")
        try:
            si.SetProperty_f64(
                self.handle, si.EPK(ps.Property.SYS_FILTER_RATE, 0, 0), value
            )
            real_filter_rate = si.GetProperty_f64(
                self.handle, si.EPK(ps.Property.SYS_FILTER_RATE, 0, 0)
            )
            self.set_offsetted_value(
                [GROUP_STREAMING, ATTR_FILTER_RATE], real_filter_rate
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_frame_aggregation(self, value: int) -> None:
        self.logger.info(f"Setting frame aggregation to {value} ")

        try:
            si.SetProperty_i32(
                self.handle, si.EPK(si.Property.FRAME_AGGREGATION, 0, 0), value
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_buffer_aggregation(self, value: int):
        self.logger.info(f"Setting buffer aggregation to {value} ")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(si.Property.STREAMBUFFER_AGGREGATION, 0, 0),
                value,
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_frame_rate(self, value: int) -> None:
        self.logger.info(f"Setting frame rate to {value} ")
        try:
            si.SetProperty_i32(self.handle, si.EPK(si.Property.FRAME_RATE, 0, 0), value)
            real_frame_rate = si.GetProperty_f64(
                self.handle, si.EPK(si.Property.PRECISE_FRAME_RATE, 0, 0)
            )
            self.set_offsetted_value([GROUP_STREAMING, ATTR_FRAMERATE], real_frame_rate)
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_streaming_mode(self, value: str) -> None:
        mode = streaming_modes.inverse.get(value)
        self.logger.info(f"Setting streaming mode to {value} ")
        try:
            si.SetProperty_i32(
                self.handle, si.EPK(si.Property.STREAMING_MODE, 0, 0), mode
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method({"mode": "precision mode"})
    def set_precision_mode(self, mode: str) -> None:
        """
        Set the precision mode to the desired level.

        It will return an error if precision mode feature is not available. The valid
        range is 0...5

        :param mode: the mode number. 'default' is mode 0.
        """
        self.logger.info(f"Setting precision mode to {int(mode)} ")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.AF_PRECISION_MODE_LEVEL, 0, 0),
                int(mode),
            )
        except si.Error as e:
            if e.code == si.ErrorCode.PERMISSION_DENIED:
                self.logger.error("'Precision mode' feature not available")
                self.get_attribute(ATTR_PRECISION_MODE)[VALUE] = 0
            else:
                raise DeviceError(self.get_exception(e))

    @expose_method({"slot": "configuration slot"})
    def load_configuration_slot(self, slot: str) -> None:
        """
        Load a configuration slot.

        It will return an error if the slot does not exist.

        :param slot: the slot number. 'default' is slot 0.
        """
        self.logger.info(f"Loading configuration slot {int(slot)} ")
        try:
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.SYS_CONFIGURATION_LOAD, int(slot), 0), 1
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method()
    def start_manual_adjustment(self) -> None:
        """
        Change to manual adjustment mode.

        If ATTR_MIN_WORKING_DISTANCE and ATTR_MAX_WORKING_DISTANCE are defined in the
        config, these attributes will be set here.
        """
        self.logger.info("Starting manual adjustment")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.AF_ADJUSTMENT_STATE, 0, 0),
                ps.AdjustmentState.MANUAL_ADJUST,
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

        if self.config:
            for attribute, value in self.config.get("attributes", {}).items():
                if attribute[0] == ATTR_MIN_WORKING_DISTANCE:
                    min_distance = self.to_device_unit(ATTR_MIN_WORKING_DISTANCE, value)
                    self.set_min_working_distance(min_distance.m)
                if attribute[0] == ATTR_MAX_WORKING_DISTANCE:
                    max_distance = self.to_device_unit(ATTR_MAX_WORKING_DISTANCE, value)
                    self.set_max_working_distance(max_distance.m)

    @expose_method()
    def start_auto_adjustment(self) -> None:
        self.logger.info("Starting automatic adjustment")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.AF_ADJUSTMENT_STATE, 0, 0),
                ps.AdjustmentState.AUTO_ADJUST,
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method()
    def stop_adjustment(self) -> None:
        self.logger.info("Disabling adjustment")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.AF_ADJUSTMENT_STATE, 0, 0),
                ps.AdjustmentState.DISABLED,
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method({"clear_values": "Clear previous streamed values"})
    def start_streaming(self, clear_values: Union[str, bool] = True) -> None:
        try:
            clear_values_flag = bool(int(clear_values))
            self.stream_sources = sorted(
                self.stream_sources, key=lambda element: (element[0], element[1])
            )
            for channel, source in self.stream_sources:
                if clear_values_flag:
                    self.notify((channel, source, ATTR_STREAM_READOUT), None)
                self.stream_buffers[(channel, source)] = []
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.SG_CLOCK_SOURCE, 0, 0),
                ps.StreamGeneratorSource.INTERNAL,
            )
            si.SetProperty_i32(
                self.handle,
                si.EPK(si.Property.STREAMING_MODE, 0, 0),
                si.StreamingMode.DIRECT,
            )
            si.SetProperty_i32(
                self.handle, si.EPK(si.Property.STREAMING_ACTIVE, 0, 0), si.ENABLED
            )
            self.set_status(STATUS_BUSY)
            Thread(target=self.stream_data_thread).start()
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method()
    def clear_streams(self) -> None:
        for channel, source in self.stream_sources:
            self.notify((channel, source, ATTR_STREAM_READOUT), None)
            self.stream_buffers[(channel, source)] = []

    @expose_method()
    def setup_triggered_stream(self) -> None:
        """
        Prepare triggered stream, that expects HW TTL signal _|¯¯¯¯|_.

        Setup inputs and outputs to collect streamed data for width of TTL pulse.
        """
        try:
            self.logger.info("Preparing triggering stream")
            # Setup source of Trigger 0 and 1 to External Trigger
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.TRIGGER_SOURCE_EVENT, 0, 0),
                ps.TriggerEvent.EXTERNAL_TRIGGER,
            )
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.TRIGGER_SOURCE_EVENT, 1, 0),
                ps.TriggerEvent.EXTERNAL_TRIGGER,
            )

            # Setup Trigger output to Immediate and don't reset stream at next trigger for trigger output 0 and 1
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.TRIGGER_OUTPUT_MODE, 0, 0),
                ps.TriggerOutputMode.IMMEDIATE_NO_RESET,
            )
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.TRIGGER_OUTPUT_MODE, 1, 0),
                ps.TriggerOutputMode.IMMEDIATE_NO_RESET,
            )

            # Setup Trigger start index to 0
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.SG_TRIGGER_START_INDEX, 0, 0), 0
            )
            # Setup Trigger stop index to 0
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.SG_TRIGGER_STOP_INDEX, 0, 0), 1
            )

            # Expect Positive Level on Trigger input 0 - start of Trigger pulse,
            # high level of TTL signal _|¯¯
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.TRIGGER_SOURCE_CONDITION, 0, 0),
                ps.TriggerCondition.POSITIVE_LEVEL,
            )
            # Expect Negative Level on Trigger input 0 - end of Trigger pulse,
            # low level of TTL signal ¯¯|_
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.TRIGGER_SOURCE_CONDITION, 1, 0),
                ps.TriggerCondition.NEGATIVE_LEVEL,
            )
            # Set Trigger logic for both trigger inputs to OR
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.TRIGGER_LOGIC_OPERATION, 0, 0),
                ps.TriggerLogicOperation.OR,
            )
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.TRIGGER_LOGIC_OPERATION, 1, 0),
                ps.TriggerLogicOperation.OR,
            )
            # Set Trigger OR and AND mask for both trigger inputs
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.TRIGGER_AND_MASK, 0, 0), 1
            )
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.TRIGGER_OR_MASK, 0, 0), 1
            )
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.TRIGGER_AND_MASK, 1, 0), 2
            )
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.TRIGGER_OR_MASK, 1, 0), 2
            )

            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.SG_TRIGGER_AUTO_RESET_MODE, 0, 0),
                si.ENABLED,
            )
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.SG_TRIGGER_POST_FRAME_COUNT, 0, 0), 0
            )

            # Set streaming mode to Trigger
            si.SetProperty_i32(
                self.handle,
                si.EPK(si.Property.STREAMING_MODE, 0, 0),
                si.StreamingMode.TRIGGERED,
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method({"clear_values": "Clear previous streamed values"})
    def wait_for_trigger(self, clear_values: Union[str, bool] = True) -> None:
        """
        Wait for HW trigger.

        clear_values should be set to True, when we are collecting sequence of triggers.
        Set it to False, when it's nth trigger within a sequence.

        :param clear_values: Clear Stream readout attribute
        """
        self.logger.info("Waiting for trigger")
        try:
            clear_values_flag = bool(int(clear_values))
            for channel, source in self.stream_sources:
                if clear_values_flag:
                    self.notify((channel, source, ATTR_STREAM_READOUT), None)
                self.stream_buffers[(channel, source)] = []

            si.SetProperty_i32(
                self.handle, si.EPK(si.Property.STREAMING_ACTIVE, 0, 0), si.ENABLED
            )
            self.set_status(STATUS_BUSY)
            Thread(target=self.stream_data_thread).start()
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method()
    def stop_streaming(self) -> None:
        """Stop streaming, either HW or SW triggered."""
        self.logger.info("Stopping streaming")
        try:
            si.SetProperty_i32(
                self.handle, si.EPK(si.Property.STREAMING_ACTIVE, 3, 0), si.DISABLED
            )
            self.set_status(STATUS_IDLE)
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method()
    def reset_streaming(self) -> None:
        """Reset all streaming attributes."""
        self.logger.info("Resetting all streaming attributes")
        try:
            si.ResetStreamingConfiguration(self.handle)
            self.set_value([ATTR_STREAMING, ATTR_FRAMERATE], 1)
            try:
                self.set_value([ATTR_STREAMING, ATTR_FILTER_RATE], 1)
            except:  # FIXME: catch the exception correctly
                pass
            self.set_value([ATTR_STREAMING, ATTR_BUFFERS_COUNT], 2)
            self.set_value([ATTR_STREAMING, ATTR_FRAME_AGGREGATION], 1)
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method()
    def save_adjustment_results(self) -> None:
        self.logger.info("Saving adjustment results")
        try:
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.AF_ADJUSTMENT_RESULT_SAVE, 1, 0), 1
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    @expose_method()
    def load_adjustment_results(self) -> None:
        self.logger.info("Loading adjustment results")
        try:
            si.SetProperty_i32(
                self.handle, si.EPK(ps.Property.AF_ADJUSTMENT_RESULT_LOAD, 1, 0), 1
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_full_access(self, value: bool) -> None:
        self.logger.info(f"Setting full access to {value}")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.SYS_FULL_ACCESS_CONNECTION, 0, 0),
                int(value),
            )
        except si.Error as e:
            raise DeviceError(self.get_exception(e))

    def set_pilot_laser(self, value: bool) -> None:
        self.logger.info(f"Setting pilot laser to {value}")
        try:
            si.SetProperty_i32(
                self.handle,
                si.EPK(ps.Property.SYS_PILOT_LASER_ACTIVE, 0, 0),
                int(value),
            )
        except si.Error as e:
            self.get_pilot_laser()
            raise DeviceError(self.get_exception(e))

    @staticmethod
    def get_exception(exception: si.Error) -> str:
        """
        Helper method to obtain Exception info from PicoScale.

        :param exception: thrown exception
        :type exception: Exception
        :return: Exception message
        :rtype: str
        """
        err_name = "(0x{:04X})".format(exception.code)
        if exception.code in set(err.value for err in si.ErrorCode):
            err_name = si.ErrorCode(exception.code).name + " " + err_name
        elif exception.code in set(err.value for err in ps.ErrorCode):
            err_name = ps.ErrorCode(exception.code).name + " " + err_name
        return f"SI {exception.func} error: {err_name}."

    def process_buffer(self, buffer: si.DataBuffer) -> bool:
        """
        Processes the contents of a buffer received from the API.

        This function would typically e.g. store the data to disc.
        In this example the data is stored in a buffer for later
        processing.

        :param buffer
        :return:
        """
        values = None
        for source_index in range(buffer.info.numberOfSources):
            values = si.CopyBuffer(self.handle, buffer.info.bufferId, source_index)
            channel, source = self.stream_sources[source_index]
            self.stream_buffers[(channel, source)] += values
        si.ReleaseBuffer(self.handle, buffer.info.bufferId)
        return bool(values == [])

    def stream_data_thread(self) -> None:
        """
        Continuously acquire buffers and write those into main big buffer.

        After stream is finished set stream_buffer for channel.
        To explain how this work.
        We are streaming at desired frequency, can be many kHz.
        We wait for event to read buffer and write it into main buffer.
        Important to notice it timeout variable.
        At the beginning we wait for TIMEOUT_INFINITE value, since there is timeout
        between start and actual start of stream.
        Normally, after stream stopped or was aborted, we would stop reading.
        But since we are dealing with buffers, we must be sure, that all data was read.
        For that reason we decrease timeout to 100 ms and wait until timeout.
        Which then is our signal, that we read all the data and can stop the Thread.
        """
        with self.readout_lock:
            self.logger.info("Starting streaming and buffer acquisition")
            timeout = si.TIMEOUT_INFINITE
            # This flag signals, that last buffer was empty and we read all buffers
            last_buffer_empty = False
            stream_stopped = False
            while True:
                try:
                    # Wait for new event from PicoScale
                    ev = si.WaitForEvent(self.handle, timeout)
                    if ev.type == si.EventType.STREAMBUFFER_READY:
                        # get buffer data
                        buffer = si.AcquireBuffer(self.handle, ev.bufferId)
                        last_buffer_empty = self.process_buffer(buffer)
                        if last_buffer_empty and stream_stopped:
                            break
                    elif ev.type in (
                        si.EventType.STREAM_STOPPED,
                        si.EventType.STREAM_ABORTED,
                    ):
                        # Stream was stopped or aborted
                        stream_stopped = True
                        if last_buffer_empty:
                            # Stop reading, only when last buffer was empty
                            break
                        # Reduce readout timeout
                        timeout = 100
                        continue
                    else:
                        self.logger.info(
                            f"Received unexpected event type: {ev.type} "
                            f"(parameter: {ev.devEventParameter})"
                        )
                        break
                except si.bindings.Error:
                    # Here readout was stopped due to readout timeout
                    break

            # Flush main stream buffers
            for channel, source in self.stream_sources:
                self.notify(
                    (channel, source, ATTR_STREAM_READOUT),
                    self.stream_buffers[(channel, source)],
                )

    def close(self) -> bool:
        """
        To properly close PicoScale, we need to close handle.

        Otherwise, we cannot connect to Device again.
        """
        try:
            if self.handle is not None:
                si.Close(self.handle)
        except Exception:
            pass
        finally:
            self.handle = None
        return Device.close(self)

    def get_full_access_state(self) -> None:
        """
        Obtain full access.

        This is important for setting triggering attributes.
        """
        full_access = si.GetProperty_i32(
            self.handle, si.EPK(ps.Property.SYS_FULL_ACCESS_CONNECTION, 0, 0)
        )
        self.set_offsetted_value(ATTR_FULL_ACCESS, full_access)

    def get_pilot_laser(self) -> None:
        """Get status of pilot laser, which is used for alignment."""
        pilot_laser = si.GetProperty_i32(
            self.handle, si.EPK(ps.Property.SYS_PILOT_LASER_ACTIVE, 0, 0)
        )
        self.set_offsetted_value(ATTR_PILOT_LASER, pilot_laser)

    def get_system_stable(self) -> None:
        """
        Get system stability flag.

        If system is not stable, we can't start streaming.
        """
        is_stable = si.GetProperty_i32(
            self.handle, si.EPK(ps.Property.SYS_IS_STABLE, 0, 0)
        )
        self.set_value(ATTR_IS_STABLE, is_stable)

    def get_trigger_state(self) -> None:
        """Get state of streaming."""
        # FIXME: This function isn't used and doesn't return anything, is it even needed?
        _trigger_state = si.GetProperty_i32(
            self.handle, si.EPK(ps.Property.TRIGGER_STATE, 0, 0)
        )

    def poll_callback(self) -> None:
        """At each poller tick, we execute all polled functions."""
        for fun in self.polled_functions:
            fun()

    def start_polling(self) -> None:
        self.polling = True
        self.polled_functions = [self.get_system_stable, self.get_full_access_state]
        self.polling_timer = PreciseCallbackTimer(300, self.poll_callback)
        self.polling_timer.start()

    def stop_polling(self) -> None:
        self.polling = False
        if self.polling_timer is not None:
            self.polling_timer.stop()


class DevicePicoscaleChannel(DeviceChannel):
    polling = False
    polling_timer = None

    def __init__(
        self,
        device: Device,
        channel: int,
        device_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.polled_functions: List[Callable] = []
        self.source_groups: Dict[int, str] = {}
        self.use_data_sources = (
            config.get("use_data_sources", []) if config is not None else []
        )
        DeviceChannel.__init__(self, device, channel, device_id, config)

    def _init_attributes(self) -> None:
        assert isinstance(self.device, DevicePicoscale)
        DeviceChannel._init_attributes(self)
        self.create_attribute(ATTR_SOURCES_COUNT, readonly=True)
        self.create_attribute(
            ATTR_HEAD_TYPE,
            default_type=self.device.available_head_types.keys(),
            set_function=self.set_head_type,
        )
        self.create_attribute(
            ATTR_BEAM_INTERRUPT_TOLERANCE,
            unit="%",
            min_value=0,
            max_value=100,
            set_function=self.set_beam_interrupt_tolerance,
            default_type=np.uint8,
        )
        self.create_attribute(
            ATTR_CHANNEL_ENABLED,
            readonly=False,
            set_function=self.set_channel_enabled,
            default_type=bool,
        )
        self.create_attribute(
            ATTR_DEAD_PATH_CORRECTION,
            readonly=False,
            set_function=self.set_deadpath_correction,
            default_type=bool,
        )

    def handle_configuration(self) -> None:
        if self.configured:
            return

        start_at = time.time()
        assert isinstance(self.device, DevicePicoscale)

        def _finish_configuration(*_, **__) -> None:
            self._config_commands()
            self._config_attributes()
            self.configured = True
            self.start_polling()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        self.connected = True
        number_of_data_sources = si.GetProperty_i32(
            self.device.handle,
            si.EPK(si.Property.NUMBER_OF_DATA_SOURCES, self.channel, 0),
        )
        self.set_value(ATTR_SOURCES_COUNT, number_of_data_sources)
        head_type = si.GetProperty_i32(
            self.device.handle, si.EPK(ps.Property.CH_HEAD_TYPE, self.channel, 0)
        )
        head_type_index, head_type_category = head_type.to_bytes(2, "little")
        head_type = self.device.available_head_types.inverse[
            (head_type_category, head_type_index)
        ]
        self.set_offsetted_value(ATTR_HEAD_TYPE, head_type)
        beam_interrupt_tolerance = si.GetProperty_i32(
            self.device.handle,
            si.EPK(ps.Property.CH_BEAM_INTERRUPT_TOLERANCE, self.channel, 0),
        )
        self.set_offsetted_value(
            ATTR_BEAM_INTERRUPT_TOLERANCE, beam_interrupt_tolerance
        )
        ch_enabled = bool(
            si.GetProperty_i32(
                self.device.handle, si.EPK(ps.Property.CH_ENABLED, self.channel, 0)
            )
        )
        self.set_offsetted_value(ATTR_CHANNEL_ENABLED, ch_enabled)

        dead_path_enabled = bool(
            si.GetProperty_i32(
                self.device.handle,
                si.EPK(ps.Property.CH_DEAD_PATH_CORRECTION_ENABLED, self.channel, 0),
            )
        )
        self.set_value(ATTR_DEAD_PATH_CORRECTION, dead_path_enabled)

        self._configure_sources()
        _finish_configuration()

    def set_deadpath_correction(self, value: bool) -> None:
        assert isinstance(self.device, DevicePicoscale)
        try:
            si.SetProperty_i32(
                self.device.handle,
                si.EPK(ps.Property.CH_DEAD_PATH_CORRECTION_ENABLED, self.channel, 0),
                int(value),
            )
        except si.Error as e:
            raise DeviceError(self.device.get_exception(e))

    def set_channel_enabled(self, value: bool) -> None:
        assert isinstance(self.device, DevicePicoscale)
        try:
            si.SetProperty_i32(
                self.device.handle,
                si.EPK(ps.Property.CH_ENABLED, self.channel, 0),
                int(value),
            )
        except si.Error as e:
            raise DeviceError(self.device.get_exception(e))

    def set_beam_interrupt_tolerance(self, value: int) -> None:
        assert isinstance(self.device, DevicePicoscale)
        try:
            si.SetProperty_i32(
                self.device.handle,
                si.EPK(ps.Property.CH_BEAM_INTERRUPT_TOLERANCE, self.channel, 0),
                int(value),
            )
        except si.Error as e:
            raise DeviceError(self.device.get_exception(e))

    def set_head_type(self, value: str) -> None:
        assert isinstance(self.device, DevicePicoscale)
        head_type_category, head_type_index = self.device.available_head_types[value]
        lb = head_type_index.to_bytes(1, "little")
        hb = head_type_category.to_bytes(1, "little")
        header_type = int.from_bytes(lb + hb, "little")
        try:
            si.SetProperty_i32(
                self.device.handle,
                si.EPK(ps.Property.CH_HEAD_TYPE, self.channel, 0),
                header_type,
            )
        except si.Error as e:
            raise DeviceError(self.device.get_exception(e))

    def _configure_sources(self) -> None:
        """
        Every channel has multiple Sources.

        We first obtain number of Source available on Channel.
        Then get through all of them and filter ones, that are in global variable
        use_data_source_types.
        """
        assert isinstance(self.device, DevicePicoscale)
        self.source_groups.clear()
        prefix = {-12: "p", -9: "n", -6: "u", -3: "m"}

        for source_index in range(self.get_value(ATTR_SOURCES_COUNT)):
            ds_type = si.GetProperty_i32(
                self.device.handle,
                si.EPK(si.Property.DATA_SOURCE_TYPE, self.channel, source_index),
            )
            if (
                ds_type in use_data_source_types
                or source_index in self.use_data_sources
            ):
                _data_type = si.GetProperty_i32(
                    self.device.handle,
                    si.EPK(si.Property.DATA_TYPE, self.channel, source_index),
                )
                base_unit = si.GetProperty_i32(
                    self.device.handle,
                    si.EPK(si.Property.BASE_UNIT, self.channel, source_index),
                )
                base_resolution = si.GetProperty_i32(
                    self.device.handle,
                    si.EPK(si.Property.BASE_RESOLUTION, self.channel, source_index),
                )
                streamable = si.GetProperty_i32(
                    self.device.handle,
                    si.EPK(si.Property.IS_STREAMABLE, self.channel, source_index),
                )
                group_name = (
                    f"{use_data_source_types.get(ds_type, f'Source_{source_index}')}"
                )
                self.source_groups[source_index] = group_name
                si_unit = si_units.get(base_unit, None)
                base_unit = None
                if si_unit is not None:
                    base_unit = prefix.get(base_resolution, "") + si_unit
                self.create_attribute(
                    ATTR_VALUE_READOUT,
                    default_type=np.float64,
                    unit=base_unit,
                    group=group_name,
                    readonly=True,
                    decimals=10,
                )
                self.create_attribute(
                    ATTR_ID,
                    group=group_name,
                    default_value=source_index,
                    readonly=True,
                    default_type=np.uint16,
                )
                if bool(streamable):
                    streaming_enabled = si.GetProperty_i32(
                        self.device.handle,
                        si.EPK(
                            si.Property.STREAMING_ENABLED, self.channel, source_index
                        ),
                    )
                    self.create_attribute(
                        ATTR_ALLOW_STREAM,
                        default_value=streaming_enabled,
                        group=group_name,
                        default_type=bool,
                        set_function=lambda v, source_index=source_index: self.set_allow_streaming(
                            source_index, v
                        ),
                    )
                else:
                    self.create_attribute(
                        ATTR_ALLOW_STREAM,
                        default_value=False,
                        group=group_name,
                        default_type=bool,
                    )
                if bool(streamable):
                    self.create_attribute(
                        ATTR_STREAM_READOUT,
                        default_value=[],
                        default_type=TYPE_ARRAY,
                        group=group_name,
                        readonly=True,
                        streaming_enabled=False,
                        unit=base_unit,
                        display=False,
                    )

    def subject_update(
        self, key: Union[str, Tuple[Any, ...]], value: Optional[Any], subject: Subject
    ) -> None:
        DeviceChannel.subject_update(self, key, value, subject)
        if self.connected and isinstance(key, tuple) and key[0] == self.channel:
            _, source, attribute = key
            group = self.source_groups[source]
            if attribute == ATTR_STREAM_READOUT:
                if value is not None:
                    self.get_value([group, attribute]).append(value)
                else:
                    self.set_value([group, attribute], [])
            else:
                self.set_value([group, attribute], value)

    def get_readout(self, source_group: str, attribute: str) -> Optional[float]:
        assert isinstance(self.device, DevicePicoscale)
        if self.device.handle is None:
            return None

        source_id = self.get_value([source_group, ATTR_ID])
        readout = si.GetValue_f64(self.device.handle, self.channel, source_id)
        self.set_value([source_group, attribute], readout)
        return readout

    def set_allow_streaming(self, source_index: int, value: int) -> None:
        assert isinstance(self.device, DevicePicoscale)
        si.SetProperty_i32(
            self.device.handle,
            si.EPK(si.Property.STREAMING_ENABLED, self.channel, source_index),
            value,
        )
        max_fa = si.GetProperty_i32(
            self.device.handle, si.EPK(si.Property.MAX_FRAME_AGGREGATION, 0, 0)
        )
        max_fr = si.GetProperty_i32(
            self.device.handle, si.EPK(si.Property.MAX_FRAME_RATE, 0, 0)
        )
        self.device.set_attribute(
            [GROUP_STREAMING, ATTR_FRAME_AGGREGATION, MAX], max_fa
        )
        self.device.set_attribute([GROUP_STREAMING, ATTR_FRAMERATE, MAX], max_fr)
        if value:
            self.device.stream_sources.append((self.channel, source_index))
        else:
            self.device.stream_sources.remove((self.channel, source_index))

    def poll_callback(self) -> None:
        for fun in self.polled_functions:
            try:
                fun()
            except si.bindings.Error:
                pass

    def start_polling(self) -> None:
        self.polling = True
        self.polled_functions = []
        for group in self.source_groups.values():
            self.polled_functions.append(
                lambda group=group: self.get_readout(group, ATTR_VALUE_READOUT)
            )
        self.polling_timer = PreciseCallbackTimer(300, self.poll_callback)
        self.polling_timer.start()

    def stop_polling(self) -> None:
        self.polling = False
        if self.polling_timer is not None:
            self.polling_timer.stop()

    @expose_method({"position": "New position"})
    def set_position(self, position: str) -> None:
        assert isinstance(self.device, DevicePicoscale)
        self.logger.info(f"Reset position to {position}")
        si.SetProperty_i64(
            self.device.handle,
            si.EPK(ps.Property.CH_POSITION, self.channel, 0),
            int(position),
        )
