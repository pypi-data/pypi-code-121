# -*- coding: utf-8 -*-
import logging
import time
import math
import threading
from argparse import ArgumentParser

from phootonics_controller.utils.MR_E_2_Python_SDK.optoMDC.mre2 import MRE2Board
from phootonics_controller.utils.vcm_resources.base_controller import run_in_thread
from phootonics_controller.utils.vcm_resources.vcm_configuration import (configuration_dictionary, STAGE_ANGLE, update_configuration,
                                                         get_wavelength_for_angle)
from phootonics_controller.utils.vcm_resources.stage import StageBusyError, OutOfRangeError, StageController

logger = logging.getLogger(__name__)


def convert_x_position_to_angles_deg(pos):
    tan_50 = math.tan(math.radians(50))
    angle = (math.degrees(math.atan(pos * tan_50)))/2
    return angle


def convert_angles_deg_to_position_x(angle):
    tan_50 = math.tan(math.radians(50))
    pos = math.tan(math.radians(angle*2)) / tan_50
    return pos


class VCMirrorController(StageController):

    SIN = 0
    TRIANG = 1
    RECT = 2
    SAW = 3

    @property
    def is_busy(self):
        return self._device is not None and (self._busy_status not in [None, 'None', ''])

    def __init__(self, port):
        super(VCMirrorController, self).__init__(monitor_interval=0.1)
        self._port = port
        self._device_info = None
        self._busy_status = None
        self.filename = 'point_cloud.txt'
        self._device = None
        self._sweep_data = []
        self._stop_worker_event = threading.Event()
        self._has_two_axes = True

    def get_angle(self):
        return self._device.get_position()

    def get_angle_y(self):
        return self._device.get_position_y()

    def stop_motion(self):
        self._stop_worker_event.set()
        self._worker_thread = None

    def set_current_angle(self, angle):
        pass  # no-op for stages with homing capabilities

    def move_to_angle(self, angle):
        if self.is_busy:
            raise StageBusyError()
        self._device.move_abs(angle)

    def move_to_angle_y(self, angle_y):
        if self.is_busy:
            raise StageBusyError()
        self._device.move_y_axis_abs(angle_y)

    def jog(self, step):
        if self.is_busy:
            raise StageBusyError()
        self._device.set_step_size(abs(step))
        if step > 0:
            self._device.step_forward()
        else:
            self._device.step_backward()

    def sweep(self, amplitude, frequency, offset, shape):
        if self.is_busy:
            raise StageBusyError()
        self._stop_worker_event.clear()
        self._worker_thread = self._sweep_worker(amplitude, frequency, offset, shape)

    def stepwise(self, steps, delay_s):
        if self.is_busy:
            raise StageBusyError()
        self._stop_worker_event.clear()
        self._worker_thread = self._stepwise_worker(steps, delay_s)

    def convert_to_motiontrack(self, motion_track):
        conv_position = [(x[0], convert_x_position_to_angles_deg(x[1])) for x in motion_track]
        return [(x[0],x[1], get_wavelength_for_angle(x[1], False)) for x in conv_position]

    @run_in_thread
    def _sweep_worker(self, amplitude, frequency, offset, shape):
        self._sweep_data = []
        try:
            self._device.start_motion_track()
            self._busy_status = VCMirrorController.SWEEP
            self._device.set_signal_generator_parameters(amplitude, frequency, offset, shape)
            self._device.start_signal_generator()
            while not self._stop_worker_event.wait(1):
                gen_status = self._device.get_generator_status()
                if self._stop_worker_event.is_set():
                    self._device.stop_signal_generator()
                    break
                if gen_status == 0:
                    self._device.stop_signal_generator()
                    break
        except Exception as e:
            logger.error('Sweep error {}'.format(e))
            raise
        finally:
            self._device.stop_motion_track()
            self._device.stop_signal_generator()
        current_sweep = self.convert_to_motiontrack(self._device.get_motion_track())
        self._sweep_data = [current_sweep]
        self._busy_status = None

    @run_in_thread
    def _stepwise_worker(self, steps, delay_s):
        try:
            self._device.start_motion_track()
            self._busy_status = VCMirrorController.STEPWISE
            for step in steps:
                if self._stop_worker_event.is_set():
                    break
                self._device.move_abs(step)
                time.sleep(delay_s)
        finally:
            self._device.stop_motion_track()
        current_step = self.convert_to_motiontrack(self._device.get_motion_track())
        self._sweep_data = [current_step]
        self._busy_status = None

    def _connected_status(self):
        if self.is_busy:
            return self._busy_status or VCMirrorController.BUSY
        return VCMirrorController.READY

    def _disconnect(self):
        try:
            self.stop_motion()
        finally:
            try:
                self._device.close()
            except Exception as e:
                logger.info('_disconnect error {}'.format(e), exc_info=1)
                self._device = None

    def _connect(self):
        self._device = VCMirror(self._port)
        self._device.open()
        self._device_info = {'serial_number': self._device.serial_number, 'model': 'MR-E-2',
                             'firmware_version': self._device.sw_verison}

    def _check_connection(self):
        if self._device:
            last_angle = self.get_angle()
            if last_angle is not None:
                if last_angle != 'N/A':
                    update_configuration({STAGE_ANGLE: last_angle})
            return self._device.check_connection()
        else:
            logger.error('self._device of VCMirrorController is None')
            return False


