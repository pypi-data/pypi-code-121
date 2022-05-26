# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:15:57 2021

Custom exceptions raised during fault detection

@author: jvorsten
"""

# Python imports
from typing import List, MutableMapping, Union

# Third party imports

# Local imports

# %%


class FDDException(Exception):
    """Base class for exceptions on fault detection and diagnostics"""

    def __init__(self, message: str, data: MutableMapping[str, Union[str, List]]):
        """inputs
        -------
        message: (str) error mesage
        data: (dict) with required keys ['primary_axis_label', 
                                         'dependent_axis_labels']"""
        super().__init__()
        # Exception message, and also message that will be logged for reporting
        self.message = message

        # Data that will be used to generate plots
        # require independent variable be labeled with key 'primary_axis_label'
        # Further axes will be plotted on a 2D line/scatter plot
        # Based on key dependent_axis_labels
        REQUIRED_LABELS = ['primary_axis_label', 'dependent_axis_labels']
        for label in REQUIRED_LABELS:
            if not data.get(label):
                raise KeyError(
                    "Required key not found in dict: {}".format(label))
        primary_axis_key = data['primary_axis_label']
        dependent_labels = data['dependent_axis_labels']
        if not data.get(primary_axis_key):
            msg = f"Designated primary_axis_label key '{primary_axis_key}' is not found or empty"
            raise KeyError(msg)
        for label in dependent_labels:
            if not data.get(label):
                msg = f"Designated dependent_axis_labels key '{primary_axis_key}' is not found or empty"
                raise KeyError(msg)

        self.data = data

        return None
