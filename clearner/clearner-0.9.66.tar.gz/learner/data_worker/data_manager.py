# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Manage all the operations related to data. This module communicates with data worker modules to load,
validate, and process the data"""

import logging
from collections.abc import Iterable
import pandas as pd

from learner.data_worker.data_processor import DataProcessor
from learner.data_worker.data_loader import DataLoader, get_data, get_indices_for_value
from learner.data_worker.data_sampler import DataSampler
from learner.data_worker.output_handler import OutputHandler
from learner.feature_engineering.feature_engineering import FeatureEngineering
from learner.validator.data_validator import DataValidator
from learner.outlier_manager.outlier_manager import OutlierManager
from learner.data_worker.data_segmenters import SegmenterHandler
from learner.utilities.timer import timeit
from learner.validator.input_validator import remove_subset_list
from learner.analysis.analysis import Analysis


class TrainDataManager:
    """Handle loading, validating, and processing the train data."""

    def __init__(self, conf):
        """Accept a conf object (from the Configuration class), and handle loading, processing, and validating the
        train data.

        :param conf: a conf object
        """
        self._conf = conf
        self.data = None
        self.processor = None
        self.feature_engineering = None
        self.sample = None

        if self._conf.model.train_models:
            self.get_data()

    @property
    def conf(self):
        return self._conf

    @timeit("load the training data")
    def get_data(self):
        """Load the training data.

        :return: None
        """
        logging.info("Loading the train data...")
        loader = DataLoader(self._conf)
        self.data = loader.load_train_data()
        self.save_data()
        self.validate_data()
        self.analyze_data()
        self.sample_data()
        self.handle_outlier()
        self.process_data()
        self.handle_feature_engineering()
        segmenter_handler = SegmenterHandler(self._conf)
        segmenter_handler.handle_segmenter(self.data)

    @timeit("save the data")
    def save_data(self):
        """If requested by user, save the data obtained using the query into a file.

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
        self.feature_engineering = FeatureEngineering(self._conf)
        self.data = self.feature_engineering.handle_feature_engineering(self.data)


