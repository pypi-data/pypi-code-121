# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements all the dataset classes for tabular, image and potentially other data types. For tabular data,
we have a separate class for train, validation, and test data. For image data, one class handles train and validation
data and another one handles test data"""

from collections import OrderedDict

import torch
from torch.utils.data import Dataset
from torchvision import datasets

from learner.configuration.configuration import Configuration
from learner.data_worker.data_loader import remove_subset_list


class LearnerTrainTabularDataset(Dataset):
    """A dataset class for loading the train tabular data. This class would expect a pandas dataframe.
    """
    def __init__(self, df, conf: Configuration, mdl):
        """Initialize a LearnerTrainTabularDataset object using the input arguments. Here, we call the method
        _get_embedding_sizes to get the embedding sizes for the categorical features. We use the mdl to save all the
        necessary information that we may need later on.

        :param df: a pandas dataframe of the training data.
        :param mdl: an item (value) in models_dict.
        """
        self.df = df
        self.mdl = mdl
        self.conf = conf
        self._get_embedding_sizes()
        # it may not be necessary to use an OrderedDict here but just to be safe
        self.mdl["params"]["embedding_sizes"] = OrderedDict(self.mdl["params"]["embedding_sizes"])
        self.mdl["n_continuous"] = len(remove_subset_list(self.mdl["train_features"], self.mdl["params"]["embedding_sizes"].keys()))
        self._get_classes()

    @staticmethod
    def embedding_size_rule(n_cat):
        """Accept the number of categorical data and return the recommended size of the embedding layer for that
        feature. We've taken this from the fastai library. The user can define their own embedding size for each
        feature.

        :param n_cat: number of categories in the feature
        :return: the computed size for the embedding layer
        """
        return min(600, round(1.6 * n_cat ** 0.56))

    def _get_embedding_sizes(self):
        """First, we check if embedding_sizes is self.mdl["params"] is None or not. If it is (meaning that the user
        did not want to overwrite the default values) we set it to an empty dictionary (please see the in-line comment
        to understand why). We then iterate through each categorical column, to build the embedding_size dictionary.
        In this dictionary, the key is the name of the column. The values are tuples in which the first element is the
        input size and the second element is the embedding size like so: {"col1": (3, 4)}.

        :return: None
        """
        # this is important. For some reason, a default {} in the configuration would populate other mdl - super strange
        if self.mdl["params"]["embedding_sizes"] is None:
            self.mdl["params"]["embedding_sizes"] = {}
        for col in self.conf.process.label_encoding_cols:
            # if the user defines, embedding size for a column, we take it
            if self.mdl["params"]["embedding_sizes"] and col in self.mdl["params"]["embedding_sizes"]:
                # + 1 if for unseen levels
                self.mdl["params"]["embedding_sizes"][col] = (self.df[col].nunique() + 1,
                                                              self.mdl["params"]["embedding_sizes"][col])
            # if not, we compute it
            else:
                self.mdl["params"]["embedding_sizes"][col] = (self.df[col].nunique() + 1,
                                                              self.embedding_size_rule(self.df[col].nunique()))

    def _get_classes(self):
        """In DeepClassifier, we need to get the classes. We will use this information later on.

        :return: None
        """
        if self.conf.engine == "DeepClassifier":
            self.mdl["classes"] = sorted(list(self.df[self.conf.column.target_col].unique()))

    def __len__(self):
        """Get the number of items in the dataframe.

        :return: the number of items in the dataframe
        """
        return self.df.shape[0]

    def __getitem__(self, idx):
        """In deep engines, we need to separate continuous and categorical features because we do embedding for
        categorical features. Here, we get the target, categorical, and continuous features given the index. For the
        features we return a list. This is important to remember. We use the embedding sizes dictionary to find the
        categorical features. We then convert the features into PyTorch tensors. We could potentially convert the
        target into a tensor but that's not needed.

        :param idx: the index of the item, this is the row number.
        :return: a tuple where the first item is a list of categorical and continuous features and the second item is the target.
        """
        # at ensures the dtype remains unchanged
        target = self.df.at[idx, self.conf.column.target_col]
        cat_features = self.df.iloc[idx][self.mdl["params"]["embedding_sizes"].keys()]
        cont_features = self.df.iloc[idx][remove_subset_list(self.mdl["train_features"],
                                                             self.mdl["params"]["embedding_sizes"].keys())]

        return [torch.tensor(cat_features).long(), torch.tensor(cont_features).float()], target


class LearnerValidationTabularDataset(Dataset):
    """A dataset class for loading the validation tabular data. This class would expect a pandas dataframe. Unlike the
    Image dataset classes, we need a separate class for the validation tabular data because in train dataset we get the
    embedding sizes and we use that in the validation and test datasets.
    """
    def __init__(self, df, conf: Configuration, mdl):
        """Initialize a LearnerValidationTabularDataset object using the input arguments. Here, assume that the
        embedding sizes dictionary for the categorical features is already populated. We use the mdl to save all the
        necessary information that we may need later on.

        :param df: a pandas dataframe of the training data.
        :param mdl: an item (value) in models_dict.
        """
        self.df = df
        self.mdl = mdl
        self.conf = conf

    def __len__(self):
        """Get the number of items in the dataframe.

        :return: the number of items in the dataframe
        """
        return self.df.shape[0]

    def __getitem__(self, idx):
        """In deep engines, we need to separate continuous and categorical features because we do embedding for
        categorical features. Here, we get the target, categorical, and continuous features given the index. For the
        features we return a list. This is important to remember. We use the embedding sizes dictionary to find the
        categorical features. We then convert the features into PyTorch tensors. We could potentially convert the
        target into a tensor but that's not needed.

        :param idx: the index of the item, this is the row number.
        :return: a tuple where the first item is a list of categorical and continuous features and the second item is the target.
        """
        # at ensures the dtype remains unchanged
        target = self.df.at[idx, self.conf.column.target_col]
        cat_features = self.df.iloc[idx][self.mdl["params"]["embedding_sizes"].keys()]
        cont_features = self.df.iloc[idx][remove_subset_list(self.mdl["train_features"],
                                                             self.mdl["params"]["embedding_sizes"].keys())]

        return [torch.tensor(cat_features).long(), torch.tensor(cont_features).float()], target


class LearnerTestTabularDataset(Dataset):
    """A dataset class for loading the test tabular data. This class would expect a pandas dataframe. The difference
    between the validation and test dataset is that the test dataset does not expect/load any targets.
    """
    def __init__(self, df, conf: Configuration, mdl):
        """Initialize a LearnerTestImageDataset object using the input arguments.

        :param df: a pandas dataframe that contains the path to the images and their corresponding label.
        :param mdl: an item (value) in models_dict.
        """
        self.df = df
        self.mdl = mdl
        self.conf = conf

    def __len__(self):
        """Get the number of items in the dataframe.

        :return: the number of items in the dataframe
        """
        return self.df.shape[0]

    def __getitem__(self, idx):
        """In deep engines, we need to separate continuous and categorical features because we do embedding for
        categorical features. Here, we get the categorical continuous features given the index. For the
        features we return a list. This is important to remember. We use the embedding sizes dictionary to find the
        categorical features. We then convert the features into PyTorch tensors. Here, unlike train and validation
        datasets, we return all the raw data as well. This data is used later on to return additional data if requested.

        :param idx: the index of the item, this is the row number.
        :return: a tuple where the first item is a list of categorical and continuous features and the second item is the target.
        """
        cols = remove_subset_list(self.conf.column.valid_cols, [self.conf.column.target_col])
        data = self.df[cols].iloc[idx].to_dict()
        cat_features = self.df.iloc[idx][self.mdl["params"]["embedding_sizes"].keys()]
        cont_features = self.df.iloc[idx][remove_subset_list(self.mdl["train_features"],
                                                             self.mdl["params"]["embedding_sizes"].keys())]

        return [torch.tensor(cat_features).long(), torch.tensor(cont_features).float()], data


class LearnerTrainImageDataset(Dataset):
    """A dataset class for loading the train and validation image data. This class uses a pandas dataframe to
    identify and load images along with their corresponding labels.
    """
    def __init__(self, df, path_col, target_col, transform=None):
        """Initialize a LearnerTrainImageDataset object using the input arguments.

        :param df: a pandas dataframe that contains the path to the images and their corresponding label.
        :param path_col: the column that contains the path to the images.
        :param target_col: the columns that contains the label.
        :param transform: a Compose object from pytorch. This is prepared by other classes/module and depend on user input.
        """
        self.df = df
        self.transform = transform
        self.path_col = path_col
        self.target_col = target_col

    def __len__(self):
        """Get the number of items in the dataframe.

        :return: the number of items in the dataframe
        """
        return self.df.shape[0]

    def __getitem__(self, idx):
        """Load a single image from the dataframe given the index. If transform is defined, pass the PIL.Image.Image
        object through the transform. In the end, return the image data and the corresponding label.

        :param idx: the index of the item, this is the row number.
        :return: the image data and the corresponding label.
        """
        path, target = self.df.iloc[idx][[self.path_col, self.target_col]]
        sample = datasets.folder.default_loader(path)
        if self.transform is not None:
            sample = self.transform(sample)
        return sample, target


class LearnerTestImageDataset(Dataset):
    """A dataset class for loading the test image data. This class uses a pandas dataframe to identify and load images.
     This class returns the image data as well as additional data. The additional data is returned in dictionary format
     because of the limitation imposed by PyTorch. That data is converted to dataframe at a later time.
    """
    def __init__(self, df, path_col, use_cols=None, transform=None):
        """Initialize a LearnerTestImageDataset object using the input arguments.

        :param df: a pandas dataframe that contains the path to the images and their corresponding label.
        :param path_col: the column that contains the path to the images.
        :param use_cols: the additional columns that should be returned from the dataframe.
        :param transform: a Compose object from pytorch. This is prepared by other classes/module and depend on user input.
        """
        self.df = df
        self.path_col = path_col
        self.use_cols = use_cols
        self.transform = transform

    def __len__(self):
        """Get the number of items in the dataframe.

        :return: the number of items in the dataframe
        """
        return self.df.shape[0]

    def __getitem__(self, idx):
        """Load a single image from the dataframe given the index. If transform is defined, pass the PIL.Image.Image
        object through the transform. We also get the additional columns from the data. In the end, return the image
        data and the additional data.

        :param idx: the index of the item, this is the row number.
        :return: the image data and the corresponding label.
        """
        path = self.df.iloc[idx][self.path_col]
        data = self.df.iloc[idx][self.use_cols].to_dict()
        sample = datasets.folder.default_loader(path)
        if self.transform is not None:
            sample = self.transform(sample)
        return sample, data
