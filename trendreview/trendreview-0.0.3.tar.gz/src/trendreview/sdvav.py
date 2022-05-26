# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 13:25:15 2022

@author: jvorsten

Logic for fault detection and trend review including single duct terminal units
See documentation for list of rules covered

Logic
1. Load data
2. Apply rules along data (see rules)
3. If a rule check is broken, then raise a custom exception
4. The exception will be caught the the calling function and handed to the 
reporting class which logs the broken rule
5. The exception will be handed to a plotting class which will create a plot
of the broken rule, and apply visual formatting. The plot is saved to a 
configurable location

#TODO
Single duct VAV uses discharge temperature control or room temperature control
Should this be configurble to cooling only or cooling + heating
Discharge temperature too high
Discharge temperature too low
Discharge temperature versus valve position
Airflow setpoint versus measured airflow
Damper position versus airflow measurement
"""

# Python imports
from typing import List, Callable
import inspect
import math

# Third party imports
import pandas as pd
import numpy as np

# Local imports
from .FDDExceptions import FDDException
from .reporting import FDDReporting
from .helpers import (masked_consecutive_elements,
                      read_csv,
                      _datetimes_to_seconds_deviation_from_start,
                      _hour_segment_indices_from_seconds,
                      maximum_allowed_failures,
                      maximum_consecutive_failures,
                      failure_threshold_exceeded)
# Declarations
SDVAV_HEADERS = ['DateTime',
                 'DamperCommand',
                 'DamperPosition',
                 'AirVolume',
                 'ControlSetpoint',
                 'HeatCoolMode',
                 'RoomTemperature',
                 'HeatingValveCommand',
                 'HeatingValvePosition',
                 ]
UNUSED_SDVAV_HEADERS = [
    'DischargeTemperature',  # Not used
    'DischargeTemperatureSetpoint',  # Not used
    'ScheduleMode',  # Not used
    'OccupancyMode',  # Not used
    'AirflowSetpoint',  # Not used
]
SDVAV_TYPES = {'DateTime': object,
               'DamperCommand': np.float32,
               'DamperPosition': np.float32,
               'AirVolume': np.float32,
               'ControlSetpoint': np.float32,
               'HeatCoolMode': str,
               'RoomTemperature': np.float32,
               'HeatingValveCommand': np.float32,
               'HeatingValvePosition': np.float32,
               }
UNUSED_SDVAV_TYPES = {
    'DischargeTemperature': np.float32,
    'DischargeTemperatureSetpoint': np.float32,
    'ScheduleMode': np.int8,
    'OccupancyMode': bool,
    'AirflowSetpoint': np.float32,
}

# %%


class SDVAVRules:
    """Collection of rules to check on trended data for dual-duct terminal
    units"""

    def __init__(self, filepath: str):
        """Inputs
        ------
        filepath: (string) name of CSV file related to a dual-duct terminal
        unit to open, parse, and apply rule checks to"""

        self.csv_filepath = filepath
        self.data = read_csv(self.csv_filepath, SDVAV_HEADERS, SDVAV_TYPES)

        return None

    def evaluate_rules(self, methods: List[Callable[[pd.DataFrame], None]],
                       reporter: FDDReporting) -> None:
        """This is a convenience function which calls each of the methods
        passed to it, and catches FDDExceptions thrown by each rule, then logs
        the exceptions

        Example
        sdvavRules = SDVAVRules(filepath)
        methods = sdvavRules.get_rules()
        reporter = FDDReporting(log_filepath=log_filepath)
        sdvavRules.evaluate_rules(methods, reporter)
        # Results of faults detected in `filepath`
        """
        for method in methods:
            try:
                method(self.data)
            except FDDException as e:
                reporter.log_exception(e, create_image=True)
        return None

    def get_rules(self):
        """Get all class member functions that start with 'rule_'"""

        methods = []
        for name in dir(self):
            attribute = getattr(self, name)
            if inspect.ismethod(attribute) and str(attribute).__contains__('.rule_'):
                methods.append(attribute)

        return methods

    @classmethod
    def rule_heating_opposed_mode(cls, data: pd.DataFrame):
        """Iterate over heating valve position and operation mode. 
        Rule fails if - 
        1. heating occurs with the incorrect state in HeatCoolMode
        HeatingValvePosition > 0 when HeatCoolMode is in 'COOL'
        """
        # Tolerance for considering airflow at zero
        tolerance = 10
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime", "HeatingValvePosition", "HeatCoolMode"]
        error_msg = ("Heating occurs with the incorrect state in HeatCoolMode " +
                     "HeatingValvePosition > 0 when HeatCoolMode is in 'COOL'")

        # masking and comparisons
        heating = np.ma.array(data["HeatingValvePosition"] > tolerance)
        cooling_mode = np.ma.array(data["HeatCoolMode"] == "COOL")
        mask = np.bitwise_and(heating, cooling_mode)  # masked array
        # overlap_indices = overlap.nonzero()

        # Failure condition n% of ovservations
        maximum_allowed_failures(mask, data, failure_percent, report_columns,
                                 error_msg)

        # Failure condition n consecutive observations
        maximum_consecutive_failures(mask, data, failure_consecutive,
                                     report_columns, error_msg)

        return None

    @classmethod
    def rule_damper_stuck(cls, data: pd.DataFrame):
        """Damper position does not match damper command
        Rule fails if - 
        1. Damper position and command are >5% different
        """
        # configuration
        tolerance = 5
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime", "DamperCommand",
                          "DamperPosition"]
        error_msg = ("Damper stuck open: damper command and position " +
                     "are >5% different")

        # masking and comparisons
        diff = np.abs(np.array(data["DamperCommand"] - data["DamperPosition"]))
        mask = np.ma.array(diff > tolerance)

        # Failure condition n% of ovservations
        maximum_allowed_failures(mask, data, failure_percent, report_columns,
                                 error_msg)

        # Failure condition n consecutive observations
        maximum_consecutive_failures(mask, data, failure_consecutive,
                                     report_columns, error_msg)

        return None

    @classmethod
    def rule_airflow_on_closed_damper(cls, data: pd.DataFrame):
        """Airflow is calculated to pass by damper when damper is commanded
        closed
        Rule fails if - 
        1. Airflow is greater than 10[cfm](default) AND damper position is 
        <2[%](default)"""
        # Tolerance for considering airflow at zero
        tolerance = 10
        tolerance_damper = 2  # percent
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime", "AirVolume", "DamperPosition"]
        error_msg = ("Airflow measured while damper is closed:")

        # masking and comparisons
        airflow = np.ma.array(data["AirVolume"] > tolerance)
        damper_closed = np.ma.array(data["DamperPosition"] < tolerance_damper)
        mask = np.bitwise_and(airflow, damper_closed)  # masked array

        # Failure condition n% of ovservations
        maximum_allowed_failures(mask, data, failure_percent, report_columns,
                                 error_msg)

        # Failure condition n consecutive observations
        maximum_consecutive_failures(mask, data, failure_consecutive,
                                     report_columns, error_msg)

        return None

    @classmethod
    def rule_damper_position_airflow_relationship(cls, data: pd.DataFrame):
        """Not implemented
        Ideally, understand the relationship between damper position and 
        calculated airflow. The intention is find misconfigured or backwards
        mounted actuators. However, controls can configure reverse or direct
        acting control, and increasing damper command may not correspond to
        increasing airflow. This rule is not implemented."""
        return None

    @classmethod
    def rule_room_temperature_deviation(cls, data: pd.DataFrame):
        """Test for room temperature ability to reach setpoint
        Rule fails if - 
        1. room temperature deviates from control setpoint as measured by 
        integral of measured temperature versus setpoint by > 1 Degree*hour per 
        hour measured"""
        # Tolerance for considering airflow at zero
        failure_threshold = 1  # [Degree * hour]
        report_columns = ["DateTime", "ControlSetpoint", "RoomTemperature"]
        error_msg = ("Excessive deviation in process variable versus setpoint. " +
                     "{:.2f} DegF*hour calculated deviation during hour long " +
                     "measurement period; threshold={}")

        # Break into hour segments
        seconds = _datetimes_to_seconds_deviation_from_start(data["DateTime"])
        segments = _hour_segment_indices_from_seconds(seconds)

        # summation
        for segment in segments:
            # Calculate temperature deviation
            diff = data.loc[segment, "ControlSetpoint"].to_numpy(
            ) - data.loc[segment, "RoomTemperature"].to_numpy()
            deviation = np.trapz(y=diff, x=seconds[segment]) / 3600
            # Error determination
            if abs(deviation) > failure_threshold:
                failure_threshold_exceeded(
                    data, report_columns,
                    report_indices=segment,
                    error_msg=error_msg.format(
                        abs(deviation), failure_threshold)
                )

        return None
