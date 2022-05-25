# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import numpy as np
from comets.utilities import utilities
from .distributionregistry import (
    DistributionRegistry,
)


class Distribution:
    """
    A class to create iid distributions.

    A Distribution object in Comets is a wrapper around a distribution defined by an external library (scipy.stats).
    The list of available distributions and their corresponding parameters are stored in the DistributionRegistry.
    It exposes a single method `get_samples` that takes as argument a single integer and returns the corresponding number of samples randomly drawn from the distribution.
    A Distribution object handle iid distributions with optional input key 'size'.

    Args:
        variable (dict): a dictionnary containing the following key/value pairs:
            * "name"/str, defining the variable name
            * "sampling"/str, defining the distribution name
            * "parameters"/dict, defining the dictionary of parameters to pass to the distribution
            * "size"/int, (optional) specifies how many iid copies of the variable to construct
    """

    def __init__(self, variable):

        # Get arguments and check values
        try:
            self.name = variable["name"]
        except KeyError:
            raise ValueError("A variable should have a name")
        try:
            self.distribution_name = variable["sampling"]
        except KeyError:
            raise ValueError(
                "Provide distribution name for variable {}".format(self.name)
            )
        # Parse parameters:
        try:
            self.params = variable["parameters"]
        except KeyError:
            raise ValueError(
                "Provide distribution parameters for variable {}".format(self.name)
            )
        utilities.check_size(variable)

        if 'size' in variable:
            self.size = variable['size']
            self.dimension = self.size
        else:
            self.size = None
            self.dimension = 1

        # Construct the distribution from the registry
        try:
            self._distribution = DistributionRegistry[self.distribution_name](
                **self.params
            )
        except KeyError:
            raise ValueError("Unknown distribution: {}".format(self.distribution_name))

        self._discrete = False
        # Set _discrete to True for discrete distributions
        self._set_discrete()

    def _set_discrete(self):
        if (
            DistributionRegistry.information[self.distribution_name]["Type"]
            == "Discrete1D"
        ):
            self._discrete = True

    def get_samples(self, number_of_samples, random_state=None):
        """Get random variate samples of the distribution

        Args:
            number_of_samples (int): number of samples to draw
            random_state (optional): Random state object. Defaults to None.

        Returns:
            numpy array: array of shape (dimension, number_of_samples), where 'dimension' represents the number of iid distributions requested
        """
        return self._distribution.rvs(
            (self.dimension, number_of_samples), random_state=random_state
        )

    def ppf(self, usamples):
        """Percent point function (inverse of cdf) of the given distribution.

        Takes samples from the unit hypercube of dimension 'size', transform them into samples of the distribution.
        The transformation is called independently on each line (iid hypothesis).

        Args:
            usamples (numpy array): Samples in the unit hypercube, with shape (size, number_of_samples)

        Returns:
            numpy array: array of shape (size, number_of_samples), where size represents the number of iid distributions requested
        """
        size, number_of_samples = usamples.shape
        # Transformed samples for current distribution
        tsamples = np.empty((size, number_of_samples))
        for j in range(size):
            tsamples[j, :] = self._distribution.ppf(usamples[j, :])
        # Cast to int for discrete type, because for some reason ppf returns floats
        if self._discrete:
            tsamples = tsamples.astype(int)
        return tsamples
