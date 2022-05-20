# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for constructing the loss functions. Currently, this module implements the LossBuilder class, which
creates the loss objects."""
import sys
from copy import deepcopy

import logging
from torch.nn import CrossEntropyLoss, NLLLoss, MSELoss, L1Loss

from learner.data_worker.data_processor import delete_keys_from_dict


class LossBuilder:
    """Use a dictionary of parameters to build the loss objects. The main method here is build_loss. This method uses
    functional programming to build the loss objects."""
    def __init__(self, loss_dict):
        """Initialize a LossBuilder object using a dictionary of parameters. This dictionary would contain the type of
        the loss function as well as other parameters.

        :param loss_dict: a dictionary that contains all the parameters for creating the loss function.
        """
        self._loss_type = loss_dict["type"]
        self._loss_dict = deepcopy(loss_dict)

    @property
    def loss_type(self):
        return self._loss_type

    @property
    def loss_dict(self):
        return self._loss_dict

    def build_loss(self):
        """The main method to get the loss object using functional programming. Here, we use the loss type to
        get the loss object.

        :return: a loss instance
        """
        delete_keys_from_dict(self.loss_dict, ["type"])
        try:
            return getattr(sys.modules[__name__], self.loss_type)(**self.loss_dict)
        except Exception as e:
            logging.critical(f"Unable to build the loss. The error is: {e}")
            sys.exit(1)

