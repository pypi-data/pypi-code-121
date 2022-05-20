# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for validating a data set against the requirements that are either defined in a separate
metadata file or provided by user in the configuration file"""

import sys
import warnings
import logging
import valideer as v
import numpy as np
import pandas as pd


class DataValidator:
    def __init__(self, conf, data: pd, data_type="train"):
        """Accept a dataset and a conf object to validate the data set against the information provided in the conf
        object

        :param conf: a conf object (an instance of the Configuration class in configuration module)
        :param data: a pandas dataframe
        :param data_type: the data type, it can be "train", "validation" or "test"
        """
        self._conf = conf
        self._data = data
        self._data_type = data_type

    @property
    def conf(self):
        return self._conf

    @property
    def data(self):
        return self._data

    @property
    def data_type(self):
        return self._data_type

    def validate_against_meta_data(self, meta_data):
        """Validate the data against a meta_data file

        :param meta_data: the meta_data file
        :return: None
        """
        logging.info("Validating the data against the meta_data file...")

        # loop through columns and create new dict with just column and schema needed for validation
        schema_dict = dict()
        for col in meta_data['column']:
            for key, value in meta_data['column'][col].items():
                if key == 'schema':
                    schema_dict[col] = [value]
                    
        val = v.parse(schema_dict)
        for col in self._data.columns:
            if not val.is_valid(self._data[[col]].dropna().to_dict('list')):
                raise Exception("Data in column {0} is Not Valid, type expected: {1}".format(col, schema_dict[col]))

        logging.info("Finished validating against meta_data...")

    @staticmethod
    def check_nulls_in_col(data, col):
        """Check if the target column has any missing values.

        :param data: a pandas dataframe
        :param col: the column to check for missing values. This is usually the target column
        :return: None
        """
        logging.info("Checking if the target contains missing values...")
        try:
            num_nulls = data[col].isnull().sum()
            if num_nulls:
                data.dropna(subset=[col], inplace=True)
                warnings.warn("The target column contains {0} rows with missing values. Those rows will be dropped "
                              "from the dataset".format(num_nulls), Warning)
                if data.empty:
                    logging.error("Looks like all values in the target column are missing, please check your data."
                                  " Exiting...")
                    sys.exit(1)

        except KeyError:
            logging.info("target_col is not in the data or not loaded. Skipping check_nulls_in_target...")

    def check_dtype_of_num_cols(self):
        """Ensure the columns passed as numerical columns are actually numeric. Learner only issues a warning if it
        finds out some columns are not numeric.

        :return: None
        """
        if self._conf.process.to_numeric_cols and self._conf.process.to_numeric_activate:
            logging.info("Checking data types of numerical columns...")
            # get columns with numeric datatypes
            numeric_columns_types = [np.issubdtype(self.data[col].dtype, np.number)
                                     for col in self._conf.process.to_numeric_cols]
            # first check to see any num_cols is defined, if not just return the data
            # if num_cols is defined, make sure all passed columns are of type number (int and float).
            if not all(numeric_columns_types):
                warnings.warn("Column(s) passed {0} can't be converted to numeric data type. This may cause some "
                              "errors. Check the data".format([col_name for col_name in self._conf.process.to_numeric_cols
                                                               if np.issubdtype(self.data[col_name].dtype, np.number)
                                                               is False]), UserWarning)

    def check_drop_from_train_includes_id_cols(self):
        """Check if drop_from_train columns include id_columns. If not issue a warning. This is important because the
        id columns should not usually be included in training.

        :return: None
        """
        logging.info("Checking if drop_from_train includes id_cols...")
        if self._conf.column.id_cols:
            diff = set(self._conf.column.id_cols) - set(self._conf.column.drop_from_train)
            if diff:
                warnings.warn("The columns {0} exist in id_cols but not in drop_from_train. This may affect the "
                              "trained model.".format(diff), UserWarning)

    def validate_data(self):
        """The main function that runs all the instance methods if the validation flag is set to true

        :return: None
        """
        logging.info("Validating the data")

        if self._conf.data.meta_data_file:
            self.validate_against_meta_data(self._conf.data.meta_data)

        # we care about nulls in target only when data_type is train or validation
        if self.data_type != "test":
            self.check_nulls_in_col(self.data, self._conf.column.target_col)
        self.check_dtype_of_num_cols()
        self.check_drop_from_train_includes_id_cols()
        logging.info("Successfully validated the data")
