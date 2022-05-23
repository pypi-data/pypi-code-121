# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

from argparse import ArgumentParser
import logging
from time import sleep

from phootonics_controller.base_controllers.config import CAVITY1_URL, CAVITY1_INDEX, CAVITY2_URL, CAVITY3_URL, \
    CAVITY2_INDEX, CAVITY3_INDEX
from phootonics_controller.base_controllers.main_controller import MainController, read_adc_detector
from phootonics_controller.base_controllers.xc_controller import ECController

import pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


SHUTDOWN = False


def scan():
    parser = ArgumentParser()
    parser.add_argument('-wl', nargs='+', type=float)
    parser.add_argument('-x', nargs='+', type=float)
    parser.add_argument('-y', nargs='+', type=float)
    parser.add_argument('--keepalive', action='store_true', default=False)
    args=parser.parse_args()
    keepalive = args.keepalive
    wl_list = args.wl
    x_list = args.x
    y_list = args.y
    controller = MainController()
    controller.start()
    results = {'active_cavity': [],
               'x_set_point': [],
               'x': [],
               'y_set_point': [],
               'y': [],
               'wavelength_set_point': [],
               'wavelength': [],
               'detector_voltage': []}
    try:
        while True:
            status = controller.get_connection_status()
            logger.info('Phootonics controller status: {}'.format(status))
            if status == MainController.RESPONDING:
                break
            sleep(0.1)
        while True:
            logger.info('Waiting is_ready_for_action')
            if controller.is_ready_to_action():
                break
            sleep(0.1)
        logger.info('Phootonics controller initialized')
        logger.info('Monitoring data {}'.format(controller.get_monitoring_data()))
        logger.info('scanning wavelengths: {}, x positions: {}, y positions: {}'.format(wl_list, x_list, y_list))

        controller.move_to_cavity_1()
        controller.get_active_cavity().activate_s2()
        for wavelength in wl_list:
            logger.info('going to wavelength {}'.format(wavelength))
            cavity_index = controller.get_cavity_from_wavelength(wavelength)
            logger.info('selecting cavity {}'.format(cavity_index))
            controller.select_cavity(cavity_index)
            cavity = controller.get_cavity_from_index(cavity_index)
            cavity.move_to_wavelength(wavelength)
            for posY in y_list:
                controller.vcm.move_to_angle_y(cavity.get_absolute_position_y(posY))
                sleep(0.1)
                for posX in x_list:
                    controller.vcm.move_to_angle(cavity.get_absolute_position(posX))
                    sleep(0.1)
                    currentX = controller.vcm.get_angle()
                    currentY = controller.vcm.get_angle_y()
                    activeCavity = controller.get_active_cavity_index()

                    detectorVoltage = read_adc_detector()
                    results['active_cavity'].append(activeCavity)
                    results['x_set_point'].append(posX)
                    results['x'].append(cavity.get_rel_position(currentX))
                    results['y_set_point'].append(posY)
                    results['y'].append(cavity.get_rel_position_y(currentY))
                    results['wavelength_set_point'].append(wavelength)
                    results['wavelength'].append(cavity.get_wavelength())
                    results['detector_voltage'].append(detectorVoltage)

        df = pandas.DataFrame.from_records(results)
        df.to_csv('outputfile.csv')

    finally:
        if not keepalive:
            controller.shutdown_all_systems(reset=False)



