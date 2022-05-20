# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module includes Learner's image classifiers. The pattern for image classifiers is no different than the
statndard classifiers. Here, we do not directly wrap sklearn models, etc. We write our own classes to wrap fastai's
implementations.
"""

import sys
import abc
import logging

import numpy as np
from torchvision.models.alexnet import alexnet
from torchvision.models.vgg import vgg11, vgg11_bn, vgg13, vgg13_bn, vgg16, vgg16_bn, vgg19, vgg19_bn
from torchvision.models.densenet import densenet121, densenet161, densenet169, densenet201
from torchvision.models.mobilenetv2 import mobilenet_v2
from torchvision.models.mobilenetv3 import mobilenet_v3_large, mobilenet_v3_small
from torchvision.models.mnasnet import mnasnet0_5, mnasnet1_0
from torchvision.models.resnet import resnet18, resnet34, resnet50, resnet101, resnet152, resnext50_32x4d, resnext101_32x8d, wide_resnet50_2, wide_resnet101_2
from torchvision.models.googlenet import googlenet
from torchvision.models.shufflenetv2 import shufflenet_v2_x0_5, shufflenet_v2_x1_0
import torch
import torch.nn as nn
from torch.nn.functional import softmax

from learner.model_manager.layer_manager import LayerBuilder
from learner.model_manager.loss_manager import LossBuilder
from learner.model_manager.optimizer_manager import OptimizerBuilder
from learner.model_manager.scheduler_manager import SchedulerBuilder, LRFinderScheduler
from learner.model_manager.nn_utils import freeze_params
from learner.model_manager.deep_loop_manager import DeepLoopManager
from learner.model_manager.nn_utils import ShapeFinder
from learner.callback_manager.callback import MetricLogger, ModelSaver, LRFinder


# these are the size of the last "features" layer after flattening them.
model_to_size = {"AlexNet": 9216,
                 "VGG11": 25088,
                 "VGG11_BN": 25088,
                 "VGG13": 25088,
                 "VGG13_BN": 25088,
                 "VGG16": 25088,
                 "VGG16_BN": 25088,
                 "VGG19": 25088,
                 "VGG19_BN": 25088,
                 "ResNet18": 512,
                 "ResNet34": 512,
                 "ResNet50": 2048,
                 "ResNet101": 2048,
                 "ResNet152": 2048,
                 "DenseNet121": 1024,
                 "DenseNet161": 2208,
                 "DenseNet169": 1664,
                 "DenseNet201": 1920,
                 "GoogLeNet": 1024,
                 "ShuffleNet_V2_x0_5": 1024,
                 "ShuffleNet_V2_x1_0": 1024,
                 "ShuffleNet_V2_x2_0": 1024,
                 "MobileNet_V2": 1280,
                 "MobileNet_V3_Large": 960,
                 "MobileNet_V3_Small": 576,
                 "ResNext50_32x4d": 2048,
                 "ResNext101_32x8d": 2048,
                 "Wide_ResNet50_2": 2048,
                 "Wide_ResNet101_2": 2048,
                 "MNASNet0_5": 1280,
                 "MNASNet1_0": 1280,
                 }

mdl_to_head = {"ImageClassifier": "classifier",
               "AlexNet": "classifier",
               "VGG11": "classifier",
               "VGG11_BN": "classifier",
               "VGG13": "classifier",
               "VGG13_BN": "classifier",
               "VGG16": "classifier",
               "VGG16_BN": "classifier",
               "VGG19": "classifier",
               "VGG19_BN": "classifier",
               "ResNet18": "fc",
               "ResNet34": "fc",
               "ResNet50": "fc",
               "ResNet101": "fc",
               "ResNet152": "fc",
               "DenseNet121": "classifier",
               "DenseNet161": "classifier",
               "DenseNet169": "classifier",
               "GoogLeNet": "fc",
               "ShuffleNet_V2_x0_5": "fc",
               "ShuffleNet_V2_x1_0": "fc",
               "DenseNet201": "classifier",
               "MobileNet_V2": "classifier",
               "MobileNet_V3_Large": "classifier",
               "MobileNet_V3_Small": "classifier",
               "ResNext50_32x4d": "fc",
               "ResNext101_32x8d": "fc",
               "Wide_ResNet50_2": "fc",
               "Wide_ResNet101_2": "fc",
               "MNASNet0_5": "classifier",
               "MNASNet1_0": "classifier",
               }


class AbstractImageClassifier:
    """The AbstractImageClassifier class. This class does not implement any functionality; it defines the structure of
    the child classes.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):  # pragma: no cover
        self.mdl = None

    @staticmethod
    def learner_fit(tag, mdl, conf, train_loader, validation_loader):  # pragma: no cover
        pass

    @staticmethod
    def learner_predict(X, mdl, device, carry_data=True, full_data=None, cols_to_carry=None):  # pragma: no cover
        pass

    @staticmethod
    def learner_predict_proba(X, mdl, device, carry_data=True, full_data=None, cols_to_carry=None):  # pragma: no cover
        pass

    @staticmethod
    def learner_find_learning_rate(tag, mdl, conf, train_loader):
        pass


