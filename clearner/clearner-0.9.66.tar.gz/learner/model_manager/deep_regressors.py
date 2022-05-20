# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module includes Learner's deep regressors. The pattern for deep regressors is no different than the standard
regressirs. Here, we do not directly wrap sklearn models, etc.
"""

import sys
import abc
import logging

import torch
import torch.nn as nn

from learner.model_manager.layer_manager import LayerBuilder
from learner.model_manager.loss_manager import LossBuilder
from learner.model_manager.optimizer_manager import OptimizerBuilder
from learner.model_manager.scheduler_manager import SchedulerBuilder, LRFinderScheduler
from learner.model_manager.deep_loop_manager import DeepLoopManager
from learner.callback_manager.callback import MetricLogger, ModelSaver, LRFinder
from learner.data_worker.data_mover import move_to_device


class AbstractDeepRegressor:
    """The AbstractDeepRegressor class. This class does not implement any functionality, it defines the structure of
    the child classes.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):  # pragma: no cover
        self.mdl = None

    @staticmethod
    def learner_fit(tag, mdl, conf, train_loader, validation_loader):  # pragma: no cover
        pass

    @staticmethod
    def learner_predict(X, mdl, conf, carry_data=True, full_data=None, cols_to_carry=None):  # pragma: no cover
        pass

    @staticmethod
    def learner_find_learning_rate(tag, mdl, conf, train_loader):
        pass


