# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities.registry import Registry
import numpy as np
from scipy import stats

GeneratorRegistry = Registry()


# Random rule in unit hypercube, using scipy.stats, discrete and continuous case
uniform_sampler = stats.uniform(loc=0, scale=1)


def random01(number_of_samples, random_state=None):
    return uniform_sampler.rvs(
        size=number_of_samples, random_state=random_state
    ).tolist()


def seed_generator(number_of_samples):
    return np.random.randint(
        2 * np.iinfo(np.int32).max - 1, size=number_of_samples
    ).tolist()


# Seed generator
def seed_sequence_generator(number_of_samples, seed=None):
    return np.random.SeedSequence(seed).spawn(number_of_samples)


# Register random sampler using scipy stats.uniform
GeneratorRegistry.register(random01, name="random01")
GeneratorRegistry.register(
    seed_generator,
    name="seed_generator",
)
# Register SeedGenerator
GeneratorRegistry.register(
    seed_sequence_generator,
    name="seed_sequence_generator",
)
