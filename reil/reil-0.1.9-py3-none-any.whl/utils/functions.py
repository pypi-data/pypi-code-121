# -*- coding: utf-8 -*-
'''
functions module
================

Contains some useful functions.
'''

import math
from typing import Any, Callable, Iterable, Optional, Tuple, TypeVar

import numpy as np
from reil import random_generator, random_generator_np
from reil.datatypes.feature import FeatureGenerator, FeatureSet
from scipy.stats import lognorm  # type: ignore

Categorical = TypeVar('Categorical')
T = TypeVar('T')


def random_choice(f: Any):
    '''
    This function allows `yaml` config files to use `random.choice`
    as part of `reil` module.
    '''
    return random_generator().choice(f)


def random_uniform(f: FeatureGenerator) -> float:
    if f.randomized:
        return random_generator_np().uniform(f.lower, f.upper)  # type: ignore

    if f.mean is not None:
        return f.mean

    if f.upper is None or f.lower is None:
        raise ValueError('mean, or upper and lower should be numbers.')

    return (f.upper - f.lower) / 2.0


def random_normal(f: FeatureGenerator) -> float:
    if f.randomized:
        return random_generator_np().normal(f.mean, f.stdev)  # type: ignore

    if f.mean is None:
        raise ValueError('mean should be a number.')

    return f.mean


def random_normal_truncated(f: FeatureGenerator) -> float:
    if f.randomized:
        return min(max(
            random_generator_np().normal(
                f.mean, f.stdev), f.lower), f.upper)  # type: ignore

    if f.mean is None:
        raise ValueError('mean should be a number.')

    return f.mean


def random_lognormal(f: FeatureGenerator) -> float:
    try:
        exp_mu = math.exp(f.mean)  # type: ignore
    except TypeError:
        raise ValueError('mean should be a number.')

    if f.randomized:
        lognorm.random_state = random_generator_np()
        return lognorm.rvs(s=f.stdev, scale=exp_mu)  # type: ignore

    return exp_mu


def random_lognormal_truncated(f: FeatureGenerator) -> float:
    # capture 50% of the data.
    # This restricts the log values to a "reasonable" range
    try:
        exp_mu = math.exp(f.mean)  # type: ignore
    except TypeError:
        raise ValueError('mean should be a number.')

    if f.randomized:
        quartileRange = (0.25, 0.75)
        rnd_np = random_generator_np()
        lnorm = lognorm(f.stdev, scale=exp_mu)  # type: ignore
        firstQ, thirdQ = lnorm.ppf(quartileRange)
        values = lnorm.rvs(size=1000, random_state=rnd_np)
        values = values[
            np.logical_and(firstQ < values, values < thirdQ)]  # type: ignore

        return rnd_np.choice(values)

    return exp_mu


def random_categorical(f: FeatureGenerator) -> Any:
    if (categories := f.categories) is None:
        raise TypeError('No categories found!')

    if f.randomized:
        if (probs := f.probabilities) is None:
            return random_generator().choice(categories)
        else:
            return random_generator_np().choice(
                categories, 1, p=probs)[0]  # type: ignore

    return categories[0]


def dist(x: float, y: Iterable[float]) -> float:
    return sum(abs(x - yi) for yi in y)


def square_dist(x: float, y: Iterable[float]) -> float:
    return sum((x - yi) ** 2 for yi in y)


def in_range(r: Tuple[float, float], x: Iterable[float]) -> int:
    return sum(r[0] <= xi <= r[1] for xi in x)


def interpolate(start: float, end: float, steps: int) -> Iterable[float]:
    return (
        start + (end - start) / steps * j
        for j in range(1, steps + 1))


def generate_modifier(
        operation: Callable[[T], T],
        condition: Optional[Callable[[FeatureSet], bool]] = None
) -> Callable[[FeatureSet, T], T]:
    '''Generate a modifier function for states or actions

    Parameters
    ----------
    operation:
        What should happen to the input.

    condition:
        A function that accepts a state `FeatureSet`, and based on that
        determines if the `operation` should be applied to the input.

    Returns
    -------
    :
        A function that accepts `condition_state` and `input` and returns the
        modified `input`.
    '''
    if condition is None:
        def no_condition_modifier(
                condition_state: FeatureSet, input: T) -> T:
            return operation(input)

        return no_condition_modifier
    else:
        def modifier(
                condition_state: FeatureSet, input: T) -> T:
            if condition(condition_state):  # type: ignore
                return operation(input)

            return input

    return modifier
