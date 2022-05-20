# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import re
import warnings
import logging

from learner.configuration.configuration import Configuration


class OutlierManager:
    def __init__(self, conf: Configuration, data):
        self._conf = conf
        self._data = data

    @property
    def conf(self):
        return self._conf

    @property
    def data(self):
        return self._data

    def sd_filtering(self):
        """Find the rows that fall on or outside the defined standard deviation cut-off value from the defined center
        for the selected columns. Then, depending on the method, remove or clip the values.

        :return data: filtered/updated dataframe
        """
        initial_num_rows = self._data.shape[0]

        logging.info("Performing sd_filtering...")

        drop_idx = set()
        for col, sd_params in self._conf.outlier.sd_dict.items():
            try:
                std = self._data[col].std()
                if sd_params['center'] == 'mode':
                    mid = getattr(self._data[col], sd_params['center'])()[0]
                else:
                    mid = getattr(self._data[col], sd_params['center'])()

                lower = mid - abs(sd_params['value']) * std
                upper = mid + abs(sd_params['value']) * std

                if sd_params["method"] == "remove":
                    output = self._data[(self._data[col] >= upper) | (self._data[col] <= lower)].index
                    # I don't drop data here because if I do, the standard deviation of a column can change and the
                    # calculations will be incorrect
                    drop_idx = drop_idx.union(set(output))

                # unlike "remove" method, we can immediately invoke clip because it won't affect std of other columns
                # (because we don't remove any rows)
                if sd_params["method"] == "clip":
                    self._data[col].clip(lower, upper, inplace=True)
            except TypeError:
                warnings.warn("Filtering on column {0} was unsuccessful. This could be related to "
                              "dtype".format(col), Warning)

        # drop the indices from "remove" method
        self._data = self._data.loc[~self._data.index.isin(drop_idx)]
        self.print_filtering_info(initial_num_rows, "sd_filtering")
        return self._data

    def min_max_filtering(self):
        """Find the rows that fall outside the "min" and "max" limits. Then, depending on the method, remove the entire
        row or clip the values in the columns.

        :return data: filtered/updated dataframe
        """
        initial_num_rows = self._data.shape[0]

        logging.info("Performing min_max operations...")

        for col, min_max_params in self.conf.outlier.min_max_dict.items():
            try:
                if min_max_params["method"] == "remove":
                    index = (self._data[col] < min_max_params["min"]) | (self._data[col] > min_max_params["max"])
                    self._data = self._data.loc[~index]

                if min_max_params["method"] == "clip":
                    self._data[col].clip(min_max_params["min"], min_max_params["max"], inplace=True)
            except TypeError:
                warnings.warn("Filtering on column {0} was unsuccessful. This could be related to "
                              "dtype".format(col), Warning)

        self.print_filtering_info(initial_num_rows, "min_max_filtering")

        # this line is unnecessary but helps with testing
        return self._data

    def quantile_filtering(self):
        """Find the rows that fall outside a minimum quantile and a maximum quantile. Then, depending on the method,
        remove the entire row or clip the values in the columns.

        :return data: filtered/updated dataframe
        """
        initial_num_rows = self._data.shape[0]
        logging.info("Performing quantile operations...")
        for col, quantile_params in self.conf.outlier.quantile_dict.items():
            try:
                lower = self._data[col].quantile(quantile_params["min"]) if quantile_params["min"] is not None else None
                upper = self._data[col].quantile(quantile_params["max"]) if quantile_params["max"] is not None else None
                if quantile_params["method"] == "remove":
                    index = (self._data[col] < lower) | (self._data[col] > upper)
                    self._data = self._data.loc[~index]

                if quantile_params["method"] == "clip":
                    self._data[col].clip(lower, upper, inplace=True)
            except TypeError:
                warnings.warn("Filtering on column {0} was unsuccessful. This could be related to "
                              "dtype".format(col), Warning)

        self.print_filtering_info(initial_num_rows, "quantile_filtering")

        # this line is unnecessary but helps with testing
        return self._data

    def value_filtering(self):
        """Loop over the columns that require value filtering or replacements. Remove the rows or replace the value based
        on the items in value_dict.

        :return data: filtered/updated dataframe
        """
        initial_num_rows = self._data.shape[0]
        logging.info("Performing value operations...")
        for col, col_info in self.conf.outlier.value_dict.items():
            for to_replace, replace_with in col_info.items():
                try:
                    pattern = re.compile(to_replace)
                    if replace_with is None:
                        index = self._data[col].str.match(pattern)
                        self._data = self._data[~index]
                    else:
                        pass
                        self._data.loc[:, col] = self._data.loc[:, col].str.replace(pattern, replace_with)
                except (AttributeError, TypeError):
                    warnings.warn(f"Value filtering Filtering on column {col} was unsuccessful. This could be related to "
                                  f"the data type of the column", Warning)

        self.print_filtering_info(initial_num_rows, "value_filtering")
        # this line is unnecessary but helps with testing
        return self._data

    def print_filtering_info(self, initial_num_rows, method_name):
        """Print useful information before and after performing outlier filtering


        :param initial_num_rows: the initial number of rows in the training data
        :param method_name: the method name to create the output message
        :return: None
        """
        # compute how many rows are left and print some useful information
        final_num_rows = self._data.shape[0]
        filtered_num_rows = initial_num_rows - final_num_rows
        logging.info("%i rows were filtered during %s and %i rows are left", filtered_num_rows, method_name,
                     final_num_rows)
        # exit if no data is left for training after filtering
        if final_num_rows == 0:
            logging.error("No data is left for training after %s. Exiting...", method_name)
            sys.exit(1)

    def handle_outlier(self):
        """The main function for filtering the data and removing outliers. Depending on the user input, appropriate
        if blocks will execute.

        :return: updated data
        """

        logging.info("Handling outliers in training data...")
        if self._conf.outlier.quantile_activate:
            self.quantile_filtering()

        if self._conf.outlier.sd_activate:
            self.sd_filtering()

        if self._conf.outlier.min_max_activate:
            self.min_max_filtering()

        if self._conf.outlier.value_activate:
            self.value_filtering()

        return self._data