class DeepRegressorHandler(AbstractDeepRegressor):
    """The handlers class calls the appropriate method of the Regressor classes for the type defined in mdl.
    """
    @abc.abstractmethod
    def __init__(self):
        super(AbstractDeepRegressor, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(tag, mdl, conf, train_loader, validation_loader):
        return getattr(sys.modules[__name__], mdl["type"]).learner_fit(tag, mdl, conf, train_loader, validation_loader)

    @staticmethod
    def learner_predict(X, mdl, device, carry_data=True, full_data=None, cols_to_carry=None):
        return getattr(sys.modules[__name__], mdl["type"]).learner_predict(X, mdl, device, carry_data, full_data, cols_to_carry)

    @staticmethod
    def learner_find_learning_rate(tag, mdl, conf, train_loader):
        return getattr(sys.modules[__name__], mdl["type"]).learner_find_learning_rate(tag, mdl, conf, train_loader)


class DeepRegressor:
    """The DeepRegressor class to build a deep learning regression model for tabular data.
    """
    @staticmethod
    def learner_fit(tag, mdl, conf, train_loader, validation_loader):
        """First, instantiate the LearnerDeepRegressor model. Then build the loss function, the optimizer, and
        the scheduler. After that, use DeepTrainManager class to train and validate the model. In the end, return the
        trained model.

        :param tag: the model tag, this is an arbitrary string defined by the user.
        :param mdl: an item of the models_dict.
        :param conf: a conf object
        :param train_loader: the train_loader to loop through the training data.
        :param validation_loader: the validation_loader to loop through the validation data.
        :return: the trained model.
        """
        model = LearnerDeepRegressor(conf=conf, mdl=mdl)
        criterion = LossBuilder(mdl["params"]["loss"]).build_loss()
        optimizer = OptimizerBuilder(list(model.parameters()), mdl["params"]["optimizer"]).build_optimizer()
        scheduler = SchedulerBuilder(mdl["params"]["scheduler"] if "scheduler" in mdl["params"] else None).build_scheduler(optimizer)

        train_manager = DeepLoopManager(conf,
                                        model,
                                        criterion,
                                        optimizer,
                                        scheduler,
                                        mdl["params"]["epochs"],
                                        tag=tag,
                                        mdl=mdl,
                                        train_loader=train_loader,
                                        validation_loader=validation_loader,
                                        callbacks=[MetricLogger(), ModelSaver()])
        train_manager.train()
        return model

    @staticmethod
    def learner_find_learning_rate(tag, mdl, conf, train_loader):
        """First, instantiate the LearnerDeepRegressor model. Then build the loss function and the optimizer.
        Set the initial learning rate of the optimizer using the parameter defined in learning_rate_params of the
        configuration file. Also, compute the number of epochs using the number of iterations needed and the number of
        batches in the train_loader. After that, use DeepTrainManager class to find the learning rate. Here, we pass
        the LRFinder callback to the DeepTrainManager class. This callback handles things related to the learning rate
        parameters such as stopping the training loop, etc. In the end, return the trained model.

        :param tag: the model tag, this is an arbitrary string defined by the user.
        :param mdl: an item of the models_dict.
        :param conf: a conf object
        :param train_loader: the train_loader to loop through the training data.
        :return: the trained model.
        """
        model = LearnerDeepRegressor(conf=conf, mdl=mdl)

        criterion = LossBuilder(mdl["params"]["loss"]).build_loss()
        # set the initial lr to be start_lr irrespective of what's being set
        mdl["params"]["optimizer"]["lr"] = conf.model.lr_start_lr
        # determine how many epochs we need depending on the size of data and num_iter
        mdl["params"]["epochs"] = int(conf.model.lr_num_it / len(train_loader)) + 1

        optimizer = OptimizerBuilder(list(model.parameters()),
                                     mdl["params"]["optimizer"]).build_optimizer()

        scheduler = LRFinderScheduler(optimizer=optimizer,
                                      start_lr=conf.model.lr_start_lr,
                                      end_lr=conf.model.lr_end_lr,
                                      num_it=conf.model.lr_num_it)

        train_manager = DeepLoopManager(conf,
                                        model,
                                        criterion,
                                        optimizer,
                                        scheduler,
                                        mdl["params"]["epochs"],
                                        tag=tag,
                                        mdl=mdl,
                                        train_loader=train_loader,
                                        callbacks=[MetricLogger(),
                                                    LRFinder(conf=conf,
                                                             scheduler=scheduler,
                                                             stop_div=conf.model.lr_stop_div,
                                                             tag=tag,
                                                             mdl=mdl)])
        train_manager.train()
        return model

    @staticmethod
    def learner_predict(X, mdl, device, carry_data=True, full_data=None, cols_to_carry=None):
        """Use the input data and a mdl dictionary along with other arguments to get the predictions. The value
        for the "model" key im mdl dictionary contains the trained model. This methods accepts the "device" argument
        as well. We move the data and the model to the appropriate device before making the predictions. This would
        enable making predictions using CPU or GPU.

        :param X: the input data for making the predictions.
        :param mdl: an item of the models_dict. This dictionary should contain the trained model.
        :param device: the device, this could be "cuda" or "cpu". The values are validated before they reach here.
        :param carry_data: a flag to indicate whether we should carry additional data or not.
        :param full_data: a pandas dataframe with additional data to send back if requested.
        :param cols_to_carry: The list of columns to select from the full dataset and send back if requested.
        :return: the predictions classes in numpy array as well as the selected columns from the data or None depending on the input.
        """
        logging.info("Making predictions using the %s model...", mdl["type"])
        with torch.no_grad():
            X = move_to_device(X, device)
            # put the model to evaluation mode. This is very important otherwise the results will not be correct
            mdl["model"].to(device).eval()
            pred = mdl["model"](*X).cpu()
            if carry_data:
                if full_data is not None and cols_to_carry:
                    return pred, full_data[cols_to_carry]
            return pred, None


class LearnerDeepRegressor(nn.Module):
    """The class to implement a deep regressor model from scratch using the parameters defined by the user. While the
    LearnerDeepRegressor model is quite flexible, it has a specific architecture. It passes all the categorical
    features through embedding layers and the continuous features through a batchnorm layer. It then concatenates the
    outputs and pass them through a series of fully connected layers. The user can/should define the size of the
    embedding layers and all the details about the fully connected layers."""

    def __init__(self, conf, mdl):
        """Initialize a LearnerDeepRegressor object using the input arguments.

        :param conf: a conf object.
        :param mdl: an item of models_dict.
        """
        super(LearnerDeepRegressor, self).__init__()
        self._conf = conf
        self._mdl = mdl

        self.embeddings = nn.ModuleList([nn.Embedding(num_input, num_features) for _, (num_input, num_features) in self._mdl["params"]["embedding_sizes"].items()])
        self.num_embeddings = sum(e.embedding_dim for e in self.embeddings)

        self.embeddings_dropout = nn.Dropout(self._mdl["params"]["embedding_dropout"])
        self.batchnorm_continuous = nn.BatchNorm1d(self._mdl["n_continuous"])

        layer_builder = LayerBuilder(raw_list=self._mdl["params"]["fully_connected_layers"],
                                     initial_size=self._mdl["n_continuous"] + self.num_embeddings)
        fully_connected_layers = layer_builder.build_layers()
        self.fully_connected_layers = nn.Sequential(*fully_connected_layers)

    def forward(self, x_cat, x_cont):
        """If there are categorical features, we pass them through embedding layers. If there are continuous features,
        we pass them through a single BatchNorm1d layer. Then we concatenate the output and pass it through the
        fully connected layer.

        :param x_cat: a PyTorch tensor containing the categorical features. These should contain the indices ready for embedding
        :param x_cont: a PyTorch tensor containing the continuous features. These should already be processes and normalized
        :return:
        """
        if self.num_embeddings != 0:
            x = [e(x_cat[:, i]) for i, e in enumerate(self.embeddings)]
            x = torch.cat(x, 1)
            x = self.embeddings_dropout(x)
        if self._mdl["n_continuous"] != 0:
            x_cont = self.batchnorm_continuous(x_cont)
            x = torch.cat([x, x_cont], 1) if self.num_embeddings != 0 else x_cont
        x = self.fully_connected_layers(x)
        # TODO: revisit this later since it could have performance impact
        x = x.double()
        x = torch.squeeze(x, 1)
        if self._mdl["params"]["y_range"] is not None:
            x = (self._mdl["params"]["y_range"][1] - self._mdl["params"]["y_range"][0]) * torch.sigmoid(x) + self._mdl["params"]["y_range"][0]
        return x
