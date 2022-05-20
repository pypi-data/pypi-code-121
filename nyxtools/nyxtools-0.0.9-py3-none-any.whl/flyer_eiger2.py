import logging
import time as ttime

from mxtools.flyer import MXFlyer
from ophyd.status import SubscriptionStatus

logger = logging.getLogger(__name__)
DEFAULT_DATUM_DICT = {"data": None, "omega": None}


class NYXEiger2Flyer(MXFlyer):
    def __init__(self, vector, zebra, detector=None) -> None:
        super().__init__(vector, zebra, detector)
        self.name = "NYXEiger2Flyer"

    def kickoff(self):
        self.detector.stage()
        st = self.vector.move()
        return st

    def update_parameters(self, **kwargs):
        super().update_parameters(**kwargs)
        self.zebra.pc.arm_signal.put(1)
        ttime.sleep(1)

    def complete(self):
        st_vector = self.vector.track_move()

        def detector_callback(value, old_value, **kwargs):
            logger.debug(f"DETECTOR status {old_value} -> {value}")
            # if old_value == "Acquiring" and value == "Done":
            if old_value == 1 and value == 0:
                logger.debug(f"DETECTOR status successfully changed {old_value} -> {value}")
                return True
            else:
                logger.debug(f"DETECTOR status changing {old_value} -> {value}...")
                return False

        st_detector = SubscriptionStatus(self.detector.cam.acquire, detector_callback, run=True)

        return st_vector & st_detector

    def detector_arm(self, **kwargs):
        logger.debug("flyer detector arm")
        kwargs["det_distance_m"] /= 1000
        super().detector_arm(**kwargs)
        logger.debug("flyer detector arm done")

    def configure_vector(self, **kwargs):
        logger.debug("configuring vector")
        angle_start = kwargs["angle_start"]
        scan_width = kwargs["scan_width"]
        exposure_ms = kwargs["exposure_period_per_image"] * 1.0e3
        num_images = kwargs["num_images"]
        x_mm = (kwargs["x_start_um"] / 1000, kwargs["x_end_um"] / 1000)
        y_mm = (kwargs["y_start_um"] / 1000, kwargs["y_end_um"] / 1000)
        z_mm = (kwargs["z_start_um"] / 1000, kwargs["z_end_um"] / 1000)
        o = (angle_start, angle_start + scan_width)
        buffer_time_ms = 0
        shutter_lag_time_ms = 2
        shutter_time_ms = 2
        self.vector.prepare_move(
            o,
            x_mm,
            y_mm,
            z_mm,
            exposure_ms,
            num_images,
            buffer_time_ms,
            shutter_lag_time_ms,
            shutter_time_ms,
        )
        logger.debug("configure done")

    def zebra_daq_prep(self):
        self.zebra.reset.put(1)
        ttime.sleep(2.0)
        self.zebra.out1.put(31)
        self.zebra.m1_set_pos.put(1)
        self.zebra.m2_set_pos.put(1)
        self.zebra.m3_set_pos.put(1)
        self.zebra.pc.arm.trig_source.put(0)  # Soft triggering for NYX
