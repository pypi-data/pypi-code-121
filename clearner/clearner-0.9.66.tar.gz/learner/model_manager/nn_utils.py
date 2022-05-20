# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements some utility functions and classes for the neural networks. These include freezing the
parameters of a network, finding the shape of the layers, etc."""


def freeze_params(model):
    """Accept a PyTorch model and freeze all the parameters by setting requires_grad to False.

    :param model: a PyTorch model
    :return: the updated model with all the parameters frozen.
    """
    for param in model.parameters():
        param.requires_grad = False
    return model


class ShapeFinder:
    """Find the size of the input data using a data_loader and the data_type. For example, if the data_type is "image",
    we'll find the height, the width, and the channel size of the input image. The main method is  find_initial_shape.
    This method calls the appropriate methods based on the data type"""
    def __init__(self, data_loader, data_type="image"):
        """Initialize a ShapeFinder object using a data_loader and the data_type. Currently, this only works for "image"
        data_type but we'll support other type as needed.

        :param data_loader: a data_loader object. We use this to get a batch of data.
        :param data_type: the data_type. Currently, we only support "image"
        """
        self.data_loader = data_loader
        self.data_type = data_type

    def find_initial_shape(self):
        """This is the main method. This method uses the data_type instance attribute to call the appropriate methods
        and find the shape of the data. It then directly returns the results from those methods.

        :return: the results that contain the shape of the input data. The results would depend on data_type.
        """
        return getattr(self, f"find_shape_for_{self.data_type}")()

    def find_shape_for_image(self):
        """For the image data, get a batch of data. Then use that batch to get the channel size, the height, and the
        width.

        :return: the channel size, the height, and the width of the images.
        """
        x, y = next(iter(self.data_loader))
        channel = x.shape[1]
        height = x.shape[2]
        width = x.shape[3]
        return channel, height, width

