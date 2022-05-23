# -*- coding: utf-8 -*-
"""
Created by Olga Reinauer

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'olgare'
__copyright__ = "Copyright Alpes Lasers SA"

import logging
import threading
import time
from time import sleep

from phootonics_controller.base_controllers.config import VCM_PORT, CAVITY1_INDEX, CAVITY2_INDEX, CAVITY3_INDEX, \
    CAVITY1_URL, CAVITY2_URL, CAVITY3_URL, ADC_CHANNEL, REF, configuration_dictionary, CAVITY4_URL, CAVITY4_INDEX, \
    EXT_VCM_PORT, get_scanning_wavelengths
from phootonics_controller.base_controllers.stage_mock import MockStageController
from phootonics_controller.base_controllers.xc_controller import ECController, MockECController
from phootonics_controller.base_controllers.stage_vcm import VCMirrorController

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def ignore_exception(f):
    def g(*args, **kargs):
        try:
            return f(*args, **kargs)
        except Exception as e:
            logger.exception(e)

    return g


class ADCDevice:

    def __init__(self):
        from phootonics_controller.utils.ADC_converter import ADS1263
        self._adc = ADS1263.ADS1263()

    def initialise(self):
        if self._adc.ADS1263_init() == -1:
            pass

    def read(self):
        try:
            adc_value = self._adc.ADS1263_GetAll()
            if adc_value[ADC_CHANNEL] >> 31 == 1:
                value = REF * 2 - adc_value[ADC_CHANNEL] * REF / 0x80000000
            else:
                value = adc_value[ADC_CHANNEL] * REF / 0x7fffffff  # 32bit
            return value
        except Exception as e:
            logger.error('could not read ADC value {}'.format(e))
            self._adc.ADS1263_Exit()


class MockADCDevice:

    def initialise(self):
        pass

    def read(self):
        return 0.2


class ScanCommand:

    def __init__(self, controller, wavelegths, positions):
        self._controller = controller
        self.wavelengths = wavelegths
        self.positions = positions
        self.results = {}
        self.stopped = threading.Event()
        self.currentX = None
        self.currentY = None
        self.activeCavity = None
        self.currentWavelength = None
        self.detectorVoltage = None
        self.error = None
        self._testWithMocks = True

    def execute(self):
        try:
            if not self._controller.testMode or self._testWithMocks:
                self._controller.move_to_cavity_1()
                self._controller.get_active_cavity().activate_s2()
                for wavelength in self.wavelengths:
                    if self.stopped.is_set():
                        return
                    logger.info('going to wavelength {}'.format(wavelength))
                    cavity_index = self._controller.get_cavity_from_wavelength(wavelength)
                    if cavity_index is None:
                        logger.info('cannot reach wavelength {}: skip to next wavelength'.format(wavelength))
                        continue
                    logger.info('selecting cavity {}'.format(cavity_index))
                    self._controller.select_cavity(cavity_index)
                    cavity = self._controller.get_cavity_from_index(cavity_index)
                    cavity.move_to_wavelength(wavelength)
                    for posX, posY in self.positions:
                        if self.stopped.is_set():
                            return
                        self._controller.extVcm.move_to_angle_y(posY)
                        self._controller.extVcm.move_to_angle(posX)
                        currentX = self._controller.extVcm.get_angle()
                        currentY = self._controller.extVcm.get_angle_y()
                        activeCavity = self._controller.get_active_cavity_index()

                        detectorVoltage = self._controller.adc.read()
                        self.results['active_cavity'].append(activeCavity)
                        self.results['x_set_point'].append(posX)
                        self.results['x'].append(currentX)
                        self.results['y_set_point'].append(posY)
                        self.results['y'].append(currentY)
                        self.results['wavelength_set_point'].append(wavelength)
                        self.results['wavelength'].append(cavity.get_wavelength())
                        self.results['detector_voltage'].append(detectorVoltage)

            else:
                if not self.stopped.wait(2.0):
                    self.results = {'active_cavity': [1, 1, 2, 2, 3, 3, 4, 4],
                                    'x_set_point': [0, 1, 0, 1, 0, 1, 0, 1],
                                    'x': [0.2, 1.2, 0.2, 1.2, 0.2, 1.2, 0.2, 1.2],
                                    'y_set_point': [0, 1, 0, 1, 0, 1, 0, 1],
                                    'y': [0.23, 1.23, 0.23, 1.23, 0.23, 1.23, 0.23, 1.23],
                                    'wavelength_set_point': [1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307],
                                    'wavelength': [1300.2, 1301.1, 1302.4, 1303.3, 1304.2, 1305.6, 1306.2, 1307.1],
                                    'detector_voltage': [0.2, 0.5, 0.3, 0.11, 0.2, 0.5, 0.3, 0.11]}

        except Exception as e:
            self.error = str(e)

    def stop(self):
        self.stopped.set()

    def to_dict(self):
        return {'runtime': {'active_cavity': self.activeCavity,
                            'current_X': self.currentX,
                            'current_y': self.currentY,
                            'error': self.error,
                            'detector_voltage': self.detectorVoltage},
                'results': self.results}


class AlreadyScanningException(Exception):
    pass


class MainController:
    RESPONDING = 'RESPONDING'
    NOT_RESPONDING = 'NOT_RESPONDING'
    READY = 'READY'
    NOT_READY = 'NOT_READY'

    def __init__(self, loop_delay=0.005, test_mode=False):
        self._scanCommand = None
        self._scanCommandThread = None
        self.testMode = test_mode
        if not self.testMode:
            self.vcm = VCMirrorController(VCM_PORT)
            self.extVcm = VCMirrorController(EXT_VCM_PORT)
            self.adc = ADCDevice()
            self.ec1 = ECController(ec_url=CAVITY1_URL, monitor_interval=0.3, index=CAVITY1_INDEX)
            self.ec2 = ECController(ec_url=CAVITY2_URL, monitor_interval=0.3, index=CAVITY2_INDEX)
            self.ec3 = ECController(ec_url=CAVITY3_URL, monitor_interval=0.3, index=CAVITY3_INDEX)
            self.ec4 = ECController(ec_url=CAVITY4_URL, monitor_interval=0.3, index=CAVITY4_INDEX)
        else:
            self.vcm = MockStageController()
            self.extVcm = MockStageController()
            self.adc = MockADCDevice()
            self.ec1 = MockECController(monitor_interval=0.3, index=CAVITY1_INDEX)
            self.ec2 = MockECController(monitor_interval=0.3, index=CAVITY2_INDEX)
            self.ec3 = MockECController(monitor_interval=0.3, index=CAVITY3_INDEX)
            self.ec4 = MockECController(monitor_interval=0.3, index=CAVITY4_INDEX)
        self._active_cavity = None
        self._monitoring_data = {}
        self._recorded_data = {}
        self._monitoring_thread = None
        self._stop_monitoring_event = threading.Event()
        self._condition_thread = None
        self._stop_condition_event = threading.Event()
        self._monitoring_loop_delay = loop_delay
        self._condition_loop_delay = 0.5
        self._system_connection_status = None
        self._system_ready_status = None
        self._system_active_cavity = None
        self._ec1_connection_status = None
        self._ec1_ready_status = None
        self._ec2_connection_status = None
        self._ec2_ready_status = None
        self._ec3_connection_status = None
        self._ec3_ready_status = None
        self._ec4_connection_status = None
        self._ec4_ready_status = None
        self._vcm_status = None
        self._extVcm_status = None

    def get_cavity_from_wavelength(self, wavelength):
        for key, item in configuration_dictionary.items():
            if item['wavelength'][0] <= wavelength <= item['wavelength'][1]:
                return key
        return None

    def get_results(self):
        if self._scanCommand:
            return self._scanCommand.to_dict()

    def start_scan(self, wavelengths=None, positions=None):
        if self._scanCommandThread:
            if self._scanCommandThread.is_alive():
                raise AlreadyScanningException
            self._scanCommandThread = None
        self._scanCommand = ScanCommand(controller=self,
                                        wavelegths=wavelengths or get_scanning_wavelengths(),
                                        positions=positions)
        self._scanCommandThread = threading.Thread(target=self._scanCommand.execute)
        self._scanCommandThread.start()

    def is_scan_command_running(self):
        if not self._scanCommandThread:
            return False
        return self._scanCommandThread.is_alive()

    def stop_scan(self):
        if self._scanCommand:
            self._scanCommand.stop()

    def start(self):
        try:
            logging.info('Initialization started, can take a few seconds')
            self.ec1.start()
            logging.info('Cavity 1 initialized')
            self.ec2.start()
            logging.info('Cavity 2 initialized')
            self.ec3.start()
            logging.info('Cavity 3 initialized')
            self.ec4.start()
            logging.info('Cavity 4 initialized')
            self.vcm.start()
            self.extVcm.start()
            logging.info('cavities initialized')
            self.adc.initialise()
            logging.info('system initialized')
            self.monitor()
        except Exception as e:
            logging.error('Could not start external cavity controllers {}'.format(e))
            self.shutdown_all_systems()

    def get_connection_status(self):
        if self._ec1_connection_status == 'RESPONDING' and self._ec2_connection_status == 'RESPONDING' and \
                self._ec3_connection_status == 'RESPONDING' and \
                self._vcm_status not in [None, 'DISCONNECTED', 'CONNECTION_ERROR'] and \
                self._extVcm_status not in [None, 'DISCONNECTED', 'CONNECTION_ERROR'] and \
                self._ec4_connection_status == 'RESPONDING':
            return MainController.RESPONDING
        else:
            return MainController.NOT_RESPONDING

    def is_ready_to_action(self):
        if self._ec1_ready_status == 'READY' and self._ec2_ready_status == 'READY' and \
                self._ec3_ready_status == 'READY' and \
                self._vcm_status == 'READY' and \
                self._extVcm_status == 'READY' and \
                self._ec4_ready_status == 'READY':
            return MainController.READY
        else:
            return MainController.NOT_READY

    def shutdown_all_systems(self, reset=False):
        try:
            self.stop_monitoring()
            if reset:
                self.ec1.shutdown()
                self.ec2.shutdown()
                self.ec3.shutdown()
                self.ec4.shutdown()
            else:
                self.ec1.stop_pulsing()
                self.ec2.stop_pulsing()
                self.ec3.stop_pulsing()
                self.ec4.stop_pulsing()
            self.vcm.stop()
            self.extVcm.stop()
        except Exception as e:
            logging.error('error on shutdown {}'.format(e))

    def get_active_cavity_index(self):
        return self._active_cavity

    def get_active_cavity(self):
        return self.get_cavity_from_index(self._active_cavity)

    def get_cavity_from_index(self, cavity_index):
        if cavity_index == CAVITY1_INDEX:
            return self.ec1
        elif cavity_index == CAVITY2_INDEX:
            return self.ec2
        elif cavity_index == CAVITY3_INDEX:
            return self.ec3
        elif cavity_index == CAVITY4_INDEX:
            return self.ec4

    def stop_monitoring(self):
        self._stop_monitoring_event.set()
        self._monitoring_thread.join(1.0)

    def monitor(self):
        self._stop_monitoring_event.clear()
        self._monitoring_thread = threading.Thread(target=self._monitoring_worker)
        self._monitoring_thread.start()

    def get_monitoring_data(self):
        return self._monitoring_data

    def _monitoring_worker(self):
        first_time = time.time()
        ec1_monitoring_trace = None
        ec2_monitoring_trace = None
        ec3_monitoring_trace = None
        ec4_monitoring_trace = None
        t = None
        while self._stop_monitoring_event.wait(self._monitoring_loop_delay) is False:
            if not self._stop_monitoring_event.is_set():
                device_time = time.time()
                t = int(device_time - first_time)
                self._system_connection_status = ignore_exception(self.get_connection_status)()
                self._system_ready_status = ignore_exception(self.is_ready_to_action)()
                self._system_active_cavity = ignore_exception(self.get_active_cavity_index)()
                self._ec1_connection_status = self.ec1.status
                self._ec1_ready_status = ignore_exception(self.ec1.xc_ready_to_action)()
                self._ec2_connection_status = self.ec2.status
                self._ec2_ready_status = ignore_exception(self.ec2.xc_ready_to_action)()
                self._ec3_connection_status = self.ec2.status
                self._ec3_ready_status = ignore_exception(self.ec2.xc_ready_to_action)()
                self._ec4_connection_status = self.ec2.status
                self._ec4_ready_status = ignore_exception(self.ec2.xc_ready_to_action)()
                self._vcm_status = self.vcm.status
                self._extVcm_status = self.extVcm.status
                ec1_monitoring_trace = ignore_exception(self.ec1.system_info)()['response']['data']
                ec2_monitoring_trace = ignore_exception(self.ec2.system_info)()['response']['data']
                ec3_monitoring_trace = ignore_exception(self.ec3.system_info)()['response']['data']
                ec4_monitoring_trace = ignore_exception(self.ec4.system_info)()['response']['data']
            self._monitoring_data = {'t': t,
                                     'active_cavity': self._system_active_cavity,
                                     'system_ready_status': self._system_ready_status,
                                     'system_connection_status': self._system_connection_status,
                                     'ec1_connection': self._ec1_connection_status,
                                     'ec2_connection': self._ec2_connection_status,
                                     'ec3_connection': self._ec3_connection_status,
                                     'ec4_connection': self._ec4_connection_status,
                                     'ec1_ready': self._ec1_ready_status,
                                     'ec2_ready': self._ec2_ready_status,
                                     'ec3_ready': self._ec3_ready_status,
                                     'ec4_ready': self._ec4_ready_status,
                                     'ec1_trace': ec1_monitoring_trace,
                                     'ec2_trace': ec2_monitoring_trace,
                                     'ec3_trace': ec3_monitoring_trace,
                                     'ec4_trace': ec4_monitoring_trace,
                                     'vcm_status': self._vcm_status,
                                     'extVcm_status': self._extVcm_status
                                     }

    def select_cavity(self, cavity_index):
        if self._system_connection_status == MainController.RESPONDING:
            if self._active_cavity != cavity_index:
                logger.info('switching to cavity {}'.format(cavity_index))
                self._switch_and_activate_cavity(cavity_index, configuration_dictionary[cavity_index]['x_position'],
                                                 configuration_dictionary[cavity_index]['y_position'])
        else:
            raise Exception('Controller not responding')

    def _switch_and_activate_cavity(self, cavity_index, cavity_position_x, cavity_position_y):
        try:
            cavity = self.get_cavity_from_index(cavity_index)
            logger.info('active cavity stops pulsing {}'.format(self.get_active_cavity_index()))
            self.get_active_cavity().stop_pulsing()
            time.sleep(1)
            self._active_cavity = None
            logger.info('moving to position {} {}'.format(cavity_position_x, cavity_position_y))
            logger.info('VCM status {}'.format(self.vcm.status))
            self.vcm.move_to_angle(cavity_position_x)
            self.vcm.move_to_angle_y(cavity_position_y)
            time.sleep(1)
            cavity.activate_s2()
            time.sleep(1)
            self._active_cavity = cavity_index
        except Exception as e:
            logging.error('Could not move to cavity {} at position {} {}, error {}'.format(cavity_index,
                                                                                           cavity_position_x,
                                                                                           cavity_position_y, e))

    def move_to_cavity_1(self):
        try:
            self.vcm.move_to_angle(configuration_dictionary[CAVITY1_INDEX]['x_position'])
            self.vcm.move_to_angle_y(configuration_dictionary[CAVITY1_INDEX]['y_position'])
            self._active_cavity = CAVITY1_INDEX
        except Exception as e:
            logging.error('Could not move to cavity 1'.format(e))

    def get_adc_voltage(self):
        return self.adc.read()
