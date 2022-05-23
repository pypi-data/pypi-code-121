# -*- coding: utf-8 -*-
"""
Created by gregory on 18.03.16

Copyright 2016 Alpes Lasers SA, Neuchatel, Switzerland
"""
import csv
import json
import hashlib
from os import path
import logging

from .vcm_calibration import (validate_calibration,
                                                       angle_for_wavelength as _angle_for_wavelength,
                                                       wavelength_for_angle as _wavelength_for_angle)
from .vcm_calibration import (validate_calibration,
                                                       angle_for_wavelength_old as _angle_for_wavelength_old,
                                                       wavelength_for_angle_old as _wavelength_for_angle_old)
from .file_backed_dict import FileBackedDict

logger = logging.getLogger(__name__)
__author__ = 'gregory'
__copyright__ = "Copyright 2016, Alpes Lasers SA"

# Configuration keys.
DEBUG = "DEBUG"
SERVER_PORT = "SERVER_PORT"
CERTIFICATE_PATH = "CERTIFICATE_PATH"
PRIVATE_KEY_PATH = "PRIVATE_KEY_PATH"
CONFIGURATION_FILE_PATH = "CONFIGURATION_FILE_PATH"
USERS_FILE_PATH = "USERS_FILE_PATH"
CALIBRATION_FILE_PATH = "CALIBRATION_FILE_PATH"
ADMINS_FILE_PATH = "ADMINS_FILE_PATH"
PULSER_PORT = "PULSER_PORT"
STAGE_MODEL = "STAGE_MODEL"
STAGE_SERIAL_NUMBER = "STAGE_SERIAL_NUMBER"
STAGE_PORT = "STAGE_PORT"
STAGE_PROP_FACTOR = "STAGE_PROP_FACTOR"
STAGE_CONTROL_FREQUENCY = "STAGE_CONTROL_FREQUENCY"
STAGE_EXCITATION_FREQUENCY = "STAGE_EXCITATION_FREQUENCY"
STAGE_ANGLE = "STAGE_ANGLE"
STAGE_ANGLE_Y = "STAGE_ANGLE_Y"
TC_SERIAL_PORT = "TC_SERIAL_PORT"
TC_BAUDRATE = "TC_BAUDRATE"
TC_MODEL = "TC_MODEL"
PULSER_GENERATION = "PULSER_GENERATION"
PULSER_MINIMUM_VOLTAGE = "PULSER_MINIMUM_VOLTAGE"
PULSER_MAXIMUM_VOLTAGE = "PULSER_MAXIMUM_VOLTAGE"
PULSER_MAXIMUM_CURRENT = "PULSER_MAXIMUM_CURRENT"
PULSER_MINIMUM_PULSE_PERIOD = "PULSER_MINIMUM_PULSE_PERIOD"
PULSER_MAXIMUM_PULSE_PERIOD = "PULSER_MAXIMUM_PULSE_PERIOD"
PULSER_MINIMUM_PULSE_WIDTH = "PULSER_MINIMUM_PULSE_WIDTH"
PULSER_MAXIMUM_PULSE_WIDTH = "PULSER_MAXIMUM_PULSE_WIDTH"
MINIMUM_DUTY_CYCLE = "MINIMUM_DUTY_CYCLE"
MAXIMUM_DUTY_CYCLE = "MAXIMUM_DUTY_CYCLE"
MAXIMUM_MIRROR_AMPLITUDE= "MAXIMUM_MIRROR_AMPLITUDE"
BYPASS_TC_CHECK = "BYPASS_TC_CHECK"
MINIMUM_STAGE_VELOCITY = "MINIMUM_STAGE_VELOCITY"
MAXIMUM_STAGE_VELOCITY = "MAXIMUM_STAGE_VELOCITY"
ANGLE_UNITS = "ANGLE_UNITS"
WAVELENGTH_UNITS = "WAVELENGTH_UNITS"

TEC_TEMPERATURE = 'temperature'
TEC_TEMPERATURE_CHANGE_RATE = 'temperature_change_rate'
TEC_INVERSE_POLARITY = 'inverse_polarity'
TEC_TEMPERATURE_TOLERANCE = 'temperature_tolerance'
TEC_MIN_TIME_STABLE = 'min_time_stable'
TEC_CONTROL_P = 'control_p'
TEC_CONTROL_I = 'control_i'
TEC_CONTROL_D = 'control_d'
TEC_MAX_VOLTAGE = 'max_voltage'
TEC_MAX_CURRENT='max_current'
TEC_NTC_RESISTANCE_0 = 'resistance_0'
TEC_NTC_RESISTANCE_25 = 'resistance_25'
TEC_NTC_RESISTANCE_60 = 'resistance_60'

PELTIER_MAX_CURRENT = 'max_current'
PELTIER_DELTA_T = 'delta_t'


