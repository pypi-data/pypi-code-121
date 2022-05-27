import time

import cv2

from kamzik3.devices.general.deviceGrabber import DeviceGrabber

try:
    import mss
except ModuleNotFoundError:
    raise Exception("Module mss was not found.")
import numpy as np

# pylint: disable=ungrouped-imports
from kamzik3.constants import *


class DeviceScreenGrabber(DeviceGrabber):
    def __init__(self, device_id=None, config=None):
        self.region = {"top": 0, "left": 0, "width": 640, "height": 480}
        DeviceGrabber.__init__(self, device_id, config)

    def _init_attributes(self):
        DeviceGrabber._init_attributes(self)
        self.create_attribute(
            ATTR_CAPTURE_REGION,
            default_value="0, 0, 640, 480",
            unit="px",
            set_function=self.set_region,
        )

    def set_region(self, value):
        top, left, width, height = value.split(",")
        # Part of the screen to capture
        self.region = {
            "top": int(top),
            "left": int(left),
            "width": int(width),
            "height": int(height),
        }

    def _acquire_loop(self):
        self.stopped.clear()
        self.frame_delay = 1.0 / self.get_value(ATTR_FRAMERATE)
        self.set_status(STATUS_BUSY)
        time_reference = time.perf_counter_ns()
        with mss.mss() as sct:
            while not self.stopped.wait(
                self.frame_delay - (time.perf_counter_ns() - time_reference) * 1e-9
            ):
                img = np.array(sct.grab(self.region))
                # Don't know why pylint can't find cvtColor and COLOR_BGR2RGB
                # pylint: disable=no-member
                self.set_value(
                    ["Output", "Frame"], cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                )
                time_reference += self.frame_delay * 1e9
