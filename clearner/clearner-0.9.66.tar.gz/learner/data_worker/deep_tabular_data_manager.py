# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This modules implements multiple classes to handle operations related to tabular data for deep engines, i.e.
deep_classifier and deep_regressor engines. This module communicates with other data worker modules to load, validate,
and process the data and create datasets, etc."""

import logging

from torch.utils.data import DataLoader

from learner.configuration.configuration import Configuration
from learner.data_worker.data_processor import DataProcessor
from learner.data_worker.data_sampler import DataSampler
from learner.data_worker.output_handler import OutputHandler
from learner.data_worker.data_set import (LearnerTrainTabularDataset, LearnerValidationTabularDataset,
                                          LearnerTestTabularDataset)
from learner.feature_engineering.feature_engineering import FeatureEngineering
from learner.validator.data_validator import DataValidator
from learner.outlier_manager.outlier_manager import OutlierManager
from learner.utilities.timer import timeit
from learner.validator.input_validator import remove_subset_list
from learner.analysis.analysis import Analysis


class TrainDataManager:
    """This class manages the training data for deep engines. The main method in this class is `get_data_loader` method.
    Unlike the class in data_manager module, we need to explicitly call that method to get the data_loader."""

    def __init__(self, conf: Configuration, mdl=None):
        """Initialize a TrainDataManager object using a conf object and an item in models_dict.

        :param conf: a conf object
        :param mdl: an item of models_dict. We use this to save the model classes.
        """
        self._conf = conf
        self._mdl = mdl
        self.data = None
        self.processor = None
        self.feature_engineering = None
        self.sample = None

    @property
    def conf(self):
        return self._conf

    @property
    def mdl(self):
        return self._mdl

    @timeit("load the training data")
    def get_data(self):
        """Load the training data. Then, do all the validation, processing, and feature engineering. The method
        `get_data_loader` calls this method. Please note that we import the learner DataLoader class here to avoid name
        conflicts with the PyTorch class.

        :return: None
        """
        logging.info("Loading the train data...")
        from learner.data_worker.data_loader import DataLoader
        loader = DataLoader(self._conf)
        self.data = loader.load_train_data()
        self.save_data()
        self.validate_data()
        self.analyze_data()
        self.sample_data()
        self.handle_outlier()
        self.process_data()
        self.handle_feature_engineering()

    @timeit("save the data")
    def save_data(self):
        """If requested by user, save the data obtained using the query into a csv file.

        :return: None
        """
        if self._conf.data.train_query_activate and self._conf.data.train_query_save_to_file:
            format_ = self._conf.data.train_format
            logging.info(f"Saving the train data obtained from the query into a {format_} file")
            output = OutputHandler(self._conf)
            filename = f"train_data_from_query{self.conf.sep_timetag}.{format_}"
            output.save_file(self.conf.workspace.data_directory,
                             filename,
                             self.data,
                             add_timetag=False,
                             format=format_,
                             sep=self.conf.data.train_delimiter)
            logging.info("Successfully saved the train data into the data directory")

    @timeit("filter the outliers")
    def handle_outlier(self):
        """Instantiate an outlier manager object and make the call to handle_outlier to get the updated data.

        :return: None
        """
        outlier_manager = OutlierManager(self._conf, self.data)
        self.data = outlier_manager.handle_outlier()

    @timeit("validate the training data")
    def validate_data(self):
        """Validate the data

        :return: None
        """
        if self._conf.validation.validate:
            validator = DataValidator(self._conf, self.data, data_type="train")
            validator.validate_data()

    @timeit("analyze the training data")
    def analyze_data(self):
        """Analyze the data

        :return: None
        """
        analysis = Analysis(self._conf)
        analysis.analyze_data(self.data)

    @timeit("sample the training data")
    def sample_data(self):
        """Sample the training data if necessary. Note that we may not need to sample the data in many situations. In
        that case, the driver method (sample_data) would make the decision.

        :return: the updated training dataset
        """
        self.sample = DataSampler(self.conf, self.data)
        self.data = self.sample.sample_data()

    @timeit("process the training data")
    def process_data(self):
        """Process the data. Data processing is carried out based on the user's instructions in the configuration file.

        :return: None
        """
        self.processor = DataProcessor(self._conf)
        self._conf, self.data = self.processor.process_data(self.data)

    def handle_feature_engineering(self):
        """Instantiate an object of the FeatureEngineering class and pass the data to the handle_feature_engineering
        method to do any requested feature engineering.

        :return: None
        """
        self.feature_engineering = FeatureEngineering(self._conf)
        self.data = self.feature_engineering.handle_feature_engineering(self.data)

    def get_dataset(self, df):
        """Use LearnerTrainTabularDataset class and the dataframe to obtain a dataset object. Please see the
        documentation of the dataset class to read more.

        :params: a pandas dataframe that contains information about the path to the images and their corresponding label
        :return: a LearnerTrainTabularDataset object
        """
        dataset = LearnerTrainTabularDataset(df, conf=self.conf, mdl=self.mdl)
        return dataset

    def get_data_loader(self):
        """The main method for getting the train data loader. This method calls other methods in this class to obtain
        all the necessary information for creating a DataLoader object. This includes getting the dataframe and
        the dataset. We also update the mdl dictionary but populating a list of training features.

        :return: a PyTorch DataLoader object
        """
        logging.info("Getting the train data loader...")
        self.get_data()
        # save the train_features
        self.mdl["train_features"] = remove_subset_list(list(self.data.drop(self._conf.column.drop_from_train, axis=1).columns),
                                                        [self._conf.column.target_col])
        dataset = self.get_dataset(self.data)

        batch_size = self.mdl["params"]["batch_size"] if "batch_size" in self.mdl["params"] and self.mdl["params"]["batch_size"] else self.conf.data.train_batch_size
        return DataLoader(dataset, batch_size=batch_size, shuffle=True)


class ValidationDataManager:
    """This class manages the validation data for deep engines. The main method in this class is the `get_data_loader`
    method.  Unlike the class in data_manager module, we need to explicitly call that method to get the data_loader."""

    def __init__(self, conf, mdl, processor=None, feature_engineering=None):
        """Initialize a ValidationDataManager object using a conf object, an item in models_dict, as well as the
        processor and feature_engineering objects.

        :param conf: a conf object
        :param processor: a DataProcessor object
        :param feature_engineering: a FeatureEngineering object
        """
        self._conf = conf
        self._mdl = mdl
        self.data = None
        self.processor = processor
        self.feature_engineering = feature_engineering

    @property
    def conf(self):
        return self._conf

    @property
    def mdl(self):
        return self._mdl

    @timeit("load the validation data")
    def get_data(self):
        """Load the training data. Then, do all the validation, processing, and feature engineering. The method
        `get_data_loader` calls this method. Please note that we import the learner DataLoader class here to avoid name
        conflicts with the PyTorch class.

        :return: None
        """
        logging.info("Loading the validation data...")
        from learner.data_worker.data_loader import DataLoader
        loader = DataLoader(self._conf)
        self.data = loader.load_validation_data()
        self.save_data()
        self.validate_data()
        self.handle_outlier()
        self.process_data()
        self.handle_feature_engineering()

    @timeit("save the data")
    def save_data(self):
        """If requested by user, save the data obtained using the query into a csv file.

        :return: None
        """
        if self._conf.data.validation_query_activate and self._conf.data.validation_query_save_to_file:
            format_ = self._conf.data.validation_format
            logging.info(f"Saving the validation data obtained from the query into a {format_} file")
            output = OutputHandler(self._conf)
            filename = f"validation_data_from_query{self.conf.sep_timetag}.{format_}"
            output.save_file(self.conf.workspace.data_directory,
                             filename,
                             self.data,
                             add_timetag=False,
                             format=format_,
                             sep=self.conf.data.train_delimiter)
            logging.info("Successfully saved the validation data into the data directory")

    @timeit("filter the outliers")
    def handle_outlier(self):
        """Instantiate an outlier manager object and make the call to handle_outlier to get the updated data.

        :return: None
        """
        outlier_manager = OutlierManager(self._conf, self.data)
        self.data = outlier_manager.handle_outlier()

    @timeit("validate the validation data")
    def validate_data(self):
        """Validate the data

        :return: None
        """
        if self._conf.validation.validate:
            validator = DataValidator(self._conf, self.data, data_type="validation")
            validator.validate_data()

    @timeit("process the validation data")
    def process_data(self):
        """Process the data. Data processing is carried out based on the user's instructions in the configuration file.

        :return: None
        """
        self._conf, self.data = self.processor.process_data(self.data)

    def handle_feature_engineering(self):
        """Instantiate an object of the FeatureEngineering class and pass the data to the handle_feature_engineering
        method to do any requested feature engineering.

        :return: None
        """
        self.feature_engineering = FeatureEngineering(self._conf)
        self.data = self.feature_engineering.handle_feature_engineering(self.data)

    def get_dataset(self, df):
        """Use LearnerValidationTabularDataset class and the dataframe to obtain a dataset object. Please see the
        documentation of the dataset class to read more.

        :params: a pandas dataframe that contains information about the path to the images and their corresponding label
        :return: a LearnerValidationTabularDataset object
        """
        dataset = LearnerValidationTabularDataset(df, conf=self.conf, mdl=self.mdl)
        return dataset

    def get_data_loader(self):
        """The main method for getting the validation data loader. This method calls other methods in this class to
        obtain all the necessary information for creating a DataLoader object. This includes getting the dataframe and
        the dataset.

        :return: a PyTorch DataLoader object
        """
        logging.info("Getting the validation data loader...")
        self.get_data()
        dataset = self.get_dataset(self.data)

        return DataLoader(dataset, batch_size=self.conf.data.validation_batch_size, shuffle=False)


class TestDataManager:
    """This class manages the test data for deep engines. Because we need to be able handle dataset of any sizes, this
    class works slightly different from the train and validation classes. Here, we get data reader and chunk of data
    first. We then pass that chunk of data to get a data loader. We then iterate through the reader object so that we
    load a limited amount of data at a time."""

    # setting this so that pytest would not try to run this as a test
    __test__ = False

    def __init__(self, conf, processor=None, feature_engineering=None):
        """Initialize a TestDataManager object using a conf object as well as the processor and feature_engineering
        objects.

        :param conf: a conf object
        :param processor: a DataProcessor object
        :param feature_engineering: a FeatureEngineering object
        """
        self._conf = conf
        self.processor = processor
        self.feature_engineering = feature_engineering
        self.save_data()

    @property
    def conf(self):
        return self._conf

    def save_data(self):
        """In some situations, we need to load the entire test data in memory and the save it into disk. These
        situations include using query and segmentation or using query and setting save_to_file to true. In those cases,
        use data loader to get the data and save it to a csv file.

        :return: None
        """
        # if requested or segmenter's been activated, we need to get all the test data and save it
        if (self._conf.data.test_query_activate and self._conf.data.test_query_save_to_file) or \
           (self._conf.data.test_query_activate and self.conf.segmenter.activate):
            format_ = self._conf.data.test_format
            logging.info(f"Getting the test data using the query and saving it into a {format_} file")
            from learner.data_worker.data_loader import DataLoader
            loader = DataLoader(self._conf)
            data = loader.load_test_from_db()
            data = data[self.conf.column.use_cols] if self.conf.column.use_cols else data
            output = OutputHandler(self._conf)
            filename = f"test_data_from_query{self.conf.sep_timetag}.csv"
            output.save_file(self.conf.workspace.data_directory,
                             filename,
                             data,
                             add_timetag=False,
                             format=format_,
                             sep=self.conf.data.test_delimiter)
            logging.info("Successfully saved the test data into the data directory. Learner will use this file for "
                         "making predictions moving forward")
            self.conf.data.test_location = self.conf.workspace.data_directory + filename

    def get_reader(self):
        """Use load_test_data to get a TextFileReader object

        :return: TextFileReader object
        """
        logging.info("Getting a reader to process the test data...")
        from learner.data_worker.data_loader import DataLoader
        loader = DataLoader(self._conf)
        reader = loader.load_test_data()
        # when using csv files, reader is an iterable otherwise is the full df. We return an iterable (a list in this
        # case) so we can treat all formats the same
        if self._conf.data.test_format == "csv":
            return reader
        else:
            return [reader]

    def get_reader_data(self, chunk):
        """Validate, process, and return the processed dataset for a chunk.

        :param chunk: a pandas dataframe
        :return: a processed pandas dataframe
        """
        # make sure we only keep use_cols if we are not reading from a file
        if not self._conf.data.test_location:
            chunk = chunk[remove_subset_list(self._conf.column.use_cols, [self._conf.column.target_col])]

        self.validate_data(chunk)
        _, chunk = self.process_data(chunk)
        chunk = self.handle_feature_engineering(chunk)
        return chunk

    def validate_data(self, data):
        """Validate the data.

        :param data: a pandas dataframe
        :return: None
        """
        if self._conf.validation.validate:
            validator = DataValidator(self._conf, data, data_type="test")
            validator.validate_data()

    def process_data(self, data):
        """Process the data. Data processing is carried out based on user input in the config file.

        :param data: a pandas dataframe to be processed
        :return: a processed pandas dataframe
        """
        # we'd probably never need to check this
        if self.processor is None:
            self.processor = DataProcessor(self._conf)
        _, data = self.processor.process_data(data)
        return _, data

    def handle_feature_engineering(self, chunk):
        """Get a chunk and run it through various feature_engineering processes.

        :param chunk: a pandas dataframe loaded in memory
        :return: the updated dataframe after feature engineering
        """
        if self.feature_engineering is None:
            self.feature_engineering = FeatureEngineering(self._conf)
        chunk = self.feature_engineering.handle_feature_engineering(chunk)
        return chunk

    def get_dataset(self, chunk, mdl):
        """Use LearnerTestTabularDataset class, the dataframe, and an item of models_dict to obtain a dataset object.
        Please see the documentation of the dataset class to read more.

        :param chunk: a pandas dataframe that contains the loaded data
        :param mdl: an item (value) in models_dict.
        :return: a LearnerTestTabularDataset object
        """
        dataset = LearnerTestTabularDataset(chunk, conf=self.conf, mdl=mdl)
        return dataset

    def get_data_loader(self, chunk, mdl):
        """The method for getting the test data loader for a chunk of data. Unlike the train and validation data, this
        is not the main class. Here, we need to provide that loaded data as an argument. The `get_reader_data` method
        handles loading and processing the data.

        :param chunk: a pandas dataframe that contains the loaded data
        :param mdl: an item (value) in models_dict.
        :return: a PyTorch DataLoader object
        """
        logging.info("Getting the test data loader...")
        dataset = self.get_dataset(chunk, mdl)
        return DataLoader(dataset, batch_size=self.conf.data.test_batch_size, shuffle=False)