configuration_dictionary = {
  "ADMINS_FILE_PATH": "admins",
  "ANGLE_UNITS": "deg",
  "BYPASS_TC_CHECK": False,
  "CALIBRATION_FILE_PATH": "/home/pi/ec_config/calibration1",
  "CERTIFICATE_PATH": "",
  "CONFIGURATION_FILE_PATH": "/home/pi/ec_config/config1.json",
  "DEBUG": False,
  "MAXIMUM_DUTY_CYCLE": 0.05,
  "MAXIMUM_MIRROR_AMPLITUDE": 25,
  "MAXIMUM_STAGE_VELOCITY": 180,
  "MINIMUM_DUTY_CYCLE": 0,
  "MINIMUM_STAGE_VELOCITY": 0.05,
  "PRIVATE_KEY_PATH": "",
  "PULSER_GENERATION": 5,
  "PULSER_MAXIMUM_CURRENT": 3.0,
  "PULSER_MAXIMUM_PULSE_PERIOD": 1310720,
  "PULSER_MAXIMUM_PULSE_WIDTH": 1310720,
  "PULSER_MAXIMUM_VOLTAGE": 0.6,
  "PULSER_MINIMUM_PULSE_PERIOD": 500,
  "PULSER_MINIMUM_PULSE_WIDTH": 200,
  "PULSER_MINIMUM_VOLTAGE": 0,
  "PULSER_PORT": "/dev/tty.ec_pulser1",
  "SERVER_PORT": 5000,
  "STAGE_ANGLE": -0.00011753971488422282,
  "STAGE_ANGLE_Y": 0,
  "STAGE_CONTROL_FREQUENCY": 1000,
  "STAGE_EXCITATION_FREQUENCY": 171500,
  "STAGE_MODEL": "MR-E",
  "STAGE_PORT": "/dev/tty.ec_vcm1",
  "STAGE_PROP_FACTOR": 60,
  "STAGE_SERIAL_NUMBER": "3",
  "STYLE": {'background': '8cff96',
            'header': 'test'},
  "TC_BAUDRATE": 38400,
  "TC_MODEL": "MEERS",
  "TC_SERIAL_PORT": "/dev/tty.ec_tc_meer1",
  "USERS_FILE_PATH": "users",
  "WAVELENGTH_UNITS": "nm"
}



def _get_subconfig_filepath(file_key):
    dirpath, _ = path.split(configuration_dictionary.get(CONFIGURATION_FILE_PATH, ''))
    filepath = path.join(dirpath, configuration_dictionary.get(file_key))
    return filepath


admins = FileBackedDict(_get_subconfig_filepath(ADMINS_FILE_PATH))
users = FileBackedDict(_get_subconfig_filepath(USERS_FILE_PATH))
_calibration = None
config_backup_operations = 100
config_write_operations = config_backup_operations


def load_configuration(filepath):
    global admins
    global users
    global _calibration

    try:
        with open(filepath) as fp:
            new_config = json.load(fp)
    except Exception:
        with open('.' + filepath + '.bk') as fp:
            new_config = json.load(fp)

    configuration_dictionary.update(new_config, **{CONFIGURATION_FILE_PATH: filepath})
    admins.load(_get_subconfig_filepath(ADMINS_FILE_PATH), clear=True)
    users.load(_get_subconfig_filepath(USERS_FILE_PATH), clear=True)
    _calibration = None
    get_calibration()


def update_configuration(config_dict=(), **kwargs):
    global admins
    global users
    global _calibration
    global config_write_operations
    new = False
    for k in config_dict:
        if config_dict[k] != configuration_dictionary.get(k):
            new = True
            break
    if not new:
        for k in kwargs:
            if kwargs[k] != configuration_dictionary.get(k):
                new = True
                break
    configuration_dictionary.update(config_dict, **kwargs)
    if ADMINS_FILE_PATH in config_dict or ADMINS_FILE_PATH in kwargs:
        admins.load(_get_subconfig_filepath(ADMINS_FILE_PATH), clear=True)
    if USERS_FILE_PATH in config_dict or USERS_FILE_PATH in kwargs:
        users.load(_get_subconfig_filepath(USERS_FILE_PATH), clear=True)
    if CALIBRATION_FILE_PATH in config_dict or CALIBRATION_FILE_PATH in kwargs:
        _calibration = None
        get_calibration()

    # Save if there is an available CONFIGURATION_FILE_PATH.
    filepath = configuration_dictionary.get(CONFIGURATION_FILE_PATH)
    if filepath and new:
        with open(filepath, 'w') as fp:
            json.dump(configuration_dictionary, fp, indent=2, sort_keys=True)
        config_write_operations += 1
        if config_write_operations >= config_backup_operations:
            config_write_operations = 0
            with open(filepath + '.bk', 'w') as fp:
                json.dump(configuration_dictionary, fp, indent=2, sort_keys=True)


def hash_pw(username, password):
    return hashlib.md5((password + str(len(username)) + username + str(len(password)) + '#*salty').encode()).hexdigest()


def get_calibration():
    global _calibration
    if _calibration:
        return _calibration
    try:
        with open(_get_subconfig_filepath(CALIBRATION_FILE_PATH)) as fp:
            _calibration = json.load(fp)
    except IOError:
        return []
    return _calibration


def set_calibration(calibration):
    global _calibration
    validate_calibration(calibration)
    _calibration = calibration
    filepath = _get_subconfig_filepath(CALIBRATION_FILE_PATH)
    if filepath:
        with open(filepath, 'w') as fp:
            json.dump(calibration, fp, indent=2)


def get_angle_for_wavelength(wavelength):
    """Raises a ValueError if the wavelength is out of bounds."""
    return _angle_for_wavelength(_calibration or [], wavelength)


def get_wavelength_for_angle(angle, out_of_range_exc=True):
    """Raises a ValueError if the wavelength is out of bounds."""
    try:
        return _wavelength_for_angle(_calibration or [], angle)
    except ValueError:
        if not out_of_range_exc:
            return None
        raise


def get_angle_for_wavelength_old(wavelength):
    """Raises a ValueError if the wavelength is out of bounds."""
    return _angle_for_wavelength_old(_calibration or [], wavelength)


def get_wavelength_for_angle_old(angle, out_of_range_exc=True):
    """Raises a ValueError if the wavelength is out of bounds."""
    try:
        return _wavelength_for_angle_old(_calibration or [], angle)
    except ValueError:
        if not out_of_range_exc:
            return None
        raise


if __name__ == '__main__':
    calibration = [(320, 1000), (10, 1050)]
    set_calibration(calibration)
    print(get_angle_for_wavelength(1039))
    print(get_wavelength_for_angle(321))
