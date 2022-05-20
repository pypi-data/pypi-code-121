# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for processing image data. Currently, this modules implement a ImageTransformer class. This class
builds a list of transforms to be passed to PyTorch's Compose class. This module is currently being used by the
image_classifier engine."""

from copy import deepcopy
import logging

from torchvision import transforms

from learner.data_worker.data_processor import delete_keys_from_dict


class ImageTransformer:
    """The ImageTransformer builds a list of transformation and passes that to the PyTorch's Compose class to create
    a transform object. That object is then passed to Dataset classes. The main method is build_transform.
    """
    def __init__(self, conf, data_type):
        """Initialize a ImageTransformer using a conf object and the data_type.

        :param conf: a conf object
        :param data_type: the data_type, this could be train, validation, or test.
        """
        self._conf = conf
        self._data_type = data_type
        self.keys_to_delete = ["type", "activate"]

    @property
    def conf(self):
        return self._conf

    @property
    def data_type(self):
        return self._data_type

    def build_transform(self):
        """The main method for building the transform list. This method uses the input provided by the user to create
        the necessary transform objects. Each method is aware of data_type value. The methods would return None if they
        should not create an object for a data_type value. That's why we check the value returned from the method
        before appending it to the list.

        :return: a Compose object to be passed to the Dataset classes
        """
        logging.info("Building image transformations...")
        transform_list = []
        if self._conf.process.image_transform_params:
            params = deepcopy(self._conf.process.image_transform_params)
            for param in params:
                transform = getattr(self, f"build_{param['type'].lower()}")(param)
                if transform:
                    transform_list.append(transform)
        return transforms.Compose(transform_list)

    def build_randomrotation(self, transform):
        if self._data_type != "train":
            return
        delete_keys_from_dict(transform, self.keys_to_delete)
        return transforms.RandomRotation(**transform)

    def build_randomhorizontalflip(self, transform):
        if self._data_type != "train":
            return
        delete_keys_from_dict(transform, self.keys_to_delete)
        return transforms.RandomHorizontalFlip(**transform)

    def build_resize(self, transform):
        delete_keys_from_dict(transform, self.keys_to_delete)
        return transforms.Resize(**transform)

    def build_centercrop(self, transform):
        delete_keys_from_dict(transform, self.keys_to_delete)
        return transforms.CenterCrop(**transform)

    def build_normalize(self, transform):
        delete_keys_from_dict(transform, self.keys_to_delete)
        return transforms.Normalize(**transform)

    def build_totensor(self, transform):
        return transforms.ToTensor()


