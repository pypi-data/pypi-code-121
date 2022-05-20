# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements classes and functions for building the layers for neural network models. Currently, this
module implements the LayerBuilder class. In the future, we'll most likely implement a parent class and let more
specialized classes inherit from it."""
import sys
from copy import deepcopy
import logging

import torch.nn as nn

from learner.data_worker.data_processor import delete_keys_from_dict


class LayerBuilder:
    """The class to build a list of neural network layers using a "raw" list that contains the necessary information
    and parameters for building those layers. The main method here is build_layers. This method calls other methods to
    build the layers"""
    def __init__(self, raw_list, initial_size, height=100, width=100):
        """Initialize a LayerBuilder object using the input parameters.

        :param raw_list: a list that contains all the necessary parameters to construct the layers
        :param initial_size: the size for building the layers. This is typically the size of input layer
        :param height: the height of the images, if applicable
        :param width: the width of the images, if applicable
        """
        self._initial_size = initial_size
        self.running_size = initial_size
        self.height = height
        self.width = width
        self.running_flatten_size = initial_size * height * width
        self._raw_list = raw_list

    @property
    def initial_size(self):
        return self._initial_size

    @property
    def raw_list(self):
        return self._raw_list

    def build_layers(self):
        """The main method for building the list of the layers. Here, we iterate through the raw list and using
        functional programming, we build one layer at a time.

        :return:
        """
        layer_list = []
        # make a copy because we may alter the list and want to keep the original list intact
        raw_list = deepcopy(self.raw_list)
        try:
            for i, layer in enumerate(raw_list):
                layer_list.append(getattr(self, f"build_{layer['type'].lower()}")(i, layer))
            return layer_list
        except Exception as e:
            logging.critical(f"Unable to build the layers. The error is {e}")
            sys.exit(1)

    def build_linear(self, index, layer):
        """Build a Linear layer. If we are building the first layer, use the initial size to set in_features parameter,
        otherwise use the running_size. Before returning the layer, set the running_size to out_features.

        :param index: the index of the layer, 0, 1, 2, ...
        :param layer: a dictionary that contains all the parameters.
        :return: a Linear object with the proper parameters
        """
        # if we are building the first layer, we need to know the initial size. If not, our input
        # is our running size
        if index == 0:
            in_features = self.initial_size
        else:
            in_features = self.running_size
        self.running_size = layer["out_features"]
        delete_keys_from_dict(layer, ["type"])
        return nn.Linear(in_features=in_features, **layer)

    def build_relu(self, index, layer):
        """Build a ReLu activation layer.

        :param index: the index of the layer, 0, 1, 2, .... This is not used here.
        :param layer: a dictionary that contains all the parameters. This is not used here.
        :return: a ReLu object
        """
        return nn.ReLU()

    def build_softmax(self, index, layer):
        """Build a Softmax activation layer.

        :param index: the index of the layer, 0, 1, 2, .... This is not used here.
        :param layer: a dictionary that contains all the parameters.
        :return: a Softmax object
        """
        delete_keys_from_dict(layer, ["type"])
        return nn.Softmax(**layer)

    def build_logsoftmax(self, index, layer):
        """Build a LogSoftmax activation layer.

        :param index: the index of the layer, 0, 1, 2, .... This is not used here.
        :param layer: a dictionary that contains all the parameters.
        :return: a LogSoftmax object
        """
        delete_keys_from_dict(layer, ["type"])
        return nn.LogSoftmax(**layer)

    @staticmethod
    def build_dropout(index, layer):
        """Build a dropout layer.

        :param index: the index of the layer, 0, 1, 2, .... This is not used here.
        :param layer: a dictionary that contains all the parameters.
        :return: a Dropout object
        """
        delete_keys_from_dict(layer, ["type"])
        return nn.Dropout(**layer)

    def build_conv2d(self, index, layer):
        """Build a Conv2d layer. If we are at the first layer, we use the initial_size to set the in_channel. If not,
        the running_size is our in_channel. Once, the layer is built, out_channel will be our running_size. We also,
        use the running_size, height, and width to get the running_flatten_size. This value can be used when connecting
        the convolutional layers to the fully connected layers. This method also calculates the height and width of the
        output images. This way, the user won't have to figure out those numbers. This commonly is a source of
        frustration for many people.

        :param index: the index of the layer, 0, 1, 2, ...
        :param layer: a dictionary that contains all the parameters.
        :return: a Conv2d object
        """
        # if we are building the first layer, we need to know the initial size. If not, our input
        # is our running size
        if index == 0:
            in_channels = self.initial_size
        else:
            in_channels = self.running_size

        self.running_size = layer["out_channels"]
        self.height = int((self.height + 2 * layer["padding"] - layer["dilation"] * (layer["kernel_size"] - 1) - 1) / layer["stride"] +1)
        self.width = int((self.width + 2 * layer["padding"] - layer["dilation"] * (layer["kernel_size"] - 1) - 1) / layer["stride"] +1)
        self.running_flatten_size = self.running_size * self.height * self.width
        delete_keys_from_dict(layer, ["type"])
        return nn.Conv2d(in_channels=in_channels, **layer)

    def build_maxpool2d(self, index, layer):
        """Build a MaxPool2d layer. We first compute the height and the width of the output images. We then use those
        numbers to compute the running_flatten_size. We then return the layer.

        :param index: the index of the layer, 0, 1, 2, ...
        :param layer: a dictionary that contains all the parameters.
        :return: a MaxPool2d object.
        """
        self.height = int((self.height + 2 * layer["padding"] - layer["dilation"] * (layer["kernel_size"] - 1) - 1) / layer["stride"] +1)
        self.width = int((self.width + 2 * layer["padding"] - layer["dilation"] * (layer["kernel_size"] - 1) - 1) / layer["stride"] +1)
        self.running_flatten_size = int(self.running_size * self.height * self.width)
        delete_keys_from_dict(layer, ["type"])
        return nn.MaxPool2d(**layer)

    def build_batchnorm1d(self, index, layer):
        """Build a BatchNorm1d layer. We set the num_features to the running_size. This layer does not change the
        running_size.

        :param index: the index of the layer, 0, 1, 2, ...
        :param layer: a dictionary that contains all the parameters.
        :return: a BatchNorm1d object with the proper parameters
        """
        delete_keys_from_dict(layer, ["type"])
        return nn.BatchNorm1d(num_features=self.running_size, **layer)
