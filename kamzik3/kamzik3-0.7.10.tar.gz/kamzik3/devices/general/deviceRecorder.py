import os
import re
from threading import Event

from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetDataAccess import get_next_file_index
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceRecorder(Device):
    # pylint: disable=unused-argument
    def __init__(self, device, attribute, device_id=None, config=None):
        self.stopped = Event()
        self.frame_delay = 0
        Device.__init__(self, device_id, config)
        self.connect()

    def handle_configuration(self):
        # has to be overridden, but doesn't make sense in this device
        pass

    def _init_attributes(self):
        Device._init_attributes(self)
        self.create_attribute(ATTR_OUTPUT_DIRECTORY, default_value="./")
        self.create_attribute(
            ATTR_FourCC_CODEC,
            default_value="X264",
            default_type=["X264", "XVID", "MJPG"],
        )
        self.create_attribute(
            ATTR_RECORDING, default_value=False, default_type=bool, readonly=True
        )
        self.create_attribute(ATTR_FILENAME_PREFIX, default_value="video")
        self.create_attribute(ATTR_OUTPUT_FILENAME, default_value=None, readonly=True)

    def setup_output_file(self):
        output_directory_path = self.get_value(["Record", ATTR_OUTPUT_DIRECTORY])
        file_prefix = self.get_value(["Record", ATTR_FILENAME_PREFIX])
        if not os.path.exists(output_directory_path):
            self.logger.info(
                "Output directory {} does not exists, trying to create it.".format(
                    output_directory_path
                )
            )
            os.makedirs(output_directory_path)
        next_index = get_next_file_index(
            output_directory_path, re.compile(rf"{file_prefix}_(\d+)\.mp4")
        )
        output_filename = os.path.join(
            output_directory_path, "{}_{}.mp4".format(file_prefix, next_index)
        )
        self.set_value(["Record", ATTR_OUTPUT_FILENAME], output_filename)

    @expose_method()
    def start_recording(self):
        self.setup_output_file()

    @expose_method()
    def stop_recording(self):
        pass