class ValidationDataManager:
    """Handle loading, validating, and processing the validation data."""

    def __init__(self, conf, processor=None, feature_engineering=None):
        """Accept a conf object (from the Configuration class), and handle loading, processing, and validating the
        train data.

        :param conf: a conf object
        :param processor: a DataProcessor object
        :param feature_engineering: a FeatureEngineering object
        """
        self._conf = conf
        self.data = None
        self.processor = processor
        self.feature_engineering = feature_engineering
        # we need the validation data only if we want to score the models
        self.get_data()

    @property
    def conf(self):
        return self._conf

    @timeit("load the validation data")
    def get_data(self):
        """Load the validation data.

        :return: None
        """
        logging.info("Loading the validation data...")
        loader = DataLoader(self._conf)
        self.data = loader.load_validation_data()
        self.save_data()
        self.validate_data()
        self.handle_outlier()
        self.process_data()
        self.handle_feature_engineering()
        segmenter_handler = SegmenterHandler(self._conf, data_type="validation")
        segmenter_handler.handle_segmenter(self.data)

    @timeit("save the data")
    def save_data(self):
        """If requested by user, save the data obtained using the query into a file.

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
        self.feature_engineering = FeatureEngineering(self._conf)
        self.data = self.feature_engineering.handle_feature_engineering(self.data)


class TestDataManager:
    """Handle loading, validating, and processing the test data."""

    # setting this so that pytest would not try to run this as a test
    __test__ = False

    def __init__(self, conf, processor=None, feature_engineering=None):
        """Accept a conf object (from the Configuration class), and handle loading, processing, and validating the
        test data through iteration.

        :param conf: a conf object
        :param processor: a DataProcessor object
        :param feature_engineering: a FeatureEngineering object
        """
        self._conf = conf
        self._file_nrows = None
        self.processor = processor
        self.feature_engineering = feature_engineering
        self.save_data()

    @property
    def conf(self):
        return self._conf

    @property
    def file_nrows(self):
        return self._file_nrows

    def save_data(self):
        """In some situations, we need to load the entire test data in memory and the save it into disk. These situations
        include using query and segmentation or using query and setting save_to_file to true. In those cases, use
        data loader to get the data and save it to a file.

        :return: None
        """
        # if requested or segmenter's been activated, we need to get all the test data and save it
        if (self._conf.data.test_query_activate and self._conf.data.test_query_save_to_file and self.conf.data.test_location is None) or \
           (self._conf.data.test_query_activate and self.conf.segmenter.activate and self.conf.data.test_location is None):
            format_ = self._conf.data.test_format
            logging.info(f"Getting the test data using the query and saving it into a {format_} file")
            loader = DataLoader(self._conf)
            data = loader.load_test_from_db()
            data = data[self.conf.column.use_cols] if self.conf.column.use_cols else data
            output = OutputHandler(self._conf)
            filename = f"test_data_from_query{self.conf.sep_timetag}.{format_}"
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
        """Use load_data to get a reader object or a list containing a single dataframe. When using binary file formats
        like parquet or feather, we have to load the entire data into memory because chunksize becomes irrelevant. Since
        the drivers iterate through the test data, we send a list (an iterable) so that the interface remains seamless.

        :return: TextFileReader object or a list
        """
        logging.info("Getting a reader to process the test data...")
        loader = DataLoader(self._conf)
        reader = loader.load_test_data()
        # If reader is an iterable and if it's not a pandas dataframe return it otherwise we will turn it into an
        # iterable (a list in this case) so we can treat all formats the same
        import pandas
        if isinstance(reader, Iterable) and not isinstance(reader, pd.DataFrame):
            return reader
        else:
            return [reader]

    def get_reader_data(self, chunk):
        """Validate, process, and return the processed dataset.

        :param chunk: a pandas dataframe
        :return: a processed pandas dataframe
        """
        # make sure we only keep use_cols if we are not reading from a file
        if not self._conf.data.test_location:
            chunk = chunk[remove_subset_list(self._conf.column.use_cols, [self._conf.column.target_col])]

        self.validate_data(chunk)
        _, chunk = self.process_data(chunk)
        chunk = self.handle_feature_engineering(chunk)
        segmenter_handler = SegmenterHandler(self._conf)
        segmenter_handler.handle_segmenter(chunk)
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

    def get_reader_for_segment(self, col, seg_border):
        """Get a TextFileReader (or a list containing a df) and obtain the indices for loading the test data in situations
        where there are multiple segments (the recommender engine currently makes use of this method).

        :param col: column name to process for getting test
        :param seg_border: the segment border
        :return: a TextFileReader (or a list containing a df) and a numpy array containing the indices in the entire dataset for seg id
        """
        logging.info("Getting a reader to process the test data...")

        data = get_data(self._conf.data.test_location,
                        manifest_file=self._conf.data.manifest,
                        format=self._conf.data.test_format,
                        sep=self._conf.data.test_delimiter,
                        nrows=self._conf.data.test_nrows,
                        usecols=[col],
                        header=self._conf.data.test_header)

        segmenter_handler = SegmenterHandler(self._conf)
        segmenter_handler.handle_segmenter(data)

        indices = get_indices_for_value(data, self._conf.segmenter.test_name, seg_border)

        logging.info(f"There are {len(indices)} rows of data in this segment")

        loader = DataLoader(self._conf)
        loader.connect_file(self._conf.data.test_location,
                            chunksize=self._conf.data.test_chunksize,
                            nrows=self._conf.data.test_nrows,
                            usecols=remove_subset_list(self._conf.column.use_cols, [self._conf.column.target_col]),
                            format=self._conf.data.test_format)

        if self._conf.data.test_format == "csv":
            return loader.df, indices
        else:
            return [loader.df], indices

