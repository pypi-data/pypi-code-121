# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities.registry import Registry
import scipy.stats

try:
    import chaospy

    _CHAOSPY_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    _CHAOSPY_AVAILABLE = False

SequenceRegistry = Registry()

# Random rule in unit hypercube, using scipy stats.uniform on multiple dimensions
uniform_sampler = scipy.stats.uniform(loc=0, scale=1)


def random(number_of_samples, dim=1, random_state=None):
    return uniform_sampler.rvs((dim, number_of_samples), random_state=random_state)


# LHS sampling methods
def latin_hypercube(number_of_samples, dim=1, random_state=None):
    sampler = scipy.stats.qmc.LatinHypercube(d=dim, seed=random_state)
    return sampler.random(n=number_of_samples).T


def centered_latin_hypercube(number_of_samples, dim=1, random_state=None):
    sampler = scipy.stats.qmc.LatinHypercube(d=dim, centered=True, seed=random_state)
    return sampler.random(n=number_of_samples).T


# Register random sampler using scipy stats.uniform
SequenceRegistry.register(
    random, name="random", info={"ExtraDependency": "None", "HasIterations": True}
)

# Register other scipy.stats sequences
scipy_sequences = {
    'latin_hypercube': latin_hypercube,
    'centered_latin_hypercube': centered_latin_hypercube,
}


for name, func in scipy_sequences.items():
    params = {"ExtraDependency": "None", "HasIterations": False}
    SequenceRegistry.register(func, name=name, info=params)


if _CHAOSPY_AVAILABLE:
    chaospy_sequences = {
        'halton': chaospy.create_halton_samples,
        'hammersley': chaospy.create_hammersley_samples,
        'sobol': chaospy.create_sobol_samples,
    }

    for name, func in chaospy_sequences.items():
        params = {"ExtraDependency": "chaospy", "HasIterations": False}
        SequenceRegistry.register(func, name=name, info=params)
