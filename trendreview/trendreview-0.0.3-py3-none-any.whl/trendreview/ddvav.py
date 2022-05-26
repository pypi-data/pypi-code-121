# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 16:11:17 2021

@author: jvorsten

Logic for fault detection and trend review including dual duct terminal units
See documentation for list of rules covered

Logic
1. Load data into pandas dataframe
2. Apply rules along data (see rules)
3. If a rule check is broken, then raise a custom exception
4. The exception will be caught the the calling function and handed to the 
reporting class which logs the broken rule
5. The exception will be handed to a plotting class which will create a plot
of the broken rule, and apply visual formatting. The plot is saved to a 
configurable location
6. 
"""

# Python imports
from typing import List, Callable
import inspect
import math

# Third party imports
import pandas as pd
import numpy as np

# Local imports
from trendreview.FDDExceptions import FDDException
from trendreview.reporting import FDDReporting
from trendreview.helpers import (
    masked_consecutive_elements,
    read_csv,
    _datetimes_to_seconds_deviation_from_start,
    _hour_segment_indices_from_seconds,
    maximum_allowed_failures,
    maximum_consecutive_failures,
    failure_threshold_exceeded)
# Declarations
DDVAV_HEADERS = [
    'DateTime', 'DischargeTemperature', 'CoolingDamperCommand',
    'CoolingDamperPosition', 'CoolingAirVolume',
    'ControlSetpoint',
    'HeatCoolMode', 'HeatingDamperCommand', 'HeatingDamperPosition',
    'HeatingAirVolume', 'RoomTemperature']
UNUSED_HEADERS = [
    'CoolingSetpoint', 'ScheduleMode', 'OccupancyMode',
    'AirflowSetpoint']
DDVAV_TYPES = {
    'DateTime': object,
    'DischargeTemperature': np.float32,
    'CoolingDamperCommand': np.float32,
    'CoolingDamperPosition': np.float32,
    'CoolingAirVolume': np.float32,
    'ControlSetpoint': np.float32,
    'HeatCoolMode': str,
    'HeatingDamperCommand': np.float32,
    'HeatingDamperPosition': np.float32,
    'HeatingAirVolume': np.float32,
    'RoomTemperature': np.float32,
}
UNUSED_DDVAV_TYPES = {
    'CoolingSetpoint': np.float32,  # Not used
    'ScheduleMode': np.int8,  # Not used
    'OccupancyMode': bool,  # Not used
    'AirflowSetpoint': np.float32,  # Not used
}

# %%


class DDVAVRules:
    """Collection of rules to check on trended data for dual-duct terminal
    units"""

    def __init__(self, filepath: str):
        """Inputs
        ------
        filepath: (string) name of CSV file related to a dual-duct terminal
        unit to open, parse, and apply rule checks to"""

        self.csv_filepath = filepath
        self.data = read_csv(self.csv_filepath, DDVAV_HEADERS, DDVAV_TYPES)

        return None

    def evaluate_rules(self, methods: List[Callable[[pd.DataFrame], None]],
                       reporter: FDDReporting) -> None:
        """This is a convenience function which calls each of the methods
        passed to it, and catches FDDExceptions thrown by each rule, then logs
        the exceptions

        Example
        ddvavRules = DDVAVRules(filepath)
        methods = ddvavRules.get_rules()
        reporter = FDDReporting(log_filepath=log_filepath)
        ddvavRules.evaluate_rules(methods, reporter)
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
    def rule_simultaneous_heating_cooling(cls, data: pd.DataFrame):
        """Iterate over heating and cooling airflow values. 
        Rule fails if - 
        1. heating and cooling volumetric flow is overlapping, where airflow > 
        0 for either heating or cooling duct while the other duct is > 0 for 
        more than n% ofobservations OR n consecutive observations"""
        # Tolerance for considering airflow at zero
        tolerance = 10
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime", "HeatingAirVolume", "CoolingAirVolume"]

        # masking and comparisons
        heating = np.ma.array(data["HeatingAirVolume"] > tolerance)
        cooling = np.ma.array(data["CoolingAirVolume"] > tolerance)
        overlap = np.bitwise_and(heating, cooling)  # masked array
        overlap_indices: tuple = overlap.nonzero()

        # Failure condition n% ofovservations
        max_overlap = math.floor(failure_percent * len(heating))
        if overlap.sum() > max_overlap:
            report_indices = overlap_indices[0][:max_overlap]
            data_view = data.loc[report_indices, [
                "DateTime", "HeatingAirVolume", "CoolingAirVolume"]].to_dict(orient='list')
            data_view['primary_axis_label'] = report_columns[0]
            data_view['dependent_axis_labels'] = report_columns[1:]
            msg = ("The maximum allowed instances of simultaneous heating and " +
                   "cooling ({} at {:.0%} of samples) was exceeded ({} observed)")
            msg = msg.format(max_overlap, failure_percent, overlap.sum())
            raise FDDException(msg, data_view)

        # Failure condition n consecutive observations
        consecutive_indices = masked_consecutive_elements(
            overlap, failure_consecutive)
        if len(consecutive_indices) > 0:
            report_indices = consecutive_indices
            data_view = data.loc[report_indices, [
                "DateTime", "HeatingAirVolume", "CoolingAirVolume"]].to_dict(orient='list')
            data_view['primary_axis_label'] = report_columns[0]
            data_view['dependent_axis_labels'] = report_columns[1:]
            msg = ("The maximum allowed consecutive instances of heating and " +
                   "cooling ({}) was exceeded ({} observed)")
            msg = msg.format(failure_consecutive, len(consecutive_indices))
            raise FDDException(msg, data_view)

        return None

    @classmethod
    def rule_heating_opposed_mode(cls, data: pd.DataFrame):
        """Iterate over heating and cooling airflow values. 
        Rule fails if - 
        1. heating/cooling occurs with the incorrect state in HeatCoolMode
        HeatingAirVolume > 0 when HeatCoolMode is in 'COOL'
        CoolingAirVolume > 0 when HeatCoolMode is in 'HEAT'
        """
        # Tolerance for considering airflow at zero
        tolerance = 10
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime", "HeatingAirVolume", "HeatCoolMode"]
        error_msg = ("Heating occurs with the incorrect state in HeatCoolMode " +
                     "HeatingAirVolume > 0 when HeatCoolMode is in 'COOL'")

        # masking and comparisons
        heating = np.ma.array(data["HeatingAirVolume"] > tolerance)
        cooling_mode = np.ma.array(data["HeatCoolMode"] == "COOL")
        mask = np.bitwise_and(heating, cooling_mode)  # masked array
        # overlap_indices = overlap.nonzero()

        # Failure condition n% of ovservations
        maximum_allowed_failures(
            mask, data, failure_percent, report_columns, error_msg)

        # Failure condition n consecutive observations
        maximum_consecutive_failures(
            mask, data, failure_consecutive, report_columns, error_msg)

        return None

    @classmethod
    def rule_cooling_opposed_mode(cls, data: pd.DataFrame):
        """Iterate over heating and cooling airflow values. 
        Rule fails if - 
        1. heating/cooling occurs with the incorrect state in HeatCoolMode
        HeatingAirVolume > 0 when HeatCoolMode is in 'COOL'
        CoolingAirVolume > 0 when HeatCoolMode is in 'HEAT'
        """
        # Tolerance for considering airflow at zero
        tolerance = 10
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime", "CoolingAirVolume", "HeatCoolMode"]
        error_msg = ("Cooling occurs with the incorrect state in HeatCoolMode " +
                     "CoolingAirVolume > 0 when HeatCoolMode is in 'HEAT'")
        # masking and comparisons
        cooling = np.ma.array(data["CoolingAirVolume"] > tolerance)
        heating_mode = np.ma.array(data["HeatCoolMode"] == "HEAT")
        mask = np.bitwise_and(cooling, heating_mode)  # masked array
        # overlap_indices = overlap.nonzero()

        # Failure condition n% of ovservations
        maximum_allowed_failures(
            mask, data, failure_percent, report_columns, error_msg)

        # Failure condition n consecutive observations
        maximum_consecutive_failures(
            mask, data, failure_consecutive, report_columns, error_msg)

        return None

    @classmethod
    def rule_cooling_damper_stuck(cls, data: pd.DataFrame):
        """Damper position does not match damper command
        Rule fails if - 
        1. Damper position and command are >5% different
        """
        # configuration
        tolerance = 5
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime", "CoolingDamperCommand",
                          "CoolingDamperPosition"]
        error_msg = ("Cooling damper stuck open: damper command and position " +
                     "are >5% different")

        # masking and comparisons
        diff = np.abs(
            np.array(data["CoolingDamperCommand"] - data["CoolingDamperPosition"]))
        mask = np.ma.array(diff > tolerance)

        # Failure condition n% of ovservations
        maximum_allowed_failures(
            mask, data, failure_percent, report_columns, error_msg)

        # Failure condition n consecutive observations
        maximum_consecutive_failures(
            mask, data, failure_consecutive, report_columns, error_msg)

        return None

    @classmethod
    def rule_heating_damper_stuck(cls, data: pd.DataFrame):
        """Damper position does not match damper command
        Rule fails if - 
        1. Damper position and command are >5% different
        """
        # configuration
        tolerance = 5
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime", "HeatingDamperCommand",
                          "HeatingDamperPosition"]
        error_msg = ("Heating damper stuck open: damper command and position " +
                     "are >5% different")

        # masking and comparisons
        diff = np.abs(
            np.array(data["HeatingDamperCommand"] - data["HeatingDamperPosition"]))
        mask = np.ma.array(diff > tolerance)

        # Failure condition n% of ovservations
        maximum_allowed_failures(
            mask, data, failure_percent, report_columns, error_msg)

        # Failure condition n consecutive observations
        maximum_consecutive_failures(
            mask, data, failure_consecutive, report_columns, error_msg)

        return None

    @classmethod
    def rule_cooling_airflow_on_closed_damper(cls, data: pd.DataFrame):
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
        report_columns = ["DateTime",
                          "CoolingAirVolume", "CoolingDamperPosition"]
        error_msg = ("Airflow measured while damper is closed:")

        # masking and comparisons
        airflow = np.ma.array(data["CoolingAirVolume"] > tolerance)
        damper_closed = np.ma.array(
            data["CoolingDamperPosition"] < tolerance_damper)
        mask = np.bitwise_and(airflow, damper_closed)  # masked array

        # Failure condition n% of ovservations
        maximum_allowed_failures(
            mask, data, failure_percent, report_columns, error_msg)

        # Failure condition n consecutive observations
        maximum_consecutive_failures(
            mask, data, failure_consecutive, report_columns, error_msg)

        return None

    @classmethod
    def rule_heating_airflow_on_closed_damper(cls, data: pd.DataFrame):
        """Airflow is calculated to pass by damper when damper is commanded
        closed
        Rule fails if
        1. Airflow is greater than 10[cfm](default) AND damper position is
        <2[%](default)"""
        # Tolerance for considering airflow at zero
        tolerance = 10
        tolerance_damper = 2  # percent
        failure_percent = 0.02
        failure_consecutive = 3
        report_columns = ["DateTime",
                          "HeatingAirVolume", "HeatingDamperPosition"]
        error_msg = ("Airflow measured while damper is closed:")

        # masking and comparisons
        airflow = np.ma.array(data["HeatingAirVolume"] > tolerance)
        damper_closed = np.ma.array(
            data["HeatingDamperPosition"] < tolerance_damper)
        mask = np.bitwise_and(airflow, damper_closed)  # masked array

        # Failure condition n% of ovservations
        maximum_allowed_failures(mask, data, failure_percent,
                                 report_columns, error_msg)

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
