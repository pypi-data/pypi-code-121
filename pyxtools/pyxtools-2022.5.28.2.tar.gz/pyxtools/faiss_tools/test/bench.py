# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import pickle

import faiss
import numpy as np

from pyxtools import global_init_logger, time_cost, random_choice

try:
    from pyxtools.faiss_tools import ImageIndexUtils
except ImportError:
    from pyxtools.pyxtools.faiss_tools import ImageIndexUtils


def load_simple_data(d: int, train_length: int, search_length: int) -> (np.ndarray, np.ndarray):
    train = np.random.random((train_length, d)).astype('float32')
    train[:, 0] += np.arange(train_length) / 1000.

    search = np.random.random((search_length, d)).astype('float32')
    search[:, 0] += np.arange(search_length) / 1000.

    return train, search


def load_feature_data(d: int, data_percent: float = 0.1) -> (np.ndarray, np.ndarray):
    cache = "/tmp/Feature/train.npy.pkl"
    with open(cache, "rb") as f:
        feature_list, _ = pickle.load(f)
        feature = np.vstack(feature_list).reshape((len(feature_list), d))

        # chosen data
        chosen_index_list = random_choice([index for index in range(len(feature_list))],
                                          k=int(len(feature_list) * data_percent), unique=True)
        search_feature_list = [feature_list[index] for index in chosen_index_list]

    return feature, np.vstack(search_feature_list).reshape((len(search_feature_list), d))


@time_cost
def test_search(train_feature: np.ndarray, search_feature: np.ndarray, d: int):
    index = faiss.index_factory(d, "Flat")
    index.add(train_feature)
    index.search(search_feature, k=5)


if __name__ == '__main__':
    global_init_logger()
    dimension = 1024
    train_data, search_data = load_feature_data(d=dimension, data_percent=0.01)
    logging.info("length of train data is {}, length of search data is {}".format(
        train_data.shape[0], search_data.shape[0]))
    test_search(train_feature=train_data, search_feature=search_data, d=dimension)
