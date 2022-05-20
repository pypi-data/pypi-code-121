# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
from math import e
import warnings
import logging

from learner.validator.input_validator import validate_subset_list
from learner.configuration.supported_items import SUPPORTED_GROUPBY_AGGREGATION_FUNCTIONS


class FeatureEngineeringConfiguration:
    """Parse all inputs related to feature_engineering section of the configuration file."""

    def __init__(self, json_config, column, process):
        self._column = column
        self._process = process
        self._json_config = json_config
        self.supported_basic_operations = {"m": "multiplication",
                                           "d": "division",
                                           "a": "addition",
                                           "s": "subtraction"}
        self.drop_cols = []
        self.col_dict = {}
        self.fillnan_mean_cols = []
        self.fillnan_median_cols = []
        self.fillnan_mode_cols = []
        self.fillnan_value_cols = {}
        self.basic_operations_params = self.get_basic_operations_params()

        self.log_transform_params = self.get_log_transform_params()
        self.exponential_transform_params = self.get_exponential_transform_params()
        self.groupby_params = self.get_groupby_params()

    def get_basic_operations_params(self):
        try:
            basic_operations_params = self._json_config["feature_engineering"]["basic_operations_params"]
            self.remove_inactive_items(basic_operations_params)
            self.update_method_names(basic_operations_params)
            self.validate_basic_operations_cols_length(basic_operations_params)
            names = self.get_update_basic_operations_col_names(basic_operations_params)
            self.update_col_dicts(names)
            self.update_drop_cols_using_basic_operations(basic_operations_params)
            self._column.valid_cols.extend(names)

            return basic_operations_params
        except KeyError:
            return None

    @staticmethod
    def remove_inactive_items(params):
        i = 0
        while 0 <= i < len(params):
            try:
                if params[i]["activate"] is False:
                    del params[i]
                    i -= 1
                i += 1
            except KeyError:
                del params[i]
                i -= 1

    def update_method_names(self, params):
        for item in params:
            try:
                operation = item["method"].lower()
                if operation not in self.supported_basic_operations.values():
                    try:
                        item["method"] = self.supported_basic_operations[operation[0]]
                    except KeyError:
                        logging.error('The basic_operation method "%s" not understood, supported operations are %s',
                                      operation, list(self.supported_basic_operations.values()))
                        sys.exit(1)
                item["method"] = self.supported_basic_operations[operation[0]]
            except (KeyError, IndexError):
                logging.error("The method name in basic_operations must be defined, the supported methods are %s. "
                              "Exiting...", list(self.supported_basic_operations.values()))
                sys.exit(1)

    @staticmethod
    def validate_basic_operations_cols_length(params):
        for item in params:
            try:
                length = len(item["cols"])
                first_col = item["cols"][0]
                if length == 1 and "value" not in item:
                    item["cols"].append(first_col)
                    warnings.warn("Only one column was defined without any constant value, "
                                  "duplicating the same column for basic operation",
                                  UserWarning)
                elif length > 1 and "value" in item:
                    logging.critical("Only one column should be defined when 'value' exist in the basic_operations "
                                     "list. Please update your configuration file and try again. Exiting...")
                    sys.exit(1)
            except (KeyError, IndexError):
                logging.critical("At least one column must be defined for each item in basic_operations_params. "
                              "Nothing was found. Exiting...")
                sys.exit(1)

    @staticmethod
    def get_update_basic_operations_col_names(params):
        names = []
        for item in params:
            try:
                name = item["name"]
                names.append(name)
            except KeyError:
                method = item["method"]
                # if we get here and only have one item in "cols" that mean we also have "value" key as well.
                # We use it to construct the name
                if len(item["cols"]) == 1 and "value" in item:
                    name = item["cols"][0] + "__" + method[0] + "__" + str(item["value"])
                else:
                    name = ''
                    for i, col in enumerate(item["cols"], 1):
                        if i < len(item["cols"]):
                            name += col + "__" + method[0] + '__'
                        else:
                            name += col
                names.append(name)
                item["name"] = name
        return names

    def update_col_dicts(self, names):
        for name in names:
            if self._process.fillnan_mean_cols and name in self._process.fillnan_mean_cols:
                self.col_dict[name] = "mean"
                self.fillnan_mean_cols.append(name)
                self._process.fillnan_mean_cols.remove(name)
            if self._process.fillnan_median_cols and name in self._process.fillnan_median_cols:
                self.col_dict[name] = "median"
                self.fillnan_median_cols.append(name)
                self._process.fillnan_median_cols.remove(name)
            if self._process.fillnan_mode_cols and name in self._process.fillnan_mode_cols:
                self.col_dict[name] = "mode"
                self.fillnan_mode_cols.append(name)
                self._process.fillnan_mode_cols.remove(name)
            if self._process.fillnan_value_cols and name in self._process.fillnan_value_cols:
                self.col_dict[name] = self._process.fillnan_value_cols[name]
                self.fillnan_value_cols[name] = self._process.fillnan_value_cols[name]
                del self._process.fillnan_value_cols[name]

    def update_drop_cols_using_basic_operations(self, params):
        self.drop_cols = set(self.drop_cols)
        for item in params:
            try:
                if item["drop"]:
                    self.drop_cols = self.drop_cols.union(set(item["cols"]))
                else:
                    warnings.warn("The cols {0} will not be dropped after performing feature engineering".format(
                        item["cols"]), UserWarning)
            except KeyError:
                warnings.warn("The cols {0} will not be dropped after performing feature engineering".format(
                    item["cols"]), UserWarning)

        self.drop_cols = list(self.drop_cols)

    def get_log_transform_params(self):
        try:
            log_transform_params = self._json_config["feature_engineering"]["log_transform_params"]
            self.remove_inactive_items(log_transform_params)
            self.validate_log_transform_cols(log_transform_params)
            self.update_base_values(log_transform_params)
            self.update_shift_values(log_transform_params)
            names = self.get_update_log_transform_col_names(log_transform_params)
            self.update_col_dicts(names)
            self.update_drop_cols_using_log_transform(log_transform_params)
            self._column.valid_cols.extend(names)

            return log_transform_params
        except KeyError:
            return None

    @staticmethod
    def get_update_log_transform_col_names(params):
        names = []
        for item in params:
            try:
                name = item["name"]
                names.append(name)
            except KeyError:
                name = "log_" + item["col"]
                names.append(name)
                item["name"] = name
        return names

    @staticmethod
    def validate_log_transform_cols(params):
        for item in params:
            if "col" not in item:
                logging.critical(f"'col' must be defined in all active items in log_transform_params. Please check  "
                                 f"{item} and try again. Exiting...")
                sys.exit(1)

    @staticmethod
    def update_base_values(params):
        for item in params:
            if "base" not in item:
                item["base"] = e

    @staticmethod
    def update_shift_values(params):
        for item in params:
            if "shift" not in item:
                item["shift"] = 0

    def update_drop_cols_using_log_transform(self, params):
        self.drop_cols = set(self.drop_cols)
        for item in params:
            try:
                if item["drop"]:
                    self.drop_cols = self.drop_cols.union([item["col"]])
                else:
                    warnings.warn("The cols {0} will not be dropped after performing feature engineering".format(
                        item["col"]), UserWarning)
            except KeyError:
                warnings.warn("The cols {0} will not be dropped after performing feature engineering".format(
                    item["col"]), UserWarning)

        self.drop_cols = list(self.drop_cols)

    def get_exponential_transform_params(self):
        try:
            exponential_transform_params = self._json_config["feature_engineering"]["exponential_transform_params"]
            self.remove_inactive_items(exponential_transform_params)
            self.validate_exponential_transform_cols(exponential_transform_params)
            self.update_power_values(exponential_transform_params)
            self.update_shift_values(exponential_transform_params)
            names = self.get_update_exponential_transform_col_names(exponential_transform_params)
            self.update_col_dicts(names)
            self.update_drop_cols_using_exponential_transform(exponential_transform_params)
            self._column.valid_cols.extend(names)

            return exponential_transform_params
        except KeyError:
            return None

    @staticmethod
    def get_update_exponential_transform_col_names(params):
        names = []
        for item in params:
            try:
                name = item["name"]
                names.append(name)
            except KeyError:
                name = "exponential_" + item["col"]
                names.append(name)
                item["name"] = name
        return names

    @staticmethod
    def validate_exponential_transform_cols(params):
        for item in params:
            if "col" not in item:
                logging.critical(f"'col' must be defined in all active items in exponential_transform_params. Please check  "
                                 f"{item} and try again. Exiting...")
                sys.exit(1)

    @staticmethod
    def update_power_values(params):
        for item in params:
            if "power" not in item:
                item["power"] = e

    def update_drop_cols_using_exponential_transform(self, params):
        self.drop_cols = set(self.drop_cols)
        for item in params:
            try:
                if item["drop"]:
                    self.drop_cols = self.drop_cols.union([item["col"]])
                else:
                    warnings.warn("The cols {0} will not be dropped after performing feature engineering".format(
                        item["col"]), UserWarning)
            except KeyError:
                warnings.warn("The cols {0} will not be dropped after performing feature engineering".format(
                    item["col"]), UserWarning)

        self.drop_cols = list(self.drop_cols)

    def get_groupby_params(self):
        try:
            groupby_params = self._json_config["feature_engineering"]["groupby_params"]
            self.remove_inactive_items(groupby_params)
            self.validate_groupby_cols(groupby_params)
            self.validate_groupby_method_names(groupby_params)
            names = self.get_update_groupby_col_names(groupby_params)
            self.update_col_dicts(names)
            self._column.valid_cols.extend(names)
            return groupby_params
        except KeyError:
            return None

    @staticmethod
    def validate_groupby_cols(params):
        for param in params:
            if "col" not in param:
                logging.critical(f"'col' must be defined in all active items in groupby_params. Please check  "
                                 f"{param} and try again. Exiting...")
                sys.exit(1)
            if "aggregation" not in param:
                logging.critical(f"'aggregation' list must be defined in all active items in groupby_params. Please check  "
                                 f"{param} and try again. Exiting...")
                sys.exit(1)
            for agg in param["aggregation"]:
                if "col" not in agg:
                    logging.critical(f"'col' must be defined in each item in 'aggregation' list. Please check  "
                                     f"{param} and try again. Exiting...")
                    sys.exit(1)

    @staticmethod
    def validate_groupby_method_names(params):
        for param in params:
            for agg in param["aggregation"]:
                try:
                    method = agg["method"]
                    validate_subset_list(parent_list=SUPPORTED_GROUPBY_AGGREGATION_FUNCTIONS,
                                         parent_name="supported aggregation methods",
                                         subset_list=[method],
                                         subset_name="defined method")
                except KeyError:
                    logging.error("The method name must be defined for each item in 'aggregation' list. "
                                  "The supported methods are {supported_methods}. Please update your configuration "
                                  "file and try again. Exiting...".format(supported_methods=SUPPORTED_GROUPBY_AGGREGATION_FUNCTIONS))
                    sys.exit(1)

    @staticmethod
    def get_update_groupby_col_names(params):
        names = []
        for param in params:
            for agg in param["aggregation"]:
                try:
                    name = agg["name"]
                    names.append(name)
                except KeyError:
                    name = f"{agg['method']}_{agg['col']}_groupby_{param['col']}"
                    names.append(name)
                    agg["name"] = name
        return names
