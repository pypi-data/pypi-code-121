# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This modules implements multiple classes to handle operations related to image data. This module communicates with
other data worker modules to load, validate, and process the image data. Currently, the image_classifier engine uses
the classes in this module"""

import logging

from learner.validator.input_validator import remove_subset_list
from torch.utils.data import DataLoader

from learner.data_worker.image_data_loader import ImageDataLoader
from learner.data_worker.data_set import LearnerTrainImageDataset, LearnerTestImageDataset
from learner.configuration.configuration import Configuration
from learner.data_worker.image_processor import ImageTransformer
from learner.data_worker.data_sampler import DataSampler


class TrainDataManager:
    """This class manages image the training data. The main method in this class is `get_data_loader` method. Unlike
    the class in data_manager module, we need to explicitly call the method to get the data_loader."""
    def __init__(self, conf: Configuration, mdl):
        """Initialize a TrainDataManager object using a conf object and an item in models_dict.

        :param conf: a conf object
        :param mdl: an item of models_dict. We use this to save the model classes.
        """
        self._conf = conf
        self._mdl = mdl

    @property
    def conf(self):
        return self._conf

    @property
    def mdl(self):
        return self._mdl

    def get_df(self):
        """Use the ImageDataLoader class to construct a dataframe from the image data.

        :return: a pandas dataframe that contains information about the path to the images and their corresponding label
        """
        loader = ImageDataLoader(self.conf, self.mdl)
        return loader.get_train_df()

    def get_transform(self):
        """Use the ImageTransformer class to build a Compose object for transforming the images.

        :return: a torchvision Compose object ready to be passed to a Dataset class
        """
        transform = ImageTransformer(self.conf, data_type="train").build_transform()
        return transform

    def get_dataset(self, df, transform):
        """Use LearnerTrainImageDataset class, the dataframe, and the transformer object to obtain a dataset object.

        :params: a pandas dataframe that contains information about the path to the images and their corresponding label
        :param: a torchvision Compose object ready to be passed to a Dataset class
        :return: a LearnerTrainImageDataset object
        """
        dataset = LearnerTrainImageDataset(df, path_col=self.conf.column.path_col, target_col=self.conf.column.target_col, transform=transform)
        return dataset

    def sample(self, df):
        """Since we build a pandas dataframe from all image data, we can also sample that dataframe, if needed, to
        create a validation dataset or reduce the size of the training data.

        :params: a pandas dataframe that contains information about the path to the images and their corresponding label
        :return: the sampled training dataframe
        """
        sample = DataSampler(self.conf, df)
        return sample.sample_data()

    def get_data_loader(self):
        """The main method for getting the train data loader. This method calls other methods in this class to obtain
        all the necessary information for creating a DataLoader object. This includes getting the dataframe, getting
        the transforms, and getting the dataset.

        :return: a PyTorch DataLoader object
        """
        logging.info("Getting the train data loader...")
        df = self.get_df()
        df = self.sample(df)
        transform = self.get_transform()
        dataset = self.get_dataset(df, transform)

        batch_size = self.mdl["params"]["batch_size"] if "batch_size" in self.mdl["params"] and self.mdl["params"]["batch_size"] else self.conf.data.train_batch_size
        return DataLoader(dataset, batch_size=batch_size, shuffle=True)


class ValidationDataManager:
    """This class manages image the validation data. The main method in this class is `get_data_loader` method. Unlike
    the class in data_manager module, we need to explicitly call the method to get the data_loader. The train and
    validation data have some similarities and some differences. For example, the validation data is accompanied by
    labels similar to training data but transformations are similar to the test data."""
    def __init__(self, conf, mdl):
        """Initialize a ValidationDataManager object using a conf object and an item in models_dict.

        :param conf: a conf object
        :param mdl: an item of models_dict. We use this to save the model classes.
        """
        self._conf = conf
        self._mdl = mdl

    @property
    def conf(self):
        return self._conf

    @property
    def mdl(self):
        return self._mdl

    def get_df(self):
        """Use the ImageDataLoader class to construct a dataframe from the image data.

        :return: a pandas dataframe that contains information about the path to the images and their corresponding label
        """
        loader = ImageDataLoader(self.conf, self.mdl)
        return loader.get_validation_df()

    def get_transform(self):
        """Use the ImageTransformer class to build a Compose object for transforming the images.

        :return: a torchvision Compose object ready to be passed to a Dataset class
        """
        transform = ImageTransformer(self.conf, data_type="validation").build_transform()
        return transform

    def get_dataset(self, df, transform):
        """Use LearnerTrainImageDataset class, the dataframe, and the transformer object to obtain a dataset object.
        Please note that we don't have a LearnerValidationImageDataset class because of the similarities between train
        and validation data. However, the transforms passed to the LearnerTrainImageDataset are built for validation
        data, which is different from the one for the training data.

        :params: a pandas dataframe that contains information about the path to the images and their corresponding label
        :param: a torchvision Compose object ready to be passed to a Dataset class
        :return: a LearnerTrainImageDataset object
        """
        dataset = LearnerTrainImageDataset(df, path_col=self.conf.column.path_col, target_col=self.conf.column.target_col, transform=transform)
        return dataset

    def get_data_loader(self):
        """The main method for getting the validation data loader. This method calls other methods in this class to
        obtain all the necessary information for creating a DataLoader object. This includes getting the dataframe,
        getting the transforms, and getting the dataset.

        :return: a PyTorch DataLoader object
        """
        logging.info("Getting the validation data loader...")
        df = self.get_df()
        transform = self.get_transform()
        dataset = self.get_dataset(df, transform)

        return DataLoader(dataset, batch_size=self.conf.data.validation_batch_size, shuffle=False)


class TestDataManager:
    """This class manages image the test data. The main method in this class is `get_data_loader` method. The test and
    validation data have some similarities and some differences. For example, the validation data is accompanied by
    labels unlike test data but transformations are similar."""
    def __init__(self, conf, mdl):
        """Initialize a TestDataManager object using a conf object and an item in models_dict.

        :param conf: a conf object
        :param mdl: an item of models_dict. We use this to save the model classes.
        """
        self._conf = conf
        self._mdl = mdl

    @property
    def conf(self):
        return self._conf

    @property
    def mdl(self):
        return self._mdl

    def get_df(self):
        """Use the ImageDataLoader class to construct a dataframe from the image data.

        :return: a pandas dataframe that contains information about the path to the images as well as some other columns
        """
        loader = ImageDataLoader(self.conf, self.mdl)
        return loader.get_test_df()

    def get_transform(self):
        """Use the ImageTransformer class to build a Compose object for transforming the images.

        :return: a torchvision Compose object ready to be passed to a Dataset class
        """
        transform = ImageTransformer(self.conf, data_type="test").build_transform()
        return transform

    def get_dataset(self, df, transform):
        """Use LearnerTestImageDataset class, the dataframe, and the transformer object to obtain a dataset object. The
        LearnerTestImageDataset behaves differently from the LearnerTrainImageDataset because there's no label in
        test data. Additionally, the LearnerTestImageDataset may need to return additional columns such as id columns
        from the data, which is different from train or validation data.

        :params: a pandas dataframe that contains information about the path to the images as well as some other columns
        :param: a torchvision Compose object ready to be passed to a Dataset class
        :return: a LearnerTestImageDataset object
        """
        cols = remove_subset_list(self.conf.column.valid_cols, [self.conf.column.target_col])
        dataset = LearnerTestImageDataset(df, path_col=self.conf.column.path_col, use_cols=cols, transform=transform)
        return dataset

    def get_data_loader(self):
        """The main method for getting the test data loader. This method calls other methods in this class to
        obtain all the necessary information for creating a DataLoader object. This includes getting the dataframe,
        getting the transforms, and getting the dataset.

        :return: a PyTorch DataLoader object
        """
        logging.info("Getting the test data loader...")
        df = self.get_df()
        transform = self.get_transform()
        dataset = self.get_dataset(df, transform)

        return DataLoader(dataset, batch_size=self.conf.data.test_batch_size, shuffle=False)
