# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 14:27:06 2022

@author: jvorsten

Logic for fault detection and trend review including single duct terminal units
See documentation for list of rules covered

Logic
1. Load data
2. Graph each data point versus DateTime
"""

# Python imports
from typing import List, Callable, Dict
import inspect
import math

# Third party imports
import pandas as pd
import numpy as np

# Local imports
from .FDDExceptions import FDDException
from .reporting import FDDReporting

# Declarations
HEADERS = ['DateTime',
           ]
TYPES = {'DateTime': object,
         }

chart_properties = {
    'color': 'b',  # Blue
    'dash_capstyle': 'butt',  # Doesnt matter with scatter
    'marker': '.',  # point, could also try pixel depending on amount of data
    'markersize': 2,  # points, diameter or marker
    'markevery': None,  # Plot all markers
    'linestyle': 'None',
}

# %%


class GraphAll:
    """Collection of rules to check on trended data for dual-duct terminal
    units"""

    def __init__(self, filepath: str, parse_dates='DateTime'):
        """Inputs
        ------
        filepath: (string) name of CSV file related to a dual-duct terminal
        unit to open, parse, and apply rule checks to"""

        self.csv_filepath = filepath
        self.data = pd.read_csv(filepath, sep=',', parse_dates=[parse_dates])

        return None

    def graph_all_data(self,
                       reporter: FDDReporting,
                       independent_axis_name: str = 'DateTime',
                       dependent_axis_names: List[str] = None,) -> None:
        """Graph each of dependent axis names versus a specified independent 
        axis

        Example
        graphall = GraphAll('c:/user/downloads/report.txt', parse_dates='DateTime')
        graphall.graph_all_data(
            FDDReporting(...), 
            independent_axis_name='DateTime', 
            dependent_axis_names=None) # Graph all data when None

        """

        if dependent_axis_names == None:
            dependent_axis_names = self.get_dependent_axis_names(
                independent_axis_name)

        for dependent_axis_name in dependent_axis_names:
            # Generic message
            msg = "Graph of {} versus {}".format(dependent_axis_name,
                                                 independent_axis_name)
            # Collect data
            data_view = self.data.loc[:, [independent_axis_name, dependent_axis_name]]\
                .to_dict(orient='list')
            data_view['primary_axis_label'] = independent_axis_name
            data_view['dependent_axis_labels'] = [dependent_axis_name]

            # Cast pandas timestamp to string
            self._timestamp_to_string(data_view[independent_axis_name])

            # The exception holds message and data
            fddexception = FDDException(msg, data_view)

            # Create visualization and report
            reporter.log_exception(fddexception, create_image=True,
                                   chart_properties=chart_properties)

        return None

    def graph_multiple_dependent_axis(
            self,
            reporter: FDDReporting,
            independent_axis_name: str = 'DateTime',
            dependent_axis_names: List[str] = None) -> None:
        """Plot multiple dependent variables agaist a single axis. For example, graph
        multiple variables against time, with both dependent variables appearing on a 
        common dependent axis

        Example
        graphall = GraphAll('c:/user/downloads/report.txt', parse_dates='DateTime')
        graphall.graph_all_data(
            FDDReporting(...), # Customize for your needs
            independent_axis_name='DateTime', 
            # 'TemperatureA, TemperatureB' required on file headers
            dependent_axis_names=['TemperatureA','TemperatureB']) 
        """

        if dependent_axis_names == None:
            raise ValueError(
                f"Specify dependent axis labels to be plotted. Got {dependent_axis_names}")

        # Generic message
        msg = f"Graph of {dependent_axis_names} versus {independent_axis_name}"
        # Collect data
        columns: List[str] = []
        columns.append(independent_axis_name)
        for dependent_axis_name in dependent_axis_names:
            columns.append(dependent_axis_name)

        # Create a data view (dictionary containing data to be plotted)
        data_view = self.data.loc[:, columns]\
            .to_dict(orient='list')
        data_view['primary_axis_label'] = independent_axis_name  # Sring
        data_view['dependent_axis_labels'] = dependent_axis_names  # List

        # Cast pandas timestamp to string
        self._timestamp_to_string(data_view[independent_axis_name])

        # The exception holds message and data
        fddexception = FDDException(msg, data_view)

        # Create visualization and report
        reporter.log_exception(
            fddexception, create_image=True,
            chart_properties={})

        return None

    @classmethod
    def _timestamp_to_string(cls, data: List):

        for i in range(0, len(data)):
            data[i] = str(data[i])  # Modify timestamp value in place

        return None

    def get_dependent_axis_names(self, independent_axis_name: str) -> List[str]:
        """Get a list of dependent axis names based on header data
        inputs
        -------
        outputs
        -------
        dependent_axis_names: (list of str)"""
        # Pandas Index object
        dependent_axis_names = self.data.columns.to_list()
        # Remove independent axis
        dependent_axis_names.remove(independent_axis_name)

        return dependent_axis_names
