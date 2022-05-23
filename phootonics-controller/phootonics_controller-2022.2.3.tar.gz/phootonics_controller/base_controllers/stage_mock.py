# -*- coding: utf-8 -*-
"""
Created by gregory on 16.03.16

Copyright 2016 Alpes Lasers SA, Neuchatel, Switzerland
"""

import logging
import time
import threading

from phootonics_controller.utils.vcm_resources.base_controller import BaseController, run_in_thread
from phootonics_controller.utils.vcm_resources.vcm_configuration import (configuration_dictionary, STAGE_ANGLE)

logger = logging.getLogger(__name__)
__author__ = 'gregory'
__copyright__ = "Copyright 2016, Alpes Lasers SA"



class StageBusyError(Exception):
    pass


class OutOfRangeError(Exception):
    pass


class MockStageController(BaseController):
    READY = 'READY'
    BUSY = 'BUSY'
    SWEEP = 'SWEEP'
    STEPWISE = 'STEPWISE'

    @property
    def has_two_axes(self):
        return bool(self._has_two_axes)

    @property
    def is_busy(self):
        return self._device_status is not None and (self._worker_thread and self._worker_thread.is_alive())

    def __init__(self, serial_number=None, dlp_controller=None, monitor_interval=1.0):
        super(MockStageController, self).__init__(monitor_interval=monitor_interval)

        self._serial_number = serial_number
        self._device_info = None
        self._device = None
        self._device_status = MockStageController.READY  # set to None to make the mock unresponsive
        self._busy_status = None  # is SWEEP or STEPWISE or None
        self._dlp_controller = dlp_controller
        self._sweep_data = []
        self._worker_thread = None
        self._stop_worker_event = threading.Event()
        self._has_two_axes = False

    def get_angle(self):
        if self._device_status:
            return 1
        else:
            return 'N/A'

    def get_angle_y(self):
        if self._device_status:
            return 1
        else:
            return 'N/A'

    def get_info(self):
        return self._device_info

    def stop_motion(self):
        self._stop_worker_event.set()
        self._worker_thread = None

    def set_current_angle(self, angle):
        pass

    def move_to_angle(self, angle):
        if self.is_busy:
            raise StageBusyError()
        pass

    def move_to_angle_y(self, angle_y):
        if self.is_busy:
            raise StageBusyError()
        pass

    def jog(self, step):
        if self.is_busy:
            raise StageBusyError()
        pass

    def sweep(self, start_angle, end_angle, velocity, repetitions=1, time_interval=0.05):
        if self.is_busy:
            raise StageBusyError()
        self._stop_worker_event.clear()
        self._worker_thread = self._sweep_worker(start_angle, end_angle, velocity, repetitions, time_interval)

    def get_sweep_data(self):
        return self._sweep_data

    def stepwise(self, steps, delay_s):
        if self.is_busy:
            raise StageBusyError()
        self._stop_worker_event.clear()
        self._worker_thread = self._stepwise_worker(steps, delay_s)

    @run_in_thread
    def _sweep_worker(self, start_angle, end_angle, velocity, repetitions=1, time_interval=0.05):
        try:
            self._busy_status = MockStageController.SWEEP
            self._sweep_data = []
            while repetitions == -1 or repetitions > 0:
                if self._stop_worker_event.is_set():
                    return
                time.sleep(time_interval)
                if self._stop_worker_event.is_set():
                    return
                current_sweep = [(0, 0, 0)]
                if repetitions > 0:
                    self._sweep_data.append(current_sweep)
                    print(self._sweep_data)
                    repetitions -= 1
                if self._stop_worker_event.is_set():
                    return
        finally:
            self._busy_status = None

    @run_in_thread
    def _stepwise_worker(self, steps, delay_s):
        try:
            self._busy_status = MockStageController.STEPWISE
            for step in steps:
                if self._stop_worker_event.is_set():
                    break
                logger.info(step)
                time.sleep(delay_s)
        finally:
            self._busy_status = None

    def _connected_status(self):
        if self.is_busy:
            return self._busy_status or MockStageController.BUSY
        return MockStageController.READY

    def _disconnect(self):
        self.stop_motion()

    def _connect(self):
        self._device_info = {'serial_number': 0, 'model': 0, 'hardware_type': 0,
                             'firmware_version': 0, 'notes': 0, 'hardware_version': 0,
                             'modification_state': 0, 'no_of_channels':0}


    def _check_connection(self):
        last_angle = 1
        try:
            if last_angle != 'N/A':
                pass
        except:
            # persist the last known angle if the motor connection fails.
            if last_angle != 'N/A':
                raise
        return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    controller = MockStageController()
    controller.start()


    try:
        time.sleep(2)
        controller.stepwise((1, 2, 3), 1)
        while controller.is_busy:
            print(controller.status)
            time.sleep(0.5)
    finally:
        controller.stop()

