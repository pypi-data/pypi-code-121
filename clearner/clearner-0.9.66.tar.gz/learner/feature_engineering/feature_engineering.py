# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module to drive the feature engineering operations."""

import logging
import warnings
import numpy as np

from learner.data_worker.data_processor import DataProcessor


class FeatureEngineering:
    """The main feature engineering class that implements the methods for performing feature engineering tasks."""

    def __init__(self, conf):
        self._conf = conf
        self._processor = None
        self._learner_groupby = None

    @property
    def conf(self):
        return self._conf

    @property
    def processor(self):
        return self._processor

    @property
    def learner_groupby(self):
        return self._learner_groupby

    def basic_operations(self, data):
        """Loop through each item in basic_operations and make the call to appropriate methods to perform basic
        operations feature engineering including addition, subtraction, multiplication, and division.

        :param data: the data frame
        :return: the updated data frame
        """
        for item in self._conf.feature_engineering.basic_operations_params:
            data = getattr(self, item["method"])(item, data)
        return data

    def division(self, item, data):
        """Divide a sequence of columns to create a new feature.

        :param item: an item in basic_operations_params list
        :param data: the data frame
        :return: the updated data frame
        """
        data[item["name"]] = data[item["cols"][0]]
        if "value" in item:
            try:
                data[item["name"]] = (data[item["name"]] / item["value"]).replace(np.inf, np.nan)
            except Exception as e:
                warnings.warn("The division operation failed when dividing col {col} by {value}. The error is: {error}".
                              format(col=item["cols"][0], value=item["value"], error=str(e)), Warning)
                self._conf.feature_engineering.drop_cols.append(item["name"])

        for col in item["cols"][1:]:
            try:
                data[item["name"]] = (data[item["name"]] / data[col]).replace(np.inf, np.nan)
            except Exception as e:
                warnings.warn("The division operation failed while processing {0}. The error is: {1}".
                              format(col, str(e)), Warning)
                self._conf.feature_engineering.drop_cols.append(item["name"])
        return data

    def multiplication(self, item, data):
        """Multiply a sequence of columns to create a new feature.

        :param item: an item in basic_operations_params list
        :param data: the data frame
        :return: the updated data frame
        """
        data[item["name"]] = data[item["cols"][0]]
        if "value" in item:
            try:
                data[item["name"]] = data[item["name"]] * item["value"]
            except Exception as e:
                warnings.warn("The multiplication operation failed when multiplying col {col} by {value}. "
                              "The error is: {error}".
                              format(col=item["cols"][0], value=item["value"], error=str(e)), Warning)
                self._conf.feature_engineering.drop_cols.append(item["name"])

        for col in item["cols"][1:]:
            try:
                data[item["name"]] *= data[col]
            except Exception as e:
                warnings.warn("The multiplication operation failed while processing {0}. The error is: {1}".
                              format(col, str(e)), Warning)
                self._conf.feature_engineering.drop_cols.append(item["name"])
        return data

    def addition(self, item, data):
        """Add a sequence of columns to create a new feature.

        :param item: an item in basic_operations_params list
        :param data: the data frame
        :return: the updated data frame
        """
        data[item["name"]] = data[item["cols"][0]]
        if "value" in item:
            try:
                data[item["name"]] = data[item["name"]] + item["value"]
            except Exception as e:
                warnings.warn("The addition operation failed when adding {value} to col {col}. "
                              "The error is: {error}".
                              format(col=item["cols"][0], value=item["value"], error=str(e)), Warning)
                self._conf.feature_engineering.drop_cols.append(item["name"])

        for col in item["cols"][1:]:
            try:
                data[item["name"]] += data[col]
            except Exception as e:
                warnings.warn("The addition operation failed while processing {0}. The error is: {1}".
                              format(col, str(e)), Warning)
                self._conf.feature_engineering.drop_cols.append(item["name"])
        return data

    def subtraction(self, item, data):
        """Subtract a sequence of columns to create a new feature.

        :param item: an item in basic_operations_params list
        :param data: the data frame
        :return: the updated data frame
        """
        data[item["name"]] = data[item["cols"][0]]
        if "value" in item:
            try:
                data[item["name"]] = data[item["name"]] - item["value"]
            except Exception as e:
                warnings.warn("The subtraction operation failed when subtracting {value} from col {col}. "
                              "The error is: {error}".
                              format(col=item["cols"][0], value=item["value"], error=str(e)), Warning)
                self._conf.feature_engineering.drop_cols.append(item["name"])

        for col in item["cols"][1:]:
            try:
                data[item["name"]] -= data[col]
            except Exception as e:
                warnings.warn("The subtraction operation failed while processing {0}. The error is: {1}".
                              format(col, str(e)), Warning)
                self._conf.feature_engineering.drop_cols.append(item["name"])

        return data

    @staticmethod
    def log_transform(data, params):
        """Loop through each item in log_transform_params and apply the log transformation to a specific base defined
        by user. If we end up with inf after the transformation, replace them with nan and handle them later.

        :param data: the train or test dataframe
        :param params: a list of log_transform parameters coming from the conf object (see the configuration module for details)
        :return: the updated dataframe
        """
        for item in params:
            try:
                data[item["name"]] = data[item["col"]] + item["shift"]
                data[item["name"]] = (np.log(data[item["name"]]) / np.log(item["base"])).replace(np.inf, np.nan).replace(-np.inf, np.nan)
            except Exception as e:
                warnings.warn("The log_transform failed while processing {0}. The error is: {1}".
                              format(item["col"], str(e)), Warning)

        return data

    @staticmethod
    def exponential_transform(data, params):
        """Loop through each item in exponential_transform_params and apply the exponential transformation to a
        specific power defined by user. If we end up with inf after the transformation, replace them with nan and
        handle them later.

        :param data: the train or test dataframe
        :param params: a list of exponential_transform parameters coming from the conf object (see the configuration module for details)
        :return: the updated dataframe
        """
        for item in params:
            try:
                data[item["name"]] = np.power(item["power"], data[item["col"]]).replace(np.inf, np.nan).replace(-np.inf, np.nan)
                data[item["name"]] = data[item["name"]] + item["shift"]
            except Exception as e:
                warnings.warn("The exponential transform failed while processing {0}. The error is: {1}".
                              format(item["col"], str(e)), Warning)
        return data

    def groupby(self, data, params):
        """If learner_groupby is None (during training), instantiate a LearnerGroupby object and then call the
        fit_transform method on it. During validation or testing, the learner_groupby would not be None. In that case,
        we call the transform method on it.

        :param data: the train or test dataframe
        :param params: a list of groupby parameters coming from the conf object (see the configuration module for details)
        :return: the updated dataframe
        """
        if not self._learner_groupby:
            self._learner_groupby = LearnerGroupby(params)
            self._learner_groupby.fit_transform(data)
        else:
            self._learner_groupby.transform(data)
        return data

    def reprocess_data(self, data):
        """Once the feature engineering is completed, process the newly created columns to ensure the data is ready for
        training.

        :param data: the data frame
        :return: the updated data
        """
        logging.info("Processing newly created columns after feature engineering, if any...")
        if not self._processor:
            self._processor = DataProcessor(self._conf)

        data = self._processor.handle_to_numeric(data, cols=list(self._conf.feature_engineering.col_dict.keys()))

        self.processor.fill_nan(data,
                                default_value=self._conf.process.fillnan_value,
                                mean_cols=self._conf.feature_engineering.fillnan_mean_cols,
                                median_cols=self._conf.feature_engineering.fillnan_median_cols,
                                mode_cols=self._conf.feature_engineering.fillnan_mode_cols,
                                value_cols=self._conf.feature_engineering.fillnan_value_cols)

        self.processor.drop_cols(data, cols=self._conf.feature_engineering.drop_cols)
        return data

    def handle_feature_engineering(self, data):
        """The main function for calling the appropriate methods for feature engineering depending on the user's input.

        :param data: the data frame
        :return: updated data
        """
        logging.info("Performing feature engineering...")
        if self._conf.feature_engineering.basic_operations_params:
            logging.info("Performing basic_operations feature engineering...")
            data = self.basic_operations(data)

        if self._conf.feature_engineering.log_transform_params:
            logging.info("Performing log_transform feature engineering...")
            data = self.log_transform(data, self._conf.feature_engineering.log_transform_params)

        if self._conf.feature_engineering.exponential_transform_params:
            logging.info("Performing exponential_transform feature engineering...")
            data = self.exponential_transform(data, self._conf.feature_engineering.exponential_transform_params)

        if self._conf.feature_engineering.groupby_params:
            logging.info("Performing groupby feature engineering...")
            data = self.groupby(data, self._conf.feature_engineering.groupby_params)

        data = self.reprocess_data(data)

        return data


