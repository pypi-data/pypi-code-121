# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import copy
from comets.utilities import utilities
from .generatorregistry import GeneratorRegistry
import comets.experiments.sampling.sampling as sampling


class Generator:
    def __init__(self, generator):

        # Get arguments and check values
        try:
            self.name = generator["name"]
        except KeyError:
            raise ValueError("A variable should have a name")
        # For custom generators, we might have directly a CustomSampling object as value
        if isinstance(generator["sampling"], sampling.CustomSampling):
            sampling_obj = generator["sampling"]
        # Else, we look in the different registries
        elif isinstance(generator["sampling"], str):
            try:
                sampling_obj = sampling.CustomSampling(
                    GeneratorRegistry[generator["sampling"]]
                )
            except KeyError:
                raise ValueError("Unknown generator {}".format(generator["sampling"]))
        else:
            raise ValueError(
                "In variable {}, generator does not have a valid format".format(
                    self.name
                )
            )
        utilities.check_size(generator)

        if 'size' in generator:
            self.size = generator["size"]
            self.dimension = generator["size"]
        else:
            self.size = None
            self.dimension = 1

        # Make copies of the generators if size is given
        if self.size is None:
            self.generators = sampling_obj
        else:
            # if size exists, we copy the generator 'size' times and store it under self._generators
            self.generators = [
                copy.deepcopy(sampling_obj) for _ in range(generator["size"])
            ]
