# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Learner uses a callback/event handling mechanism to modify the train loops of deep learning models. This module
implements the main classes. The two classes "Event" and "EventManager" will always be sitting in this module but other
classes that handle different events may move to other modules."""
import math
import logging
from shutil import copyfile

import pandas as pd
import torch

from learner.utilities.templates import SAVE_MODEL_PATH, SAVE_MODEL_PATH_EPOCH, LEARNING_RATE
from learner.analysis.plot import Plot


class Callback:
    """The base class for all event handler classes. All of the event handler classes inherit from this class. This
    class has one method for all the events. This way, the child classes would only need to implement the relevant
    methods and the rest will be handled by the methods in the parent class."""
    def on_batch_end(self, *args, **kwargs):
        pass

    def on_epoch_end(self, *args, **kwargs):
        pass


class CallbackManager:
    """The EventManager class accepts a list of callback objects. This class implements all the methods of the Event
    class. In each method, this class loops through each object and calls the instance method identical to the caller
    method. For example, the method "on_epoch_end" would loop through all callback objects and would call the
    "on_epoch_end" method of those objects/instances"""
    def __init__(self, *callbacks):
        """Initialize an EventManager object using a list of callback instances.

        :param callbacks: a list of callback objects/instances
        """
        self.callbacks = callbacks

    def on_batch_end(self, *args, **kwargs):
        """Loop through the list of callbacks and call their on_epoch_end method.

        :param args: a tuple/list of positional arguments
        :param kwargs: a dictionary of keyword arguments
        :return: None
        """
        for callback in self.callbacks:
            callback.on_batch_end(*args, **kwargs)

    def on_epoch_end(self, *args, **kwargs):
        """Loop through the list of callbacks and call their on_epoch_end method.

        :param args: a tuple/list of positional arguments
        :param kwargs: a dictionary of keyword arguments
        :return: None
        """
        for callback in self.callbacks:
            callback.on_epoch_end(*args, **kwargs)


class MetricLogger(Callback):
    """A class to log the metrics and other information during the training and validation process."""
    def on_epoch_end(self, *args, **kwargs):
        """This method expects the keyword argument "metrics", which is a dictionary containing the metrics and their
        corresponding values. The metrics can be anything. Here, we iterate through each items to create a logging
        message. We then log that message. The items in the "metrics" dictionary would depend on the user input and
        other factors.

        :param args: a tuple/list of positional arguments
        :param kwargs: a dictionary of keyword arguments
        :return: None
        """
        message = ""
        for metric, value in kwargs["metrics"].items():
            if isinstance(value, int):
                message += f"{metric}: {value}\t"
            else:
                message += f"{metric}: {value:.10f}\t"
        logging.info(message)


class ModelSaver(Callback):
    """A class to save the trained model and other necessary information during the training process. The user can decide
    the frequency in which the models should be saved. Once those conditions are met, Learner saved the models."""
    def on_epoch_end(self, *args, **kwargs):
        """At the end of each epoch, we need to decide whether we should save the model or not. The user can define a
        parameter called "save_interval" to define the frequency of saving the models. This method needs a lot of
        keyword arguments such as "mdl", "conf", "tag", etc. The reason is that, Learner needs to be able to load the
        saved model and resume the training or make the predictions with minimum input from the user.

        :param args: a tuple/list of positional arguments
        :param kwargs: a dictionary of keyword arguments
        :return: None
        """
        if kwargs["mdl"]["params"]["save_interval"] and kwargs["epoch"] % kwargs["mdl"]["params"]["save_interval"] == 0:
            logging.info("Saving the model...")
            filename = SAVE_MODEL_PATH.format(
                path=kwargs["conf"].model.models_dict[kwargs["tag"]]["path"],
                output_name=kwargs["conf"].workspace.name,
                tag=kwargs["tag"],
                sep_timetag=str(kwargs["conf"].sep_timetag),
                ext=".pth"
            )
            epoch_filename = SAVE_MODEL_PATH_EPOCH.format(
                path=kwargs["conf"].model.models_dict[kwargs["tag"]]["path"],
                output_name=kwargs["conf"].workspace.name,
                tag=kwargs["tag"],
                epoch=kwargs["epoch"],
                sep_timetag=str(kwargs["conf"].sep_timetag),
                ext=".bck"
            )
            kwargs["mdl"]["model"] = kwargs["model"]
            torch.save({"conf": kwargs["conf"],
                        "tag": kwargs["tag"],
                        "mdl": kwargs["mdl"],
                        "processor": kwargs["processor"],
                        "feature_engineering": kwargs["feature_engineering"]},
                       filename)
            copyfile(filename, epoch_filename)


class LRFinder(Callback):
    """This callback class is used for finding the optimum learning rate. This class is only used when we want to find
    the learning rate. See this article for more details: https://sgugger.github.io/how-do-you-find-a-good-learning-rate.html"""
    def __init__(self, conf, scheduler, stop_div, tag, mdl):
        """Initializer a LRFinder object using the input arguments.

        :param conf: a conf object
        :param scheduler: a scheduler object. The scheduler must have the step method.
        :param stop_div: a flag to specify if we should stop when the loss starts to diverge.
        :param tag: the model tag, this is an arbitrary string defined by the user.
        :param mdl: an item of the models_dict.
        """
        self._conf = conf
        self._scheduler = scheduler
        self.best_loss = torch.tensor(0)
        self.stop_div = stop_div
        self.tag = tag
        self.mdl = mdl
        self.avg_loss = 0
        self.beta = 0.98
        self.data = {}

    @property
    def conf(self):
        return self._conf

    @property
    def scheduler(self):
        return self._scheduler

    def on_batch_end(self, *args, **kwargs):
        """At the end of each batch (not epoch), we'd need to compute the average loss, the smoothed loss, record the
        smoothed loss, and update the learning rate. If we are done or if the loss is diverging, we'd plot the loss as a
        function of learning rate and tell the trainer to stop.

        :param args: a tuple/list of positional arguments
        :param kwargs: a dictionary of keyword arguments
        :return: None
        """
        #  compute the smoothed loss
        self.avg_loss = self.beta * self.avg_loss + (1-self.beta) * kwargs["loss"].item()
        smoothed_loss = self.avg_loss / (1 - self.beta**(kwargs["iteration"] + 1))

        if kwargs["iteration"] == 0 or smoothed_loss < self.best_loss:
            self.best_loss = kwargs["loss"]
        self.record_data(smoothed_loss)
        self._scheduler.step()
        if self._scheduler.is_done or (self.stop_div and (smoothed_loss > 10 * self.best_loss or math.isnan(smoothed_loss))):
            df = self.get_df()
            self.plot_lr(df)
            kwargs["deep_trainer"].should_stop = True

    def record_data(self, smoothed_loss):
        """Update the data dictionary with adding the current learning rate and the smoothed loss.

        :param smoothed_loss: the value of the smoothed loss
        :return: None
        """
        self.data[self._scheduler.optimizer.param_groups[0]["lr"]] = smoothed_loss

    def get_df(self):
        """Convert the data dictionary to a pandas dataframe to make the plotting easier.

        :return: a pandas dataframe containing two columns: "lr" and "loss"
        """
        return pd.DataFrame(data=self.data.items(), columns=["lr", "loss"])

    def plot_lr(self, df):
        """Use the dataframe containing the learning rate and the loss and create a plot.

        :param df: a pandas dataframe containing two columns: "lr" and "loss"
        :return: None
        """
        plot_filename = LEARNING_RATE.format(
            path=self._conf.model.models_dict[self.tag]["path"],
            output_name=self._conf.workspace.name,
            tag=str(self.tag),
            sep_timetag=str(self._conf.sep_timetag))

        plot = Plot(self._conf)
        plot.learning_rate(df["lr"],
                           df["loss"],
                           filename=plot_filename)
