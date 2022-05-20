# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import warnings
import logging

from learner.validator.input_validator import (validate_intersection_cols,
                                               validate_subset_list,
                                               validate_in_range,
                                               validate_type)
from learner.data_worker.data_loader import get_value


class OutlierConfiguration:
    """Parse all inputs related to outlier management of the training data."""

    supported_methods = {"r": "remove", "c": "clip"}

    def __init__(self, json_config, column, data, process):
        self._column = column
        self._json_config = json_config
        self._data = data
        self._process = process

        self.min_max_activate = get_value(self._json_config, False, "outlier", "min_max_params", "activate")
        self.min_max_cols = self.get_min_max_cols()
        self.min_max_dict = self.get_min_max_dict()

        self.quantile_activate = get_value(self._json_config, False, "outlier", "quantile_params", "activate")
        self.quantile_cols = self.get_quantile_cols()
        self.quantile_dict = self.get_quantile_dict()

        self.sd_activate = get_value(self._json_config, False, "outlier", "sd_params", "activate")
        self.sd_cols = self.get_sd_cols()
        self.sd_dict = self.get_sd_dict()

        self.value_activate = get_value(self._json_config, False, "outlier", "value_params", "activate")
        self.value_cols = self.get_value_cols()
        self.value_dict = self.get_value_dict()

    def get_min_max_cols(self):
        try:
            min_max_cols = self._json_config["outlier"]["min_max_params"]["cols_params"]
            # in case min or max does not contain in the keys, add them and set their values to None
            try:
                for col, col_info in min_max_cols.items():
                    # we need to check this because valideer won't
                    validate_subset_list(["min", "max", "method"],
                                         "supported fields",
                                         col_info.keys(),
                                         "the fields in cols_params")

                    min_max_cols[col] = {"min": col_info.get("min", None),
                                         "max": col_info.get("max", None),
                                         "method": col_info.get("method", "remove")}

            except Exception as e:
                logging.error("There is an issue with cols_params in min_max_params. The error is {error}".format(error=str(e)))
                sys.exit(1)
            return min_max_cols
        except KeyError:
            return {}

    def get_min_max_dict(self):
        min_max_dict = {}

        if self._data.meta_data:
            min_max_dict = {col: {"min": col_info["min_max"].get("min", None),
                                  "max": col_info["min_max"].get("max", None),
                                  "method": col_info["min_max"].get("method", "remove")}
                            for col, col_info in self._data.meta_data["column"].items()
                            if col in self._column.use_cols and "min_max" in col_info.keys() and
                            ("min" in col_info["min_max"].keys() or "max" in col_info["min_max"].keys())}

        min_max_dict.update(self.min_max_cols)

        if self.min_max_activate:
            min_max_dict = self.update_min_max_dict(min_max_dict)
            self.validate_min_max_filtering_cols(min_max_dict)
        return min_max_dict

    @staticmethod
    def update_min_max_dict(min_max_dict):
        # make sure we don't keep the items in which both min and max values are None, i.e, no filtering needed
        return {col: {"min": col_info["min"], "max": col_info["max"], "method": col_info["method"]} for col, col_info in min_max_dict.items()
                if (col_info["min"] is not None or col_info["max"] is not None)}

    def validate_min_max_filtering_cols(self, min_max_dict):
        # make sure the specified methods are valid
        for col, col_info in min_max_dict.items():
            try:
                method = col_info["method"]
                col_info["method"] = OutlierConfiguration.supported_methods[method[0].lower()]
            except KeyError:
                logging.error('The method "{method}" for min_max not understood. The acceptable '
                              'methods are {acceptable_methods}'.
                    format(method=method,
                           acceptable_methods=list(OutlierConfiguration.supported_methods.values())))
                sys.exit(1)

        if self._process.dummies_activate:
            validate_intersection_cols(cols1=self._process.dummies_cols,
                                       cols2=list(min_max_dict.keys()),
                                       cols1_name='dummy_cols',
                                       cols2_name='min_max_cols')

        if self._process.label_encoding_activate:
            validate_intersection_cols(cols1=self._process.label_encoding_cols,
                                       cols2=list(min_max_dict.keys()),
                                       cols1_name='label_encoding cols',
                                       cols2_name='min_max_cols')

    def get_quantile_cols(self):
        try:
            quantile_cols = self._json_config["outlier"]["quantile_params"]["cols_params"]
            # in case min or max does not contain in the keys, add them and set their values to None
            try:
                for col, col_info in quantile_cols.items():
                    # we need to check this because valideer won't
                    validate_subset_list(["min", "max", "method"],
                                         "supported fields",
                                         col_info.keys(),
                                         "the fields in cols_params")

                    quantile_cols[col] = {"min": col_info.get("min", None),
                                          "max": col_info.get("max", None),
                                          "method": col_info.get("method", "remove")}

            except Exception as e:
                logging.error("There is an issue with cols_params in quantile_params. The error is {error}".format(error=str(e)))
                sys.exit(1)
            return quantile_cols
        except KeyError:
            return {}

    def get_quantile_dict(self):
        quantile_dict = {}

        if self._data.meta_data:
            quantile_dict = {col: {"min": col_info["quantile"].get("min", None),
                                   "max": col_info["quantile"].get("max", None),
                                   "method": col_info["quantile"].get("method", "remove")}
                             for col, col_info in self._data.meta_data["column"].items()
                             if col in self._column.use_cols and "quantile" in col_info.keys() and
                             ("min" in col_info["quantile"].keys() or "max" in col_info["quantile"].keys())}

        quantile_dict.update(self.quantile_cols)

        if self.quantile_activate:
            quantile_dict = self.update_min_max_dict(quantile_dict)
            self.validate_quantile_cols(quantile_dict)
        return quantile_dict

    @staticmethod
    def update_quantile_dict(quantile_dict):
        # make sure we don't keep the items in which both min and max values are None, i.e, no filtering needed
        return {col: {"min": col_info["min"], "max": col_info["max"], "method": col_info["method"]} for col, col_info in quantile_dict.items()
                if (col_info["min"] is not None or col_info["max"] is not None)}

    def validate_quantile_cols(self, quantile_dict):
        # make sure the specified methods are valid
        for col, col_info in quantile_dict.items():
            try:
                method = col_info["method"]
                col_info["method"] = OutlierConfiguration.supported_methods[method[0].lower()]
                # need to make sure minimum and maximum are between 0 and 1
                validate_in_range([col_info["min"], col_info["max"]], minimum=0, maximum=1)
            except KeyError:
                logging.error('The method "{method}" for quantile not understood. The acceptable '
                              'methods are {acceptable_methods}'
                              .format(method=method,
                                      acceptable_methods=list(OutlierConfiguration.supported_methods.values())))
                sys.exit(1)

        if self._process.dummies_activate:
            validate_intersection_cols(cols1=self._process.dummies_cols,
                                       cols2=list(quantile_dict.keys()),
                                       cols1_name='dummy_cols',
                                       cols2_name='quantile_cols')

        if self._process.label_encoding_activate:
            validate_intersection_cols(cols1=self._process.label_encoding_cols,
                                       cols2=list(quantile_dict.keys()),
                                       cols1_name='label_encoding cols',
                                       cols2_name='quantile_cols')

    def get_sd_cols(self):
        try:
            sd_filtering_cols = self._json_config["outlier"]["sd_params"]["cols_params"]
            return sd_filtering_cols
        except KeyError:
            return {}

    def get_sd_dict(self):
        sd_dict = {}

        if self._data.meta_data:
            sd_dict = dict((col, col_info["sd"]) for col, col_info in self._data.meta_data["column"].items()
                           if col in self._column.use_cols and "sd" in col_info.keys())

        sd_dict.update(self.sd_cols)

        if self.sd_activate:
            self.validate_sd_dict_format(sd_dict)
            self.update_sd_dict(sd_dict)
            self.validate_sd_dict_cols(sd_dict)
        return sd_dict

    @staticmethod
    def validate_sd_dict_format(sd_dict):
        for col, sd_params in sd_dict.items():
            if isinstance(sd_params, dict):
                try:
                    if not isinstance(sd_params["value"], (float, int)):
                        logging.error("The value for col %s in sd_params must be a number. Exiting...",
                                      col)
                        sys.exit(1)
                except KeyError:
                    logging.exception('When passing a dictionary to a column in cols_params, "value" must be '
                                      'defined. A single number can also be passed to a column instead of a '
                                      'dictionary. Exiting...')
                    sys.exit(1)
            elif isinstance(sd_params, (float, int)):
                sd_dict[col] = {'value': sd_params}
            else:
                logging.error("The value for col %s in sd_params must be a number or a dictionary. "
                              "Exiting...", col)
                sys.exit(1)
            # set the method to "remove" if not defined
            sd_dict[col]["method"] = sd_dict[col].get("method", "remove")

    @staticmethod
    def update_sd_dict(sd_dict):
        for col, sd_params in sd_dict.items():
            try:
                if sd_params["center"].lower().startswith('med'):
                    sd_params["center"] = "median"
                elif sd_params["center"].lower().startswith('mo'):
                    sd_params["center"] = "mode"
                else:
                    sd_params["center"] = "mean"
                sd_params["method"] = sd_params.get("method", "remove")
            except KeyError:
                warnings.warn('No center was defined for col {0} in sd_params, using "mean"'.format(col),
                              UserWarning)
                sd_params["center"] = "mean"
            except AttributeError:
                warnings.warn('The defined center for col {0} in sd_params not understood, using "mean"'
                              .format(col), UserWarning)
                sd_params["center"] = "mean"

    def validate_sd_dict_cols(self, sd_dict):
        # make sure the specified methods are valid
        for col, sd_params in sd_dict.items():
            try:
                method = sd_params["method"]
                sd_params["method"] = OutlierConfiguration.supported_methods[method[0].lower()]
            except KeyError:
                logging.error('The method "{method}" for sd_params not understood. The acceptable '
                              'methods are {acceptable_methods}'.
                              format(method=method,
                                     acceptable_methods=list(OutlierConfiguration.supported_methods.values())))
                sys.exit(1)
            # we need to check this because valideer won't
            validate_subset_list(["value", "center", "method"],
                                 "supported fields",
                                 sd_params.keys(),
                                 "the fields in cols_params")

        if self._process.dummies_activate:
            validate_intersection_cols(cols1=self._process.dummies_cols,
                                       cols2=list(sd_dict.keys()),
                                       cols1_name='dummy_cols',
                                       cols2_name='sd_cols')

        if self._process.label_encoding_activate:
            validate_intersection_cols(cols1=self._process.label_encoding_cols,
                                       cols2=list(sd_dict.keys()),
                                       cols1_name='label_encoding cols',
                                       cols2_name='sd_cols')

    def get_value_cols(self):
        try:
            cols_params = self._json_config["outlier"]["value_params"]["cols_params"]
            return cols_params
        except KeyError:
            return {}

    def get_value_dict(self):
        value_dict = {}
        for col, col_info in self.value_cols.items():
            # if col_info is a list, assume all the values need to be remove. So update the dictionary accordingly
            if isinstance(col_info, list):
                value_dict[col] = {}
                for item in col_info:
                    value_dict[col][item] = None
            else:
                # if col_info is not a list, it must be a dictionary
                validate_type(object_=col_info, type_=dict, object_name=f"the value of {col}", type_name="dictionary")
                value_dict[col] = col_info

        return value_dict
