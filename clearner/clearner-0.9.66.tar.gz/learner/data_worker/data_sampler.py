# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for sampling the data. Currently, the main functionality include handling the imbalanced data for
classification problems using over or under-sampling techniques. This module should also handle other sampling related
tasks. Please note that, sampling the data for loading the training dataset is handled by data_loader module."""
import sys
import logging
import pandas as pd
from sklearn.model_selection import train_test_split

from learner.configuration.configuration import Configuration
from learner.data_worker.output_handler import OutputHandler


class DataSampler(object):
    """The main class to handle data_sampling tasks. The main driver method here is the sample_data."""
    def __init__(self, conf: Configuration, data: pd):
        """Instantiate a DataSampler object by providing a conf object and a reference to the training dataset.

        :param conf: an instance of the Configuration class
        :param data: a reference to the training dataset
        """
        self._conf = conf
        self.data = data
        # this hold the number of items in the majority class
        self.majority_count = None
        # this will be the label for the majority class (true or false, 0 or 1)
        self.majority_label = None
        # this will be the indices (true or false list) to identify the rows for the majority class
        self.majority_rows = None

        # the same as above but for the minority class
        self.minority_count = None
        self.minority_label = None
        self.minority_rows = None

        # these are the train and test indices if train_test_split was activated
        self.train_indices = None
        self.test_indices = None

    @property
    def conf(self):
        return self._conf

    def get_classes(self):
        """Get the information about the classes in the target columns. This is done by calling the value_counts method
        on the target column.

        :return: None
        """
        classes_df = self.data[self.conf.column.target_col].value_counts()
        num_classes = classes_df.shape[0]
        if num_classes != 2:
            logging.error("Learner only supports over/undersampling for binary classifications. Exiting...")
            sys.exit(1)
        # the class_df will be sorted, that's why this logic works
        self.majority_count = classes_df.iloc[0]
        self.majority_label = classes_df.index[0]
        self.minority_count = classes_df.iloc[1]
        self.minority_label = classes_df.index[1]

        logging.info(f"There are {self.majority_count} items for class {self.majority_label} and {self.minority_count} "
                     f"for class {self.minority_label}")

        # get the rows for the minority class
        self.minority_rows = self.data[self.conf.column.target_col] == self.minority_label
        self.majority_rows = self.data[self.conf.column.target_col] == self.majority_label

    def oversampling_handler(self):
        """Oversample the minority class to have as many as majority instances in the training data. To make this happen
        the minority class is being sampled with replacement. Note that this method does not add any noise to the data.
        That means the minority row are being duplicated in the training data.

        :return: None
        """
        # upsample the minority class to have as many as majority class instances (note that this only duplicates the
        # data)
        logging.info("Upsampling the minority class...")
        self.data = pd.concat([self.data[self.majority_rows],
                               self.data[self.minority_rows].sample(self.majority_count,
                                                                    replace=True,
                                                                    random_state=self.conf.sample.imbalanced_random_state)],
                              ignore_index=True)

    def undersampling_handler(self):
        """Under-sample the majority class to have as few as the minority class in the training dataset. Here, the
        majority rows are being sampled without replacement.

        :return: None
        """
        # sample the majority class (as many as the minority) and concatenate with minority
        logging.info("Undersampling the majority class...")
        self.data = pd.concat([self.data[self.majority_rows].sample(self.minority_count,
                                                                    replace=False,
                                                                    random_state=self.conf.sample.imbalanced_random_state),
                               self.data[self.minority_rows]],
                              ignore_index=True)

    def handle_random_train_test_split(self):
        """Randomly split the original train data into the new train and test data using the parameters provided. Then
        write the test data to disk so that Learner will use it when making predictions. Also, if requested, write the
        new train data to disk so that user can access it if needed.

        :return: None
        """
        logging.info("The number of rows for the original train_data: {nrows}".format(nrows=self.data.shape[0]))
        try:
            data, test_data = train_test_split(self.data,
                                               test_size=self.conf.sample.split_test_size,
                                               random_state=self.conf.sample.split_random_state,
                                               shuffle=self.conf.sample.split_shuffle,
                                               stratify=self.data[self.conf.sample.split_random_stratify]
                                               if self.conf.sample.split_random_stratify else None)

            self.test_indices = test_data.index
            self.train_indices = data.index
            if self.conf.sample.split_data:
                self.data = data
            self._write_split_data(test_data)
        except Exception as e:
            logging.error("Splitting the training data was unsuccessful. The error is {error}. Exiting".format(error=e))
            sys.exit(1)

    def handle_sort_train_test_split(self):
        """Split the training data into two date sets to use for training and testing using a date column.
        To make this work, we first convert the date column to datetime type. We then call the appropriate methods
        depending on the user input. If test_on_after is defined, we select the train and test data based on the dates
        provided by user otherwise we sort the training data by the date column and then split it.

        :return: None
        """
        nrows = self.data.shape[0]
        logging.info(f"The number of rows for the original train_data: {nrows}")
        try:
            # we need to convert the sort_col to a date type
            self.data[self.conf.sample.split_sort_col] = pd.to_datetime(self.data[self.conf.sample.split_sort_col],
                                                                        errors='coerce',
                                                                        infer_datetime_format=True)
            if self.conf.sample.split_test_on_after:
                data, test_data = self._handle_sort_split_using_dates()
            else:
                data, test_data = self._handle_sort_split_using_test_size()

            # if the user wants to shuffle train data, we do it here
            if self.conf.sample.split_shuffle:
                data = data.sample(frac=1, random_state=self.conf.sample.split_random_state)

            self.test_indices = test_data.index
            self.train_indices = data.index
            if self.conf.sample.split_data:
                self.data = data

            self._write_split_data(test_data)
        except Exception as e:
            logging.error("Splitting the training data was unsuccessful. The error is {error}. Exiting".format(error=e))
            sys.exit(1)

    def _handle_sort_split_using_dates(self):
        """Assuming that two dates are defined, we split the training data into two dataset. If one of those datasets
        are empty after the split, we issues an error.

        :return: the new training dataset and the test dataset
        """
        test_data = self.data[self.data[self.conf.sample.split_sort_col] >= self.conf.sample.split_test_on_after]
        data = self.data[self.data[self.conf.sample.split_sort_col] < self.conf.sample.split_train_before]
        if data.empty:
            logging.critical("""No data is left for training after train_test_split. Please update the configuration  
            file and try again. Exiting...""")
            sys.exit(1)

        if test_data.empty:
            logging.critical("""No data is left for testing after train_test_split. Please update the configuration  
            file and try again. Exiting...""")
            sys.exit(1)

        return data, test_data

    def _handle_sort_split_using_test_size(self):
        """Sort the training data set and split it into two datasets for training and testing. Issue an error if
        sampling leads to an empty dataset.

        :return: the new training dataset and the test dataset
        """
        nrows = self.data.shape[0]
        self.data.sort_values(by=self.conf.sample.split_sort_col,
                              ascending=True,
                              inplace=True,
                              na_position=self.conf.sample.split_sort_nan_position)

        # compute the number of rows we need for splitting
        # when split_test_size < 1, we need to get a fraction of data
        if self.conf.sample.split_test_size < 1:
            num_test_rows = int(self.data.shape[0] * self.conf.sample.split_test_size)
        else:
            num_test_rows = self.conf.sample.split_test_size

        data, test_data = (self.data.iloc[:nrows - num_test_rows, :],
                           self.data.iloc[nrows - num_test_rows:, :])
        if num_test_rows >= nrows:
            logging.critical("""test_size in train_test_split is greater than the number of rows in train data.
            Please update you configuration file by choosing a smaller number and try again. Exiting...""")
            sys.exit(1)
        return data, test_data

    def _write_split_data(self, test_data):
        """Write the test data to disk so that Learner can use it when making predictions. Also, if requested, write the
        new train data to disk so that user can access it if needed.

        :param test_data: the test_data to save to disk
        :return: None
        """
        logging.info("The number of rows for the train data after split: {nrows}".format(nrows=self.data.shape[0]))
        logging.info("The number of rows for the test data after split: {nrows}".format(nrows=test_data.shape[0]))

        logging.info("Writing the split test data in {filepath}"
                     .format(filepath=self.conf.workspace.data_directory + self.conf.data.sample_validation_filename))
        out = OutputHandler(self.conf)
        out.save_file(self.conf.workspace.data_directory,
                      self.conf.data.sample_validation_filename,
                      test_data,
                      add_timetag=False,
                      format=self.conf.data.validation_format,
                      sep=self.conf.data.test_delimiter)

        if self.conf.sample.split_save_train_data:
            logging.info("Writing the split train data in {filepath}"
                         .format(filepath=self.conf.workspace.data_directory + self.conf.data.sample_train_filename))

            out.save_file(self.conf.workspace.data_directory,
                          self.conf.data.sample_train_filename,
                          self.data,
                          add_timetag=False,
                          format=self.conf.data.train_format,
                          sep=self.conf.data.train_delimiter)

    def sample_data(self):
        """This is the main driver method for the DataSampler class. In general, this method is called after
        instantiating the object.

        :return: a reference to the training data
        """
        if self.conf.sample.split_activate and self.conf.sample.split_method == "random":
            self.handle_random_train_test_split()

        if self.conf.sample.split_activate and self.conf.sample.split_method == "sort":
            self.handle_sort_train_test_split()

        if self.conf.sample.imbalanced_activate:
            logging.info("Balancing the training data...")
            # we first populate the information on each class
            self.get_classes()
            getattr(self, self.conf.sample.imbalanced_method + "_handler")()
        return self.data
