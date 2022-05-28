# -*- coding: utf-8 -*-
'''
A Reinforcement Learning Module for Python
==========================================

This module provides a framework for training and test of different
reinforcement learning methods.

Modules
-------
agents
    Entities that act on one or more subject via an environment and observing
    the reward. `Agents` can learn or just be actors.

subjects
    Entities with an internal state that get one or more
    `agents`' action via an `environment` and return new state and reward.

environments
    Classes that connect `agents` and `subjects`, and simulate their
    interactions.

learners
A set of learning techniques used as the learner of an `agent`.

stats
    Compute statistics.

reilbase
    Base class for all `reil` classes.

stateful
    Based class for all stateful objects.

datatypes
    All custom datatypes used in `reil`.

utils
    Classes and functions that are utilities used in `reil`.

legacy
    All classes that are no longer supported.

@author: Sadjad Anzabi Zadeh (sadjad-anzabizadeh@uiowa.edu)
'''
import logging
import random
from contextlib import contextmanager
from typing import Literal, Optional, Tuple

import numpy as np
import tensorflow as tf

from ._version import get_versions

__version__ = get_versions()['version']  # type: ignore
del get_versions


FILE_FORMAT: Literal['pbz2', 'pkl'] = 'pkl'

RandomGeneratorsType = Tuple[
    random.Random, np.random.Generator, tf.random.Generator]

RANDOM_SEED: Optional[int] = None
RANDOM_GENERATOR: random.Random = random.Random()
RANDOM_GENERATOR_NP: np.random.Generator = np.random.default_rng()
RANDOM_GENERATOR_TF: tf.random.Generator = tf.random.get_global_generator()


def random_generator():
    return RANDOM_GENERATOR


def random_generator_np():
    return RANDOM_GENERATOR_NP


def random_generator_tf():
    return RANDOM_GENERATOR_TF


def random_generators_from_seed(
        seed: Optional[int] = None) -> RandomGeneratorsType:
    if seed is None:
        return (RANDOM_GENERATOR, RANDOM_GENERATOR_NP, RANDOM_GENERATOR_TF)

    random_gen: random.Random = random.Random(seed)
    random_gen_np: np.random.Generator = np.random.default_rng(
        seed)  # type: ignore
    random_gen_tf: tf.random.Generator = tf.random.Generator.from_seed(seed)

    return random_gen, random_gen_np, random_gen_tf


def set_reil_random_seed(seed: Optional[int]):
    global RANDOM_SEED
    global RANDOM_GENERATOR
    global RANDOM_GENERATOR_NP
    global RANDOM_GENERATOR_TF

    RANDOM_SEED = seed

    if seed is None:
        RANDOM_GENERATOR = random.Random()
        RANDOM_GENERATOR_NP = np.random.default_rng()
        RANDOM_GENERATOR_TF = tf.random.get_global_generator()
    else:
        RANDOM_GENERATOR, RANDOM_GENERATOR_NP, RANDOM_GENERATOR_TF = \
            random_generators_from_seed(RANDOM_SEED)


@contextmanager
def random_generator_context(
        gen: Optional[random.Random] = None,
        gen_np: Optional[np.random.Generator] = None,
        gen_tf: Optional[tf.random.Generator] = None):
    global RANDOM_GENERATOR
    global RANDOM_GENERATOR_NP
    global RANDOM_GENERATOR_TF

    temp = RANDOM_GENERATOR
    temp_np = RANDOM_GENERATOR_NP
    temp_tf = RANDOM_GENERATOR_TF
    try:
        gen_list = []
        if gen:
            RANDOM_GENERATOR = gen
            gen_list.append(RANDOM_GENERATOR)
        if gen_np:
            RANDOM_GENERATOR_NP = gen_np
            gen_list.append(RANDOM_GENERATOR_NP)
        if gen_tf:
            RANDOM_GENERATOR_TF = gen_tf
            gen_list.append(RANDOM_GENERATOR_TF)
        if len(gen_list) == 1:
            yield gen_list[0]
        else:
            yield gen_list
    finally:
        RANDOM_GENERATOR = temp
        RANDOM_GENERATOR_NP = temp_np
        RANDOM_GENERATOR_TF = temp_tf


def set_file_format(fmt: Literal['pbz2', 'pkl']):
    global FILE_FORMAT

    if fmt not in ('pbz2', 'pkl'):
        logging.warn(
            f'Unknown file format skipped: {fmt}. '
            f'Current format: {FILE_FORMAT}.')
    else:
        FILE_FORMAT = fmt
