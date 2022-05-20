# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements the scheduler classes and functions. This includes the SchedulerBuilder class to create the
general scheduler objects as well as the LRFinderScheduler the custom scheduler for finding the learning rate. The main
difference between the general scheduler and the LRFinder is how they've been used. The LRFinderScheduler is merely used
for finding the learning rates. Unlike other scheduler, the step method is LRFinder called after each bach and not after
each epoch."""
import sys
from copy import deepcopy
import logging

from torch.optim.lr_scheduler import StepLR, MultiStepLR, CosineAnnealingLR, ExponentialLR, ReduceLROnPlateau, CyclicLR, CosineAnnealingWarmRestarts

from learner.data_worker.data_processor import delete_keys_from_dict


class SchedulerBuilder:
    """The class to functionally build the scheduler objects depending on the user input. The main method here is
    build_scheduler. This method uses the type of the scheduler and the parameters to instantiate the corresponding
    object.
    """
    def __init__(self, scheduler_dict):
        """Initialize a SchedulerBuilder object using the scheduler_dict. This dictionary contains all the parameters
        as well as the type of scheduler. The type is the value of the "type" key.

        :param scheduler_dict: the dictionary that contains the type of the scheduler as well as the necessary parameters.
        """
        self._scheduler_type = scheduler_dict["type"] if scheduler_dict else None
        self._scheduler_dict = deepcopy(scheduler_dict)

    @property
    def scheduler_type(self):
        return self._scheduler_type

    @property
    def scheduler_dict(self):
        return self._scheduler_dict

    def build_scheduler(self, optimizer):
        """The main method to get the scheduler object using functional programming. Here, we use the scheduler type to
        get the scheduler object.

        :param optimizer: an optimizer object
        :return: the scheduler object ready to be used during the training.
        """
        if self.scheduler_dict:
            delete_keys_from_dict(self.scheduler_dict, ["type"])
            try:
                return getattr(sys.modules[__name__], self.scheduler_type)(optimizer, **self.scheduler_dict)
            except Exception as e:
                logging.critical(f"Unable to build the scheduler. The error is: {e}")
                sys.exit(1)


class LRFinderScheduler:
    """The scheduler to use when finding the learning rate. This uses a similar logic as the fastai library. The
    original paper can be found here: https://arxiv.org/abs/1506.01186. Here's a useful blog about fastai
    implementation: https://sgugger.github.io/how-do-you-find-a-good-learning-rate.html"""
    def __init__(self, optimizer, start_lr, end_lr, num_it):
        """Initialize a LRFinderScheduler using the input parameters. The majority of the input parameters are defined
        in the configuration file by the user.

        :param optimizer: an optimizer object. We will use this object to update the learning rate.
        :param start_lr: the starting point for the learning rate probe.
        :param end_lr: the end point for the learning rate probe.
        :param num_it: the number of iteration when probing the learning rate. We exponentially go from start_lr to end_lr in this many itertions
        """
        self._optimizer = optimizer
        self._start_lr = start_lr
        self._end_lr = end_lr
        self._num_it = num_it
        self.it = 0

    @property
    def optimizer(self):
        return self._optimizer

    @property
    def start_lr(self):
        return self._start_lr

    @property
    def end_lr(self):
        return self._end_lr

    @property
    def num_it(self):
        return self._num_it

    def step(self):
        """Take one step to update the learning rate. In this schedule we update the learning rate after each batch. We
        first calculate the learning rate depending on the iteration we are at. We will then update the learning rate of
        the optimizer.

        :return: None
        """
        self.it += 1
        lr = self.start_lr * (self.end_lr / self.start_lr) ** (self.it/self.num_it)
        for group in self.optimizer.param_groups:
            group["lr"] = lr

    @property
    def is_done(self):
        """Determine if we have reached the end of the scheduler. This happens when are at or above the number of
        iterations we need.

        :return: true is we've reached the end, false otherwise
        """
        return self.it >= self.num_it
