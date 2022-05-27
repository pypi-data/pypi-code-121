import time
from random import randint
from threading import Event, Thread

import numpy as np

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.dummy.deviceDummy import DeviceDummy
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import device_units

ATTR_ACQUIRED_FRAMES = "Acquired frames"
ATTR_FRAME_NAME = "Frame name"
ATTR_FRAME_FILE = "Frame file"


class DummyDetector(DeviceDummy):
    offset = 0

    def __init__(self, device_id=None, config=None):
        self.acquisition_running = Event()
        DeviceDummy.__init__(self, device_id, config)

    def _init_attributes(self):
        DeviceDummy._init_attributes(self)
        self.create_attribute(
            ATTR_EXPOSURE_TIME,
            default_value=0,
            readonly=False,
            default_type=np.float,
            unit="ms",
            min_value=1,
            decimals=1,
        )
        self.create_attribute(
            ATTR_FRAME_IMAGE, default_value=0, readonly=True, default_type=np.uint64
        )
        self.create_attribute(ATTR_FRAME_NAME, default_value="Frame", readonly=False)
        self.create_attribute(ATTR_FRAME_FILE, default_value=0, readonly=True)
        self.create_attribute(
            ATTR_SUMMED_FRAMES,
            default_value=0,
            readonly=False,
            default_type=np.uint64,
            min_value=1,
        )
        self.create_attribute(
            ATTR_ACQUIRED_FRAMES, default_value=0, readonly=True, default_type=np.uint64
        )
        self.create_attribute(
            ATTR_WIDTH, default_value=1024, unit="px", default_type=np.uint64
        )
        self.create_attribute(
            ATTR_HEIGHT, default_value=1024, unit="px", default_type=np.uint64
        )
        npa = np.zeros(dtype=np.uint8, shape=(1024, 1024))
        self.create_attribute(
            "Frame",
            group="Output",
            default_value=npa,
            default_type=TYPE_ARRAY,
            unit="",
            readonly=True,
            display=IMAGE,
            min_broadcast_timeout=100,
        )

    @expose_method()
    def stop(self):
        self.acquisition_running.clear()

    def _generate_frame(self):
        width, height = self.get_value(ATTR_WIDTH), self.get_value(ATTR_HEIGHT)
        frame = np.random.randint(0, 255, dtype=np.uint8, size=(width, height))
        wh, hh = int(width / 2), int(height / 2)
        rw = randint(10, 100)
        frame[:25, :height] = 0
        frame[:width, :25] = 0
        frame[width - 25 :, :height] = 0
        frame[:width, height - 25 :] = 0
        frame[wh - rw : wh + rw, hh - rw : hh + rw] = 0
        return frame

    @expose_method(
        {
            "Name": ATTR_FRAME_NAME,
            "Frames": ATTR_SUMMED_FRAMES,
            "Exposure": ATTR_EXPOSURE_TIME,
        }
    )
    def start_acquisition(self, Name, Frames, Exposure):
        if self.acquisition_running.isSet():
            raise DeviceError("Another acquisition is already running")
        self.acquisition_running.set()
        Frames = device_units(self, ATTR_SUMMED_FRAMES, Frames)
        Exposure = device_units(self, ATTR_EXPOSURE_TIME, Exposure)

        self.set_status(STATUS_BUSY)
        self.set_value(ATTR_FRAME_NAME, Name)
        self.set_value(ATTR_SUMMED_FRAMES, Frames)
        self.set_value(ATTR_EXPOSURE_TIME, Exposure)
        self.set_value(ATTR_ACQUIRED_FRAMES, 0)

        def _acquire():
            exposure_time_increment = 10
            current_exposure_time = 0
            last_frame_number = 0
            while self.acquisition_running.isSet():
                time.sleep(exposure_time_increment * 1e-3)
                current_exposure_time += exposure_time_increment
                acquired_frames = int(current_exposure_time / Exposure.m)
                if last_frame_number != acquired_frames:
                    self.set_value(["Output", "Frame"], self._generate_frame())
                    last_frame_number = acquired_frames

                if acquired_frames >= Frames:
                    self.set_value(ATTR_ACQUIRED_FRAMES, Frames)
                    break
                else:
                    self.set_value(ATTR_ACQUIRED_FRAMES, acquired_frames)

            if self.connected:
                self.acquisition_running.clear()
                self.set_status(STATUS_IDLE)

        Thread(target=_acquire).start()
