import time

from kamzik3.devices.general.deviceGrabber import DeviceGrabber

try:
    import cv2
except ModuleNotFoundError:
    raise Exception("Module cv2 (opencv-python) was not found.")
import numpy as np

# pylint: disable=ungrouped-imports
from kamzik3.constants import *


# disable pylint errors related to the external library opencv-python, these attributes
# do exist
# pylint: disable=no-member
class DeviceCv2(DeviceGrabber):
    api_presets = {
        "Any": cv2.CAP_ANY,
        "FFmpeg": cv2.CAP_FFMPEG,
        "Gstreamer": cv2.CAP_GSTREAMER,
    }

    def _init_attributes(self):
        DeviceGrabber._init_attributes(self)
        self.create_attribute(ATTR_SOURCE)
        self.create_attribute(
            ATTR_SOURCE_FRAMERATE,
            default_value=0,
            default_type=np.float,
            unit="FPS",
            min_value=0,
            max_value=10000,
            decimals=2,
            readonly=True,
        )
        self.create_attribute(
            ATTR_SOURCE_WIDTH,
            default_value=0,
            default_type=np.uint,
            unit="px",
            min_value=0,
            max_value=2**32,
            readonly=True,
        )
        self.create_attribute(
            ATTR_SOURCE_HEIGHT,
            default_value=0,
            default_type=np.uint,
            unit="px",
            min_value=0,
            max_value=2**32,
            readonly=True,
        )
        self.create_attribute(
            ATTR_AUTO_SET_FRAMERATE,
            default_value=True,
            default_type=bool,
            set_function=self.set_auto_frameset,
        )
        self.create_attribute(
            ATTR_CAPTURE_API, default_value="Any", default_type=self.api_presets.keys()
        )

    def _acquire_loop(self):
        self.stopped.clear()
        capture_api = self.api_presets.get(
            self.get_value(ATTR_CAPTURE_API), cv2.CAP_ANY
        )
        try:
            cap = cv2.VideoCapture(int(self.get_value(ATTR_SOURCE)), capture_api)
        except ValueError:
            cap = cv2.VideoCapture(self.get_value(ATTR_SOURCE), capture_api)

        if not cap.isOpened():
            cap.release()
            return
        self.set_value(ATTR_SOURCE_FRAMERATE, cap.get(cv2.CAP_PROP_FPS))
        self.set_value(ATTR_SOURCE_WIDTH, cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.set_value(ATTR_SOURCE_HEIGHT, cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if self.get_value(ATTR_AUTO_SET_FRAMERATE):
            self.set_value(ATTR_FRAMERATE, self.get_value(ATTR_SOURCE_FRAMERATE))
        self.frame_delay = 1e9 / self.get_value(ATTR_FRAMERATE)
        self.set_status(STATUS_BUSY)
        fps_counter_reference = time_reference = time.perf_counter_ns()
        grabbed_frames_count = 0
        fps_counter = 0
        while not self.stopped.wait(
            (self.frame_delay - (time.perf_counter_ns() - time_reference)) * 1e-9
        ):
            time_reference = time.perf_counter_ns()
            ret, cv_img = cap.read()
            grabbed_frames_count += 1
            fps_counter += 1
            if ret:
                self.set_value(
                    ["Grabber", "Frame"], cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                )

            if (time.perf_counter_ns() - fps_counter_reference) >= 1e9:
                self.set_raw_value(ATTR_FRAMERATE, fps_counter)
                self.set_raw_value(ATTR_FRAMES_GRABBED, grabbed_frames_count)
                fps_counter = 0
                fps_counter_reference = time.perf_counter_ns()

    def set_auto_frameset(self, value):
        if value:
            self.set_value(ATTR_FRAMERATE, self.get_value(ATTR_SOURCE_FRAMERATE))