class LearnerGroupby:
    """LearnerGroupby is a class for performing the groupby operations on the datasets. The reason for implementing a
     custom class is to be able to use the values from the training data when working with validation or test dataset.
     Basically, we do all the calculations during the training process. We then build a dictionary that maps the values
     of the training data to their corresponding aggregated values. When it comes to validation or test data, we'll use
     that dictionary to set the values. This is commonly overlooked by many people.
     """
    def __init__(self, params):
        """Initialize an object of LearnerGroupby class using the parameters coming from the conf object. These
        parameters have already been validated and updated. We do not perform any validation in this class.

        :param params: a list of groupby parameters coming from the conf object (see the configuration module for details)
        """
        self._params = params
        self._groupby_dict = dict()

    @property
    def groupby_dict(self):
        return self._groupby_dict

    def fit(self, data):
        """If the params has values, loop through the parameters and the aggregation operations to populate the groupby
        dictionary. For each column and aggregation combination, there will be a key in this dictionary. The value for
        each key is another dictionary that maps the original values to their aggregated values. This dictionary will
        then be used to do the transformation.

        :param data: a pandas dataframe. This is usually training dataset.
        :return: None
        """
        if self._params:
            for param in self._params:
                for agg in param["aggregation"]:
                    gb = data.groupby(by=param["col"]).agg({agg["col"]: agg["method"]})
                    key = f"{param['col']}_{agg['col']}_{agg['method']}"
                    self._groupby_dict[key] = dict(zip(gb.index, gb[agg["col"]]))

    def transform(self, data):
        """If the params has values, loop through the parameters and the aggregation operations to create new columns
        using the groupby dictionary. For each column and aggregation combination, there will be a key in this
        dictionary. The value for each key is another dictionary that maps the original values to their aggregated
        values.

        :param data: a pandas dataframe. This is could be train, validation, or test data.
        :return: None
        """
        for param in self._params:
            for agg in param["aggregation"]:
                key = f"{param['col']}_{agg['col']}_{agg['method']}"
                data[agg["name"]] = data[param["col"]].map(self._groupby_dict[key])

    def fit_transform(self, data):
        """Call fit and transform method. This method is typically called during training while the transform method is
        called during testing.

        :param data: a pandas dataframe. This is could be train, validation, or test data.
        :return: None
        """
        self.fit(data)
        self.transform(data)
