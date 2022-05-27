import time
from threading import Event, Thread
import numpy as np
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceGrabber(Device):
    """Here comes some description of the class DeviceGrabber."""

    def __init__(self, device_id=None, config=None):
        self.stopped = Event()
        self.frame_delay = 0
        Device.__init__(self, device_id, config)
        self.connect()

    def _init_attributes(self):
        Device._init_attributes(self)
        npa = np.zeros(dtype=np.uint8, shape=(1, 1, 3))
        self.create_attribute(
            ATTR_FRAME,
            group="Grabber",
            default_value=npa,
            default_type=TYPE_ARRAY,
            unit="",
            readonly=True,
            display=IMAGE,
            min_broadcast_timeout=100,
        )
        self.create_attribute(
            ATTR_MAX_BROADCAST_RATE,
            default_value=10,
            default_type=np.uint8,
            unit="Hz",
            min_value=0,
            max_value=10000,
            set_function=self.set_max_broadcast_rate,
        )
        self.create_attribute(
            ATTR_FRAMERATE,
            default_value=10,
            default_type=np.float,
            unit="FPS",
            min_value=1,
            max_value=10000,
            set_function=self.set_framerate,
            decimals=2,
        )
        self.create_attribute(
            ATTR_FRAMES_GRABBED, default_value=0, default_type=np.uint, readonly=True
        )

    @expose_method()
    def acquire(self):
        if self.get_value(ATTR_STATUS) == STATUS_BUSY:
            return
        Thread(target=self._acquire_loop).start()

    def _acquire_loop(self):
        """
        Here comes a short description about _acquire_loop.

        self.stopped.clear()
        self.frame_delay = 1. / self.get_value(ATTR_FRAMERATE)
        self.set_status(STATUS_BUSY)

        fps_counter_reference = time_reference = time.perf_counter_ns()
        grabbed_frames_count = 0
        fps_counter = 0
        while not self.stopped.wait((self.frame_delay - (time.perf_counter_ns() - time_reference)) * 1e-9):
            time_reference = time.perf_counter_ns()
            grab_frame_method
            grabbed_frames_count += 1
            fps_counter += 1
            if ret:
                self.set_value(["Grabber", "Frame"], cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

            if (time.perf_counter_ns() - fps_counter_reference) >= 1e9:
                self.set_raw_value(ATTR_FRAMERATE, fps_counter)
                self.set_raw_value(ATTR_FRAMES_GRABBED, grabbed_frames_count)
                fps_counter = 0
                fps_counter_reference = time.perf_counter_ns()
        """
        raise NotImplementedError

    def set_max_broadcast_rate(self, value):
        self[ATTR_OUTPUT][ATTR_FRAME][ALLOW_BROADCAST] = value > 0
        if value > 0:
            self[ATTR_OUTPUT][ATTR_FRAME].min_broadcast_timeout = (1e9 / value) * 0.95

    def set_framerate(self, value):
        self.frame_delay = 1e9 / value

    def handle_configuration(self):
        start_at = time.time()
        self._config_attributes()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    @expose_method()
    def stop(self):
        self.stopped.set()
        self.set_status(STATUS_IDLE)

    def close(self):
        self.stop()
        Device.close(self)
