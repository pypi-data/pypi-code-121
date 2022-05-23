# -*- coding: utf-8 -*-
"""
Created by gregory on 16.03.16

Copyright 2016 Alpes Lasers SA, Neuchatel, Switzerland
"""

import logging
import time
import threading

from .vcm_configuration import (configuration_dictionary, STAGE_ANGLE, update_configuration, MAXIMUM_STAGE_VELOCITY,
                                                         get_wavelength_for_angle)
from motor_apt.core2.cr1 import CR1

from .base_controller import BaseController, run_in_thread
from .dlp import DLPController

logger = logging.getLogger(__name__)
__author__ = 'gregory'
__copyright__ = "Copyright 2016, Alpes Lasers SA"


class StageBusyError(Exception):
    pass


class OutOfRangeError(Exception):
    pass


class StageController(BaseController):
    READY = 'READY'
    BUSY = 'BUSY'
    SWEEP = 'SWEEP'
    STEPWISE = 'STEPWISE'

    @property
    def has_two_axes(self):
        return bool(self._has_two_axes)

    @property
    def is_busy(self):
        return self._device is not None and self._device_status is not None and (self._device_status.moving or
                                                                                 self._device_status.homing or
                                             (self._worker_thread and self._worker_thread.is_alive()))

    def __init__(self, serial_number=None, dlp_controller=None, monitor_interval=1.0):
        super(StageController, self).__init__(monitor_interval=monitor_interval)

        self._serial_number = serial_number
        self._device_info = None
        self._device_status = None
        self._busy_status = None  # is SWEEP or STEPWISE or None
        self._device = None
        self._dlp_controller = dlp_controller

        self._sweep_data = []
        self._worker_thread = None
        self._stop_worker_event = threading.Event()
        self._has_two_axes = False

    def get_angle(self):
        if self._device_status:
            return self._device_status.position
        else:
            return 'N/A'

    def get_info(self):
        return self._device_info

    def stop_motion(self):
        self._stop_worker_event.set()
        self._worker_thread = None
        self._device.stop(wait=True, immediate=True)

    def set_current_angle(self, angle):
        update_configuration({STAGE_ANGLE: angle})
        self._device.set_encoder_counter(int(self._device.enccnt * angle))

    def move_to_angle(self, angle):
        if self.is_busy:
            raise StageBusyError()
        self._device.move_absolute(angle, wait=False)

    def jog(self, step):
        if self.is_busy:
            raise StageBusyError()
        jog_mode, step_size, min_vel, acc, max_vel, stop_mode = self._device.jog_parameters()
        if acc > self._device.max_acceleration:
            acc = self._device.max_acceleration
        if max_vel > self._device.max_velocity:
            max_vel = self._device.max_velocity
        self._device.set_jog_parameters(jog_mode=jog_mode, step_size=abs(step), acceleration=acc, max_velocity=max_vel,
                                        stop_mode=stop_mode)
        self._device.jog(direction=2 if step > 0 else 1, wait=False)

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
        min_vel, acc, max_vel = self._device.velocity_parameters()
        if acc > self._device.max_acceleration:
            acc = self._device.max_acceleration
        max_vel = self._device.max_velocity
        try:
            self._busy_status = StageController.SWEEP
            self._sweep_data = []
            while repetitions == -1 or repetitions > 0:
                self._device.set_velocity_parameters(acc, max_vel)
                self.__notify_ramping(False, True)
                self._device.move_absolute(start_angle, wait=True)
                if self._stop_worker_event.is_set():
                    return
                self._device.set_velocity_parameters(acc, velocity)

                start_time = time.time()
                status = self._device.status()
                current_sweep = [(0, status.position, get_wavelength_for_angle(status.position, False))]
                self._device.move_absolute(end_angle, wait=False)
                self.__notify_ramping(True, False)
                moving = True
                while moving:
                    time.sleep(time_interval)
                    if self._stop_worker_event.is_set():
                        return
                    status = self._device.status()
                    moving = status.moving
                    logger.debug('Current position: {}'.format(status.position))
                    current_sweep.append((time.time() - start_time, status.position,
                                          get_wavelength_for_angle(status.position, False)))
                self.__notify_ramping(False, False)
                if repetitions > 0:
                    self._sweep_data.append(current_sweep)
                    repetitions -= 1
                else:
                    self._sweep_data = [current_sweep]
                if self._stop_worker_event.is_set():
                    return
        finally:
            self.__notify_ramping(False, False)
            self._device.set_velocity_parameters(acc, max_vel)
            self._busy_status = None

    def __notify_ramping(self, is_ramping_forward, is_ramping_backwards):
        if self._dlp_controller and self._dlp_controller.status == DLPController.READY:
            self._dlp_controller.set_channel(1, is_ramping_forward)
            self._dlp_controller.set_channel(2, is_ramping_backwards)

    @run_in_thread
    def _stepwise_worker(self, steps, delay_s):
        try:
            self._busy_status = StageController.STEPWISE
            for step in steps:
                if self._stop_worker_event.is_set():
                    break
                self._device.move_absolute(step, wait=True)
                time.sleep(delay_s)
        finally:
            self._busy_status = None

    def _connected_status(self):
        if self.is_busy:
            return self._busy_status or StageController.BUSY
        return StageController.READY

    def _disconnect(self):
        last_angle = self.get_angle()
        if last_angle != 'N/A':
            update_configuration({STAGE_ANGLE: last_angle})
        try:
            self.stop_motion()
            self._device_info = None
        finally:
            try:
                self._device.close()
            except:
                pass
            self._device = None

    def _connect(self):
        try:
            self._device = CR1(self._serial_number)
            self._device.open()
            self.set_current_angle(configuration_dictionary[STAGE_ANGLE])
            self._device.set_velocity_parameters(self._device.max_acceleration, configuration_dictionary[MAXIMUM_STAGE_VELOCITY])
        except:
            raise Exception('Cannot connect.')
        serial_number, model, hwtype, fwver, notes, hwver, modstate, numchan = self._device.info()
        self._device_info = {'serial_number': serial_number, 'model': model, 'hardware_type': hwtype,
                             'firmware_version': fwver, 'notes': notes, 'hardware_version': hwver,
                             'modification_state': modstate, 'no_of_channels': numchan}

    def _check_connection(self):
        last_angle = self.get_angle()
        try:
            self._device_status = self._device.status()
            if last_angle != 'N/A':
                update_configuration({STAGE_ANGLE: last_angle})
        except:
            # persist the last known angle if the motor connection fails.
            if last_angle != 'N/A':
                update_configuration({STAGE_ANGLE: last_angle})
            raise
        return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.DEBUG)
    controller = StageController()
    controller.start()
    try:
        time.sleep(2)
        controller.sweep(0, 2, 2, 2, 0.05)
        while controller.is_busy:
            time.sleep(0.5)
        print(controller.get_sweep_data())
    finally:
        controller.stop()
