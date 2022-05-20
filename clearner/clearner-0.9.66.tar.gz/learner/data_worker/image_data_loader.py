# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements classes and functions for loading image data. The main class is ImageDataLoader. This class
uses other class and functions to identify and load image data. Learner uses a consistent approach for treating image
data. If the image data are organized in folders, Learner creates a dataframe to identify the path to the images and
their corresponding labels, if relevant. If a file is provided, Learner will read that file."""

import sys
import os

from torchvision import datasets
import pandas as pd

from learner.data_worker.data_loader import DataLoader


class ImageDataLoader(DataLoader):
    """A class to create a dataframe containing image path (and labels if relevant) from image data. This class
    implements three main methods to create dataframes for train, validation, and test data. Depending on the input
    type, i.e. "file" or "folder", the relevant classes and methods are used.
    """
    def __init__(self, conf, mdl):
        """Initialize a ImageDataLoader object using a conf object and an item in models_dict.

        :param conf: a conf object
        :param mdl: an item of models_dict. We use this to save the model classes.
        """
        super(ImageDataLoader, self).__init__(conf)
        self._conf = conf
        self._mdl = mdl

    @property
    def conf(self):
        return self._conf

    @property
    def mdl(self):
        return self._mdl

    def get_train_df(self):
        """Construct the dataframe corresponding to the train image data. If the input type is "folder", we use the
        DataFrameFromImageFolder class to get the dataframe. If the input type is "file", we use the parent method to
        obtain the dataframe.

        :return: a pandas dataframe that contains the path to the images and the corresponding labels.
        """
        if self._conf.data.train_input_type == "folder":
            df = DataFrameFromImageFolder(conf=self._conf, root=self._conf.data.train_location, data_type="train", mdl=self._mdl).get_df()
        else:
            df = self.load_train_from_file()
            self._mdl["classes"] = sorted(list(df[self._conf.column.target_col].unique()))
            from learner.data_worker.data_processor import LearnerLabelEncoder
            LearnerLabelEncoder().fit_transform(df, cols=[self._conf.column.target_col])
        return df

    def get_validation_df(self):
        """Construct the dataframe corresponding to the validation image data. If the input type is "folder", we use the
        DataFrameFromImageFolder class to get the dataframe. If the input type is "file", we use the parent method to
        obtain the dataframe.

        :return: a pandas dataframe that contains the path to the images and the corresponding labels.
        """
        if self._conf.data.validation_input_type == "folder":
            df = DataFrameFromImageFolder(conf=self._conf, root=self._conf.data.validation_location, data_type="validation", mdl=self._mdl).get_df()
        else:
            df = self.load_validation_from_file()
            self._mdl["classes"] = sorted(list(df[self._conf.column.target_col].unique()))
            from learner.data_worker.data_processor import LearnerLabelEncoder
            LearnerLabelEncoder().fit_transform(df, cols=[self._conf.column.target_col])
        return df

    def get_test_df(self):
        """Construct the dataframe corresponding to the test image data. If the input type is "folder", we use the
        DataFrameFromImageFolder class to get the dataframe. If the input type is "file", we use the parent method to
        obtain the dataframe.

        :return: a pandas dataframe that contains the path to the images. Unlike other methods, the test data does not have labels.
        """
        if self._conf.data.test_input_type == "folder":
            df = DataFrameFromImageFolder(conf=self._conf, root=self._conf.data.test_location, data_type="test").get_df()
        else:
            df = self.load_test_from_file(chunksize=None)
        return df


class DataFrameFromImageFolder:
    """A class to construct a pandas dataframe for an image folder. The assumption is that the images are arranged in
    the following patterns.

    /cat/1.jpg
    /cat/2.jpg

    /dog/1.jpg
    /dog/2.jpg

    This classes uses pytorch's functionality whenever possible. For example, supported image extensions comes from
    pytorch. We also use ImageFolder class of pytorch to get the dataframe for train and validation data.
    """
    def __init__(self, conf, root, data_type, mdl=None):
        """Initialize a DataFrameFromImageFolder object.

        :param conf: a conf object. It's mainly used for getting the column names.
        :param root: the path to the directory where all the subfolders are located.
        :param data_type: the data type, it should be "train", "test", or "validation".
        :param mdl: an item of models_dict dictionary.
        """
        self._conf = conf
        self._root = root
        self._data_type = data_type
        self._mdl = mdl
        self.extensions = datasets.folder.IMG_EXTENSIONS

    @property
    def conf(self):
        return self._conf

    @property
    def root(self):
        return self._root

    @property
    def data_type(self):
        return self._data_type

    @property
    def mdl(self):
        return self._mdl

    def get_df(self):
        """Depending on the data type, call the relevant method to obtain the dataframes.

        :return: The pandas dataframe that are returned by other methods.
        """
        if self.data_type == "test":
            return self.get_test_df()
        else:
            return self.get_train_validation_df()

    def get_test_df(self):
        """Leverage the function get_image_list_from_directory to get a list of images in the directory. Then, create
        a dataframe using that list.

        :return: a pandas dataframe with a column containing the path to all the images.
        """
        samples = get_image_list_from_directory(self.root, self.extensions)
        if len(samples) == 0:
            sys.exit(f"Found 0 files in {self.root}. Supported extensions are: {self.extensions}")
        return pd.DataFrame(samples, columns=[self._conf.column.path_col])

    def get_train_validation_df(self):
        """Use ImageFolder class from pytorch to get the list of images and labels. Then use that list to create the
        dataframe.

        :return: a pandas dataframe with three columns: the path column, the target column, and the classes (from the folder names).
        """
        validation_data = datasets.ImageFolder(root=self.root)
        self.mdl["classes"] = validation_data.classes
        df = pd.DataFrame(validation_data.samples, columns=[self._conf.column.path_col, self._conf.column.target_col])
        df["classes"] = df[self._conf.column.target_col].map({index: class_ for class_, index in validation_data.class_to_idx.items()})
        return df


def get_image_list_from_directory(directory, extensions):
    """Accept the path to a directory and the list of extensions (this usually comes from PyTorch) and return a list of
    paths to the images.

    :param directory: the path to the directory to look for the images
    :param extensions: the list of acceptable extensions
    :return: a list of paths to the images in the directory
    """
    def is_valid_file(x):
        return datasets.folder.has_file_allowed_extension(x, extensions)

    instances = []
    directory = os.path.expanduser(directory)

    for root, _, fnames in sorted(os.walk(directory, followlinks=True)):
        for fname in sorted(fnames):
            path = os.path.join(root, fname)
            if is_valid_file(path):
                instances.append(path)
    return instances

