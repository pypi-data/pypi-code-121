# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import time
import datetime
from typing import Type
from ..utilities import get_logger


class StopCriteria:
    """
    StopCriteria class

    Interface for providing stopping criteria to algorithms

    Args:
        stop_dict (dict): dictionary of stopping criteria. List of criteria keys: "max_evaluations", "max_iterations", "max_duration", "callback".
            For "callback", the value should be a user-defined function.
        experiment (Experiment): experiment the StopCriteria will apply to.


    """

    _AVAILABLE_CRITERIA = [
        "max_evaluations",
        "max_iterations",
        "max_duration",
        "callback",
    ]

    def __init__(self, stop_dict, experiment):
        self._initial_values = {}
        for key in stop_dict:
            if key not in self._AVAILABLE_CRITERIA:
                raise ValueError("Unknown stopping criterion <{}>".format(key))
        self._criteria = stop_dict
        if "max_duration" in self._criteria:
            # Convert duration to seconds
            if isinstance(self._criteria["max_duration"], datetime.timedelta):
                self._criteria["max_duration"] = self._criteria[
                    "max_duration"
                ].total_seconds()
            elif isinstance(self._criteria["max_duration"], dict):
                max_duration_args = self._criteria["max_duration"]
                try:
                    self._criteria["max_duration"] = datetime.timedelta(
                        **max_duration_args
                    ).total_seconds()
                except TypeError:
                    raise ValueError(
                        "Invalid max_duration format {}".format(max_duration_args)
                    )
            else:
                try:
                    self._criteria["max_duration"] = float(
                        self._criteria["max_duration"]
                    )
                except ValueError:
                    raise ValueError(
                        "Invalid max_duration format {}".format(
                            self._criteria["max_duration"]
                        )
                    )

        self.experiment = experiment

    def initialize(self):
        """
        Initializes the starting point for each criterion
        """
        self._initial_values["max_evaluations"] = self.experiment.number_of_evaluations
        self._initial_values["max_iterations"] = self.experiment.number_of_iterations
        self._initial_values["max_duration"] = time.time()
        self._initial_values["callback"] = None

    def is_finished(self):
        """
        Browse all criteria to check if the algorithm should stop
        """
        logger = get_logger(__name__)
        for key, value in self._criteria.items():
            if getattr(self, key)():
                logger.info(
                    "Experiment stopped : budget exhausted for criterion {} = {}".format(
                        key, value
                    )
                )
                return True

    def max_evaluations(self):
        if (
            self.experiment.number_of_evaluations
            - self._initial_values["max_evaluations"]
            >= self._criteria["max_evaluations"]
        ):
            return True
        else:
            return False

    def max_iterations(self):
        if (
            self.experiment.number_of_iterations
            - self._initial_values["max_iterations"]
            >= self._criteria["max_iterations"]
        ):
            return True
        else:
            return False

    def max_duration(self):
        if (
            time.time() - self._initial_values["max_duration"]
            >= self._criteria["max_duration"]
        ):
            return True
        else:
            return False

    def callback(self):
        return self._criteria["callback"](self.experiment)