class ImageClassifierHandler(AbstractImageClassifier):
    """The handlers class calls the appropriate method of the image classifier classes with the appropriate arguments.
    """
    @abc.abstractmethod
    def __init__(self):
        super(AbstractImageClassifier, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(tag, mdl, conf, train_loader, validation_loader):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_fit(tag, mdl, conf, train_loader, validation_loader)
        except AttributeError:
            return StandardImageClassifier.learner_fit(tag, mdl, conf, train_loader, validation_loader)

    @staticmethod
    def learner_predict(test_data, mdl, device, carry_data=True, full_data=None, cols_to_carry=None):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_predict(test_data, mdl, device, carry_data, full_data, cols_to_carry)
        except AttributeError:
            return StandardImageClassifier.learner_predict(test_data, mdl, device, carry_data, full_data, cols_to_carry)

    @staticmethod
    def learner_predict_proba(test_data, mdl, device, carry_data=True, full_data=None, cols_to_carry=None):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_predict_proba(test_data, mdl, device, carry_data, full_data, cols_to_carry)
        except AttributeError:
            return StandardImageClassifier.learner_predict_proba(test_data, mdl, device, carry_data, full_data, cols_to_carry)

    @staticmethod
    def learner_find_learning_rate(tag, mdl, conf, train_loader):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_find_learning_rate(tag, mdl, conf, train_loader)
        except AttributeError:
            return StandardImageClassifier.learner_find_learning_rate(tag, mdl, conf, train_loader)


class StandardImageClassifier(AbstractImageClassifier):
    """A class for the standard methods of the image classifiers. These currently include learner_predict and
    learner_predict_proba methods. If a image classifier does not have these methods implemented, it would fall here.
    This way we won;t have to implement similar methods for all the image classifier models."""
    def __init__(self):
        super(AbstractImageClassifier, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(tag, mdl, conf, train_loader, validation_loader):
        """First, instantiate the model from PyTorch. If needed, freeze the parameters. Then replace the
        classifier attribute, build the loss function, and the optimizer. After that, use DeepTrainManager class to
        train and validate the model. In the end, return the trained model.

        :param tag: the model tag, this is an arbitrary string defined by the user.
        :param mdl: an item of the models_dict.
        :param conf: a conf object
        :param train_loader: the train_loader to loop through the training data.
        :param validation_loader: the validation_loader to loop through the validation data.
        :return: the trained model.
        """
        # instantiate the model
        model = getattr(sys.modules[__name__], mdl["type"].lower())(pretrained=True)
        # freeze the parameters if requested
        if mdl["params"]["freeze_features"]:
            model = freeze_params(model)

        layers = LayerBuilder(raw_list=mdl["params"]["classifier"], initial_size=model_to_size[mdl["type"]]).build_layers()

        setattr(model, mdl_to_head[mdl["type"]], nn.Sequential(*layers))
        params_to_update = list(getattr(model, mdl_to_head[mdl["type"]]).parameters())

        criterion = LossBuilder(mdl["params"]["loss"]).build_loss()
        optimizer = OptimizerBuilder(params_to_update if mdl["params"]["freeze_features"] else list(model.parameters()), mdl["params"]["optimizer"]).build_optimizer()
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
        """First, instantiate the model from PyTorch. If needed, freeze the parameters. Then replace the
        classifier attribute, build the loss function, and the optimizer. Set the initial learning rate of the optimizer
        using the parameter defined in learning_rate_params of the configuration file. Also, compute the number of
        epochs using the number of iterations needed and the number of batches in the train_loader. After that,
        use DeepTrainManager class to find the learning rate. Here, we pass the LRFinder callback to the
        DeepTrainManager class. This callback handles things related to the learning rate parameters such as stopping
        the training loop, etc. In the end, return the trained model.

        :param tag: the model tag, this is an arbitrary string defined by the user.
        :param mdl: an item of the models_dict.
        :param conf: a conf object
        :param train_loader: the train_loader to loop through the training data.
        :return: the trained model.
        """
        # instantiate the model
        model = getattr(sys.modules[__name__], mdl["type"].lower())(pretrained=True)
        # freeze the parameters if requested
        if mdl["params"]["freeze_features"]:
            model = freeze_params(model)

        layers = LayerBuilder(raw_list=mdl["params"]["classifier"], initial_size=model_to_size[mdl["type"]]).build_layers()

        setattr(model, mdl_to_head[mdl["type"]], nn.Sequential(*layers))
        params_to_update = list(getattr(model, mdl_to_head[mdl["type"]]).parameters())

        criterion = LossBuilder(mdl["params"]["loss"]).build_loss()
        # set the initial lr to be start_lr irrespective of what's being set
        mdl["params"]["optimizer"]["lr"] = conf.model.lr_start_lr
        # determine how many epochs we need depending on the size of data and num_iter
        mdl["params"]["epochs"] = int(conf.model.lr_num_it / len(train_loader)) + 1

        optimizer = OptimizerBuilder(params_to_update if mdl["params"]["freeze_features"] else list(model.parameters()),
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
        """Use the input data and a mdl dictionary along with other arguments to get the class predictions. The value
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
        with torch.no_grad():
            X = X.to(device)
            # put the model to evaluation mode. This is very important otherwise the results will not be correct
            mdl["model"].to(device).eval()
            pred = mdl["model"](X)
            # if the activation is LogSoftmax, do the exponential to get the probabilities
            if isinstance(getattr(mdl["model"], mdl_to_head[mdl["type"]])[-1], torch.nn.LogSoftmax):
                pred = torch.exp(pred)
            # if activation is not LogSoftmax and not Softmax, we need to pass it through a softmax function to get
            # the probabilities
            if not isinstance(getattr(mdl["model"], mdl_to_head[mdl["type"]])[-1], torch.nn.LogSoftmax) and \
               not isinstance(getattr(mdl["model"], mdl_to_head[mdl["type"]])[-1], torch.nn.Softmax):
                pred = torch.nn.functional.softmax(pred, dim=1)

            pred = np.argmax(pred.cpu(), 1)
            if carry_data:
                if full_data is not None and cols_to_carry:
                    return pred, full_data[cols_to_carry]
            return pred, None

    @staticmethod
    def learner_predict_proba(X, mdl, device, carry_data=True, full_data=None, cols_to_carry=None):
        """Use the input data and a mdl dictionary along with other arguments to get the predicted probabilities.
        The value for the "model" key im mdl dictionary contains the trained model. This methods accepts the "device"
        argument as well. We move the data and the model to the appropriate device before making the predictions.
        This would enable making predictions using CPU or GPU.

        :param X: the input data for making the predictions.
        :param mdl: an item of the models_dict. This dictionary should contain the trained model.
        :param device: the device, this could be "cuda" or "cpu". The values are validated before they reach here.
        :param carry_data: a flag to indicate whether we should carry additional data or not.
        :param full_data: a pandas dataframe with additional data to send back if requested.
        :param cols_to_carry: The list of columns to select from the full dataset and send back if requested.
        :return: the predictions classes in numpy array as well as the selected columns from the data or None depending on the input.
        """
        with torch.no_grad():
            X = X.to(device)
            # put the model to evaluation mode. This is very important otherwise the results will not be correct
            mdl["model"].to(device).eval()
            pred = mdl["model"](X).cpu()
            # if the activation is LogSoftmax, do the exponential to get the probabilities
            if isinstance(getattr(mdl["model"], mdl_to_head[mdl["type"]])[-1], torch.nn.LogSoftmax):
                pred = torch.exp(pred)
            # if activation is not LogSoftmax and not Softmax, we need to pass it through a softmax function to get
            # the probabilities
            if not isinstance(getattr(mdl["model"], mdl_to_head[mdl["type"]])[-1], torch.nn.LogSoftmax) and \
               not isinstance(getattr(mdl["model"], mdl_to_head[mdl["type"]])[-1], torch.nn.Softmax):
                pred = torch.nn.functional.softmax(pred, dim=1)

            if carry_data:
                if full_data is not None and cols_to_carry:
                    if len(mdl["classes"]) == 2:
                        return pred[:, 1], full_data[cols_to_carry]
                    else:
                        return pred, full_data[cols_to_carry]
            if len(mdl["classes"]) == 2:
                return pred[:, 1], None
            return pred, None


class ImageClassifier:
    """A class for building an image classifier model from the scratch. This class leverages LearnerImageClassifier
    to get the model object. The learner_fit is the main method here
    """

    @staticmethod
    def learner_fit(tag, mdl, conf, train_loader, validation_loader):
        """First, we need to get the dimensions of the images to pass them to the LearnerImageClassifier class.
        Since we are building the model from the scratch as opposed to transfer learning, we won't freeze
        the parameters. We then build the loss function and the optimizer. After that, we use
        DeepTrainManager class to train and validate the model. In the end, we return the trained model.

        :param tag: the model tag, this is an arbitrary string defined by the user.
        :param mdl: an item of the models_dict.
        :param conf: a conf object
        :param train_loader: the train_loader to loop through the training data.
        :param validation_loader: the validation_loader to loop through the validation data.
        :return: the trained model.
        """
        channel, height, width = ShapeFinder(train_loader, data_type="image").find_initial_shape()
        # instantiate the model
        model = LearnerImageClassifier(conf=conf, mdl=mdl, channel=channel, height=height, width=width)

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
        """First, we need to get the dimensions of the images to pass them to the LearnerImageClassifier class.
        Since we are building the model from the scratch as opposed to transfer learning, we won't freeze
        the parameters. We then build the loss function and the optimizer. We set the initial learning rate of the
        optimizer using the parameter defined in learning_rate_params of the configuration file. Also, compute the
        number of epochs using the number of iterations needed and the number of batches in the train_loader. After
        that, use DeepTrainManager class to find the learning rate. Here, we pass the LRFinder callback to the
        DeepTrainManager class. This callback handles things related to the learning rate parameters such as stopping
        the training loop, etc. In the end, return the trained model.

        :param tag: the model tag, this is an arbitrary string defined by the user.
        :param mdl: an item of the models_dict.
        :param conf: a conf object
        :param train_loader: the train_loader to loop through the training data.
        :return: the trained model.
        """
        channel, height, width = ShapeFinder(train_loader, data_type="image").find_initial_shape()
        # instantiate the model
        model = LearnerImageClassifier(conf=conf, mdl=mdl, channel=channel, height=height, width=width)

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


class LearnerImageClassifier(nn.Module):
    """The class to implement an image classifier model from scratch using the architecture defined by the user. The
    image classifier model has two major attributes namely the "features" and the "classifier"."""
    def __init__(self, conf, mdl, channel, height, width):
        """Initialize a LearnerImageClassifier object using the input arguments.

        :param conf: a conf object.
        :param mdl: an item of models_dict.
        :param channel: the number of channels of the input image.
        :param height: the height of the image.
        :param width: the width of the image.
        """
        super(LearnerImageClassifier, self).__init__()
        self._conf = conf
        self._mdl = mdl
        self._channel = channel
        self._height = height
        self._width = width
        layer_builder = LayerBuilder(raw_list=self._mdl["params"]["features"],
                                     initial_size=self._channel,
                                     height=self._height,
                                     width=self._width)
        features = layer_builder.build_layers()
        self.features = nn.Sequential(*features)

        classifier = LayerBuilder(raw_list=self._mdl["params"]["classifier"],
                                  initial_size=layer_builder.running_flatten_size).build_layers()

        self.classifier = nn.Sequential(*classifier)

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
