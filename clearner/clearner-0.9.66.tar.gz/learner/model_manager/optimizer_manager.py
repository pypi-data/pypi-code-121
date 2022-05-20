# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements classes and functions to build optimizer for training neural networks."""
import sys
from copy import deepcopy
import logging

from torch.optim import Adam, AdamW, SparseAdam, Adamax, ASGD, LBFGS, RMSprop, Rprop, SGD

from learner.data_worker.data_processor import delete_keys_from_dict


class OptimizerBuilder:
    """A class to build an optimizer based on the input parameters and model parameters.
    """
    def __init__(self, params, optimizer_dict):
        """Initialize an OptimizerBuilder object using a the model parameters (from the PyTorch model) and
        other input parameters that contains the optimizer type, lr, etc.

        :param params: the parameters of the model to be optimized. We may need to consider moving this to the build_optimizer method.
        :param optimizer_dict: a dictionary that contains all the parameters for instantiating the optimizer object
        """
        self._params = params
        self._optimizer_type = optimizer_dict["type"]
        self._optimizer_dict = deepcopy(optimizer_dict)

    @property
    def params(self):
        return self._params

    @property
    def optimizer_type(self):
        return self._optimizer_type

    @property
    def optimizer_dict(self):
        return self._optimizer_dict

    def build_optimizer(self):
        """The main method to get the optimizer object using functional programming. Here, we use the optimizer type to
        get the optimizer object.

        :return: the optimizer object with all the parameters set.
        """
        delete_keys_from_dict(self.optimizer_dict, ["type"])
        try:
            return getattr(sys.modules[__name__], self.optimizer_type)(self.params, **self.optimizer_dict)
        except Exception as e:
            logging.critical(f"Unable to build the optimizer. The error is: {e}")
            sys.exit(1)

