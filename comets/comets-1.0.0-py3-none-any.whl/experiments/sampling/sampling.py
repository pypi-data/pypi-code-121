# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from abc import ABC, abstractmethod
from .distributions import Distribution, DistributionRegistry
from .generator import Generator
from . import SequenceRegistry
from . import GeneratorRegistry

import numpy as np


class BaseSampling(ABC):
    """
    Abstract class for sampling
    """

    def __init__(self):
        pass

    @abstractmethod
    def get_samples(self, number_of_samples):
        pass


class CustomSampling(BaseSampling):
    """
    Wrapper for custom generators.

    It freezes the arguments of the generator provided as input. Generated samples can be of any type and will be handled by the task encoder.

    Args:
        generator (callable): A callable object that takes as first argument an integer determining the number of samples and returns a list of the corresponding samples

    """

    def __init__(self, generator, *args, **kwargs):
        self._generator = generator
        self._args = args
        self._kwargs = kwargs

    def get_samples(self, number_of_samples):
        """
        Draw samples from the generator

        Args:
            number_of_samples (int)

        Returns:
            List of samples, with length number_of_samples
        """
        return self._generator(number_of_samples, *self._args, **self._kwargs)


class DistributionSampling(BaseSampling):
    """
    A class to group and sample the variables defined with distributions

    Args:
        variables (list): list of random variables (list of dictionaries) following some distributions.
    """

    def __init__(self, variables, rule="random"):
        # Parse variables as a list of Distribution objects
        self._distributions = [Distribution(variable) for variable in variables]
        self.dimension = None
        self._set_dimension()  # Automatically compute problem dimension
        if rule is None or rule == "random":
            # Default sampler is rvs
            self._rule = "random"
        else:
            self._rule = SequenceRegistry[rule]

    def get_samples(self, number_of_samples):
        """Draw samples assuming independently distributed variables

        Args:
            number_of_samples (int)

        Returns:
            List of ParameterSet, with length number_of_samples
        """
        samples = [{} for _ in range(number_of_samples)]

        if self._rule == "random":
            for dist in self._distributions:
                # Transpose to numpy array with line=number_of_samples, columns=dist.dimension
                samp = dist.get_samples(number_of_samples).T
                if dist.size is None:
                    for i in range(number_of_samples):
                        # Add sample to dictionary as scalar
                        samples[i][dist.name] = np.squeeze(samp[i, ...]).tolist()
                else:
                    for i in range(number_of_samples):
                        # Add sample to dictionary as list
                        samples[i][dist.name] = samp[i, ...].tolist()
        else:
            # Samples on unit hypercube, shape (dimension, number_of_samples)
            usamples = self._rule(number_of_samples, dim=self.dimension)
            # Column counter
            col = 0
            # For each Distribution object, for each of its dimension, transform with ppf
            for dist in self._distributions:
                # Transpose to get shape (number_of_samples, dimension)
                tsamples = dist.ppf(usamples[col : col + dist.dimension, :]).T
                col += dist.dimension
                # Now transform to comets format
                if dist.size is None:
                    for i in range(number_of_samples):
                        # Add sample to dictionary as scalar
                        samples[i][dist.name] = np.squeeze(tsamples[i, ...]).tolist()
                else:
                    for i in range(number_of_samples):
                        # Add sample to dictionary as list
                        samples[i][dist.name] = tsamples[i, ...].tolist()
        return samples

    def _set_dimension(self):
        self.dimension = 0
        for dist in self._distributions:
            self.dimension += dist.dimension


class CompositeSampling(BaseSampling):
    """
    CompositeSampling groups a list of samplers into one sampling interface.

    It can handle sampling from both distributions or custom generators.

    Args:
        variables (list): list of random variables or generators (list of dictionaries).
    """

    def __init__(self, variables, rule="random"):

        # Separate generators and distributions:

        # Generators are saved as a list of variables (list of dictionaries):
        # the CustomSampling object is stored under the dictionnary key "sampling" and accessed with generator["sampling"].
        # If size is not None, generator["sampling"] is a list containing copies of the original CustomSampling object.
        self._generators = []

        # Distributions are stored in a DistributionSampler object.
        # We build a temporary list 'distributions' to separate them from custom generators.
        distributions = []

        for variable in variables:
            if "name" not in variable.keys():
                raise ValueError("A variable should have a name")

            if "sampling" not in variable.keys():
                raise ValueError(
                    'Variable {} should define a distribution or a custom generator using key "sampling"'.format(
                        variable["name"]
                    )
                )
            # For custom generators, we might have directly a CustomSampling object as value
            if isinstance(variable["sampling"], CustomSampling):
                self._generators.append(Generator(variable))
            # Else, we look in the different registries
            elif isinstance(variable["sampling"], str):
                if variable["sampling"] in GeneratorRegistry.keys():
                    self._generators.append(Generator(variable))
                elif variable["sampling"] in DistributionRegistry.keys():
                    distributions.append(variable)
                else:
                    raise ValueError(
                        "Unknown generator or distribution {}".format(
                            variable["sampling"]
                        )
                    )
            else:
                raise ValueError(
                    "In variable {}, generator does not have a valid format".format(
                        variable["name"]
                    )
                )

        # Construct DistributionSampler:
        if len(distributions) == 0:
            self._distribution_sampler = None
        else:
            self._distribution_sampler = DistributionSampling(distributions, rule=rule)
        # Set generators as None if list is empty, to match with _distribution_sampler
        if len(self._generators) == 0:
            self._generators = None

        self.dimension = None
        self._set_dimension()  # Automatically compute problem dimension

        # Generate the correct get_samples method depending on inputs
        self._get_samples = self._define_get_samples()

    def get_samples(self, number_of_samples):
        """Draw samples assuming independent generators / distributions in each dimension

        Args:
            number_of_samples (int)

        Returns:
            List of ParameterSet, with length number_of_samples
        """
        return self._get_samples(number_of_samples)

    def _distributions_get_samples(self, number_of_samples):
        return self._distribution_sampler.get_samples(number_of_samples)

    def _generators_get_samples(self, number_of_samples):
        samples = [{} for _ in range(number_of_samples)]
        # To sample from a generator, we need its get_sample method
        # The calling object is stored under key generator["sampling"]
        for generator in self._generators:
            if generator.size is None:
                list_of_samples = generator.generators.get_samples(number_of_samples)
                # Now transform to comets format
                for i, sample in enumerate(samples):
                    sample[generator.name] = list_of_samples[i]
            else:
                for sample in samples:
                    sample[generator.name] = []
                for obj in generator.generators:
                    list_of_samples = obj.get_samples(number_of_samples)
                    # Now transform to comets format
                    for i, sample in enumerate(samples):
                        sample[generator.name].append(list_of_samples[i])
        return samples

    def _general_get_samples(self, number_of_samples):
        distrib_samples = self._distributions_get_samples(number_of_samples)
        generator_samples = self._generators_get_samples(number_of_samples)
        for i in range(number_of_samples):
            generator_samples[i].update(distrib_samples[i])
        return generator_samples

    def _define_get_samples(self):
        if self._generators is None:
            return self._distributions_get_samples
        elif self._distribution_sampler is None:
            return self._generators_get_samples
        else:
            return self._general_get_samples

    def _set_dimension(self):
        if self._distribution_sampler is None:
            self.dimension = 0
        else:
            self.dimension = self._distribution_sampler.dimension
        if self._generators is not None:
            for generator in self._generators:
                self.dimension += generator.dimension
