#!/usr/bin/env python3
"""
Ageas Reborn

author: jy, nkmtmsys
"""

import difflib
import itertools
import ageas.classifier as classifier
from sklearn import svm
from collections import deque



class Error(Exception):
    """
    Error handling
    """
    pass


class Config_Maker_Template(object):
    """
    Template class for config makers
    """
    def __init__(self, header = None, config = None):
        self.epoch = 1
        self.batch_size = None
        self.header = header
        config = self.__resize_config(config)
        self.configs = self.__get_configs(config)

    # Generate all possible hyperparameter combination
    # Check model config file for orders of parameters
    def __get_configs(self, config):
        deq = deque()
        combs = list(itertools.product(*config.values()))
        for ele in combs:
            assert len(config.keys()) == len(ele)
            temp = {}
            for i in range(len(ele)):
                key = list(config.keys())[i]
                value = ele[i]
                temp[key] = value
            temp = self.__verify_config(temp)
            if temp is not None:
                record = {'config':temp}
                if record not in deq: deq.appendleft(record)
        return {self.header + str(i) : deq[i] for i in range(len(deq))}

    # this should vary with different classes
    def __resize_config(self, query):
        return query

    # this should vary with different classes
    def __verify_config(self, query):
        return query
