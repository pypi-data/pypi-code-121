from math import ceil

import numpy as np

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.deviceNiCard import DeviceNiCard, GROUP_DO

try:
    from PyDAQmx import *
except ImportError:
    raise DeviceError("PyDAQmx import error!")
from ctypes import *


# disable pylint errors related to the external library PyDAQmx these attributes
# do exist
# pylint: disable=undefined-variable
class DeviceRheodyneBox(DeviceNiCard):
    max_channels_per_switch = 6

    def __init__(self, card_address, active_switches, device_id=None, config=None):
        self.active_switches = active_switches
        super().__init__(card_address, device_id, config)

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(
            ATTR_ACTIVE_SWITCHES,
            default_value=self.active_switches,
            readonly=True,
            default_type=np.uint32,
            min_value=1,
        )
        for i in range(self.active_switches):
            switch_name = "Switch{}".format(i + 1)
            self.attributes[switch_name] = {}
            sample_names = []
            for j in range(self.max_channels_per_switch):
                sample_name = "Sample {} name".format(j + 1)
                sample_names.append("Sample {}".format(j + 1))
                self.create_attribute(
                    sample_name,
                    switch_name,
                    default_value="Sample {}".format(j + 1),
                    set_function=lambda sn, i=i + 1, j=j + 1: self.set_sample_name(
                        i, j, sn
                    ),
                )

            self.create_attribute(
                ATTR_CURRENT_SAMPLE,
                switch_name,
                default_type=sample_names,
                set_function=lambda sn, i=i + 1: self.set_current_sample(i, sn),
            )
            self.create_attribute(
                ATTR_CURRENT_CHANNEL,
                switch_name,
                default_type=np.uint16,
                min_value=1,
                max_value=self.max_channels_per_switch,
                set_function=lambda ch, i=i + 1: self.set_current_channel(i, ch),
            )

    def set_current_sample(self, switch, sample_name):
        switch_name = "Switch{}".format(switch)
        self.logger.info(
            "Setting Sample: {} on Switch: {}".format(sample_name, switch_name)
        )
        default_type = self.attributes[switch_name][ATTR_CURRENT_SAMPLE][
            TYPE_LIST_VALUES
        ]
        channel = default_type.index(sample_name) + 1
        self.set_current_channel(switch, channel)

    def set_current_channel(self, switch, channel):
        switch_name = "Switch{}".format(switch)
        channel = int(channel)
        self.logger.info(
            "Setting Channel: {} on Switch: {}".format(channel, switch_name)
        )
        default_type = self.attributes[switch_name][ATTR_CURRENT_SAMPLE][
            TYPE_LIST_VALUES
        ]
        self.set_value([switch_name, ATTR_CURRENT_SAMPLE], default_type[channel - 1])
        self.set_value([switch_name, ATTR_CURRENT_CHANNEL], channel)
        port = ceil(switch / 2) - 1
        _line_bits, myline = ([16, 32, 64, 128], [1, 2, 4, 8])[switch % 2], (
            [4, 5, 6, 7],
            [0, 1, 2, 3],
        )[switch % 2]

        try:
            self.write_do_task = self.task("set_digital_output_task")
            self.add_active_task(self.write_do_task, "set_digital_output_task")
            self.write_do_task.CreateDOChan(
                "{}/port{}/line{}:{}".format(
                    self.card_address, port, myline[0], myline[-1]
                ),
                "",
                DAQmx_Val_ChanForAllLines,
            )
            self.start_task(self.write_do_task.taskHandle.value)
            data = np.array(
                [
                    bool(channel & 1),
                    bool(channel & 2),
                    bool(channel & 4),
                    bool(channel & 8),
                ],
                # FIXME: pretty sure this is supposed to be np.uint8?
                dtype=uInt8,
            )
            DAQmxWriteDigitalLines(
                self.write_do_task.taskHandle.value,
                1,
                1,
                10.0,
                DAQmx_Val_GroupByChannel,
                data,
                None,
                None,
            )
            self.stop_task("set_digital_output_task")
        except DAQError:
            raise DeviceError("Error setting digital output")

    def set_sample_name(self, switch, channel, sample_name):
        switch_name = "Switch{}".format(switch)
        channel = int(channel)
        default_type = self.attributes[switch_name][ATTR_CURRENT_SAMPLE][
            TYPE_LIST_VALUES
        ]
        default_type[channel - 1] = sample_name
        self.set_attribute(
            [switch_name, ATTR_CURRENT_SAMPLE, TYPE_LIST_VALUES], default_type
        )

    def handle_configuration(self):
        super().handle_configuration()
        self.read_digital_output()

        if self.config.get("macros"):
            for macro_name, macro_config in self.config.get("macros").items():
                setattr(
                    self,
                    macro_name,
                    lambda macro_config=macro_config: self.execute_configured_macro(
                        macro_config
                    ),
                )
                self.exposed_methods.append((macro_name, None))

    def execute_configured_macro(self, macro_config):
        switches, channels = macro_config
        if isinstance(channels, int):
            channels = [channels] * len(switches)
        if len(switches) != len(channels):
            raise DeviceError("Number of switches is not equal numbers of channels")
        for i, switch in enumerate(switches):
            channel = channels[i]
            self.set_current_channel(switch, channel)
        self.read_digital_output()

    def read_digital_output(self):
        try:
            self.read_do_task = self.task("get_digital_input_task")
            self.add_active_task(self.read_do_task, "get_digital_input_task")
            self.read_do_task.CreateDOChan(
                "{}/port0/line0:7".format(self.card_address),
                "",
                DAQmx_Val_ChanForAllLines,
            )
            self.read_do_task.CreateDOChan(
                "{}/port1/line0:7".format(self.card_address),
                "",
                DAQmx_Val_ChanForAllLines,
            )
            self.read_do_task.CreateDOChan(
                "{}/port2/line0:7".format(self.card_address),
                "",
                DAQmx_Val_ChanForAllLines,
            )
            self.start_task(self.read_do_task.taskHandle.value)
            task_buffer = np.zeros([1000], dtype=np.uint8)
            # FIXME: pretty sure this is supposed to be np.int32?
            read = int32()
            # FIXME: pretty sure this is supposed to be np.int32?
            bytesPerSamp = int32()
            DAQmxReadDigitalLines(
                self.read_do_task.taskHandle.value,
                1,
                10.0,
                DAQmx_Val_GroupByChannel,
                task_buffer,
                100,
                byref(read),
                byref(bytesPerSamp),
                None,
            )

            word = ""
            switch = 1
            for i, do_line in enumerate(self[GROUP_DO].keys()):
                self.set_value([GROUP_DO, do_line], int(task_buffer[i]))
                if (i + 1) % 4 == 0 and switch <= self.active_switches:
                    switch_name = "Switch{}".format(switch)
                    default_type = self.attributes[switch_name][ATTR_CURRENT_SAMPLE][
                        TYPE_LIST_VALUES
                    ]
                    channel = int(word, 2)
                    if channel > self.max_channels_per_switch:
                        channel = 1
                    self.set_value(
                        [switch_name, ATTR_CURRENT_SAMPLE], default_type[channel - 1]
                    )
                    self.set_value([switch_name, ATTR_CURRENT_CHANNEL], channel)
                    word = ""
                    switch += 1
                else:
                    word = str(task_buffer[i]) + word

            self.stop_task("get_digital_input_task")
        except DAQError:
            raise DeviceError("Error getting digital inputs")