class VCMirror:

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def sw_verison(self):
        return self._sw_version

    def __init__(self, port, loop_delay=0.001):
        self.data_lock = threading.RLock()
        self.stopEvent = threading.Event()
        self.thread = None
        self._serial_number = ''
        self._sw_version = ''
        self._port = port
        self.device = None
        self.loop_delay = loop_delay
        self._position = None
        self._position_y = None
        self._temperature = None
        self._last_recording = None
        self._step_size = 0.2
        self.sig_gen_params_valid = False
        self._is_connected = False
        self._motion_track = None
        self._is_recording = False

    def connection_ok(self):
        self._is_connected = True

    def connection_ko(self):
        self._is_connected = False

    def start_motion_track(self):
        with self.data_lock:
            self._motion_track = []
            self._is_recording = True

    def stop_motion_track(self):
        self._is_recording = False

    def get_motion_track(self):
        return self._motion_track

    def _record_motion(self):
        if self._is_recording:
            self._motion_track.append((self._last_recording,
                                       self._position))

    def _home(self):
        with self.data_lock:
            self.device.Mirror.Channel_0.StaticInput.SetXY(0.0)
            self.device.Mirror.Channel_1.StaticInput.SetXY(0.0)

    def _set_xy_control_mode_both_axes(self):
        with self.data_lock:
            current_control_mode_x = self.device.Mirror.Channel_0.GetControlMode()
            if current_control_mode_x != 2:
                self.device.Mirror.Channel_0.SetControlMode(2)
            current_control_mode_y = self.device.Mirror.Channel_1.GetControlMode()
            if current_control_mode_y != 2:
                self.device.Mirror.Channel_1.SetControlMode(2)

    def _init(self):
        self._set_xy_control_mode_both_axes()
        self._home()
        self.move_y_axis_abs(configuration_dictionary['STAGE_ANGLE_Y'])
        with self.data_lock:
            self._serial_number = self.device.Status.get_register('cpu_fpga_version')[0]
            self._sw_version = self.device.Status.get_register('firmware_id')[0]

    def open(self):
        if not self.device:
            self.device = MRE2Board(port=self._port, verbose=True)
        self._init()
        self.connection_ok()
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def close(self):
        try:
            self.stopEvent.set()
            self.thread.join(2)
            if self.thread.isAlive():
                logger.error('stage vcm _run thread is still alive on close')
            self.device.disconnect()
        finally:
            self.thread = None
            self.device = None
            self.connection_ko()

    def check_connection(self):
        if not self.thread or (not self.thread.isAlive()):
            return False
        return self._is_connected

    def _run(self):
        while self.stopEvent.wait(self.loop_delay) is False:
            if self.stopEvent.is_set():
                return
            try:
                with self.data_lock:
                    pos_x_cal = self.device.Mirror.OpticalFeedback.get_register('x')[0]
                    pos_y_cal = self.device.Mirror.OpticalFeedback.get_register('y')[0]
                    pos_angle = convert_x_position_to_angles_deg(pos_x_cal)
                    pos_angle_y = convert_x_position_to_angles_deg(pos_y_cal)
                    self._position = pos_angle
                    self._position_y = pos_angle_y
                    self._temperature = self.device.TemperatureManager.GetProxyTemperature()[0]
                    self._last_recording = time.time()
                    self._record_motion()
            except Exception as e:
                logger.exception(e)
                logger.info('error communicating with VCM')
                return

    def get_position(self):
        return self._position

    def get_position_y(self):
        return self._position_y

    def move_abs(self, angle):
        with self.data_lock:
            pos = convert_angles_deg_to_position_x(angle)
            if self.angle_not_out_of_bounds(angle):
                self.device.Mirror.Channel_0.StaticInput.SetXY(pos)
            else:
                raise OutOfRangeError()

    def move_y_axis_abs(self, angle):
        with self.data_lock:
            posy = convert_angles_deg_to_position_x(angle)
            if self.angle_not_out_of_bounds(angle):
                self.device.Mirror.Channel_1.StaticInput.SetXY(posy)
            else:
                raise OutOfRangeError()

    def move_rel(self, increment):
        with self.data_lock:
            current_position_x = float(self.device.Mirror.Channel_0.StaticInput.GetXY()[0])
            current_angle_x = convert_x_position_to_angles_deg(current_position_x)
            target_angle_x = current_angle_x + increment
            target_position_x = convert_angles_deg_to_position_x(target_angle_x)
            if self.angle_not_out_of_bounds(target_angle_x):
                self.device.Mirror.Channel_0.StaticInput.SetXY(target_position_x)
            else:
                raise OutOfRangeError()

    def step_forward(self):
        self.move_rel(self._step_size)

    def step_backward(self):
        self.move_rel(self._step_size*(-1))

    def get_step_size(self):
        return self._step_size

    def set_step_size(self, step_size):
        self._step_size = abs(step_size)

    def angle_not_out_of_bounds(self, position):
        if position >-25 and position < 25 :
            return True
        else:
            return False

    def set_signal_generator_parameters(self, amplitude, frequency, offset, shape):
        with self.data_lock:
            amp = convert_angles_deg_to_position_x(amplitude)
            off = convert_angles_deg_to_position_x(offset)
            max_position = abs(amplitude) + abs(offset)
            if self.angle_not_out_of_bounds(max_position):
                self.sig_gen_params_valid = True
            else:
                self.sig_gen_params_valid = False
            if self.sig_gen_params_valid:
                self.device.Mirror.Channel_0.SignalGenerator.SetAmplitude(amp)
                self.device.Mirror.Channel_0.SignalGenerator.SetFrequency(frequency)
                self.device.Mirror.Channel_0.SignalGenerator.SetAsInput()
                self.device.Mirror.Channel_0.SignalGenerator.SetUnit(2)
                self.device.Mirror.Channel_0.SignalGenerator.SetShape(shape)
                self.device.Mirror.Channel_0.SignalGenerator.SetCycles(-1)
                self.device.Mirror.Channel_0.SignalGenerator.SetOffset(off)
            else:
                raise OutOfRangeError()

    def start_signal_generator(self):
        with self.data_lock:
            if self.sig_gen_params_valid:
                self.device.Mirror.Channel_0.SignalGenerator.Run()
            else:
                raise OutOfRangeError()

    def get_generator_status(self):
        with self.data_lock:
            gen_status= self.device.Mirror.Channel_0.SignalGenerator.GetRunningStatus()[0]
            return gen_status

    def stop_signal_generator(self):
        with self.data_lock:
            self.device.Mirror.Channel_0.SignalGenerator.Stop()
            self.set_static_input()

    def set_static_input(self):
        with self.data_lock:
            self.device.Mirror.Channel_0.StaticInput.SetAsInput()

def move():
    parser = ArgumentParser()
    parser.add_argument('position_x', type=float)
    parser.add_argument('position_y', type=float)
    parser.add_argument('-p', type=str)
    args=parser.parse_args()
    d = VCMirror(args.p)
    d.open()
    try:
        d.move_abs(args.position_x)
        d.move_y_axis_abs(args.position_y)
    finally:
        d.close()


if __name__ == '__main__':
    move()


