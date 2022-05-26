#!/usr/bin/env python3

import logging
import numpy as np
import random
from typing import List, Tuple

# ToDo: Make a function that just takes an annotation df and a split-by category and then just adds a "set" column.
#       Warn if there are repititions (i.e. non-unique values), such as when using the "file_name" column for splitting.
#       However, this would probably go without the id-dictionary that was used in ds_annotations.
#       Check how often and where that was actually used! [I did. It is actually only used in add_set_column()!]


def get_cutoff_indices(n, prop_train, prop_val, prop_test):
    assert np.isclose((prop_train + prop_val + prop_test), 1.0)
    # The following block uses int(np.round()) to prevent baker's rounding.
    _train_cutoff = int(np.round(n * prop_train))
    _val_cutoff = int(np.round(n * (prop_train + prop_val)))
    logging.debug(f'Train cutoff: {_train_cutoff}({n * prop_train})')
    logging.debug(f'Val. cutoff: {_val_cutoff}({n * (prop_train + prop_val)})')
    logging.debug(f'N - N * test_prop: {n - int(np.round(n * prop_test))}')
    assert _val_cutoff == (n - int(np.round(n * prop_test)))
    return _train_cutoff, _val_cutoff


def split_on_cutoffs(shuffled_instances: list, train_cutoff_i: int, val_cutoff_i: int) -> Tuple[list, list, list]:
    """
    Requires a list of shuffled instances and returns the three portions (train, test, val) of it.
    :param shuffled_instances:
    :param train_cutoff_i:
    :param val_cutoff_i:
    :return: Tuple[list, list, list]
    """
    train_ids = shuffled_instances[:train_cutoff_i]
    val_ids = shuffled_instances[train_cutoff_i:val_cutoff_i]
    test_ids = shuffled_instances[val_cutoff_i:]
    return train_ids, val_ids, test_ids


def create_model_indices(n_instances: int,
                         prop_train: float = 0.7, prop_val: float = 0.2, prop_test: float = 0.1,
                         seed=42) -> dict:
    """
    Creates shuffled indeces to split a data set of size n_instances into a train, validation and test set with the
    proportions given in the parameters.
    :param n_instances: Number of instances (e.g. pictures). Note that this starts with 1!
    :param prop_train: float
    :param prop_val: float
    :param prop_test: float
    :param seed: int
    :return: train_indices: dict('train': [indices list], 'test': [indices list], 'val': [indices list]
    """
    random.seed(seed)
    assert np.isclose(prop_train + prop_val + prop_test, 1.0)
    _shuffled_ids = random.sample(list(range(n_instances)), n_instances)
    assert max(_shuffled_ids) == (n_instances - 1)  # Indeces are zero indexed, number of instances not.
    assert len(_shuffled_ids) == len(set(_shuffled_ids)) == n_instances
    _train_cutoff, _val_cutoff = get_cutoff_indices(n_instances, prop_train, prop_val, prop_test)
    train_ids, val_ids, test_ids = split_on_cutoffs(_shuffled_ids, _train_cutoff, _val_cutoff)
    # Make sure there is no overlap between the three groups:
    if set(train_ids).intersection(set(val_ids), set(test_ids)):
        raise OSError('Split data set sections overlap')
    logging.info(f'TRAIN:\t{len(train_ids)}:\t{train_ids}')
    logging.info(f'VAL:\t{len(val_ids)}:\t{val_ids}')
    logging.info(f'TEST:\t{len(test_ids)}:\t{test_ids}')

    return {'train': train_ids,
            'val': val_ids,
            'test': test_ids}


def split_instance_list_to_train_val_test(instances: list,
                                          prop_train_val_test: Tuple[float, float, float] = (0.7, 0.2, 0.1),
                                          seed=42) -> dict:
    """
    Splits a list (of e.g. file names) into three, according to the train, val and test proportions. Returns a dictionary containing a resulting list under each category key.
    :param instances: list. Can be a list of indices or a list of instances.
    :param prop_train_val_test: Tuple of proportions of train, validation and test set. Must add up to 1
    :param seed:
    :return:
    """
    random.seed(seed)
    prop_train, prop_val, prop_test = prop_train_val_test
    assert np.isclose((prop_train + prop_val + prop_test), 1.0)
    assert len(instances) == len(set(instances))
    _shuffled_instances = random.sample(instances, len(instances))
    _train_cutoff, _val_cutoff = get_cutoff_indices(len(instances), prop_train, prop_val, prop_test)
    train_instances, val_instances, test_instances = split_on_cutoffs(_shuffled_instances, _train_cutoff, _val_cutoff)

    logging.info(f"TRAIN:\t{len(train_instances)}:\t{train_instances}")
    logging.info(f"VAL:\t{len(val_instances)}:\t{val_instances}")
    logging.info(f"TEST:\t{len(test_instances)}:\t{test_instances}")

    return {"train": train_instances,
            "val": val_instances,
            "test": test_instances}