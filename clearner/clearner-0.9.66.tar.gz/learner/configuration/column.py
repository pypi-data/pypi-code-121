# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import copy
import warnings
import logging

from learner.data_worker.data_loader import get_dtype_dict as data_worker_get_dtype_dict
from learner.data_worker.data_loader import get_data, get_value


class ColumnConfiguration:
    """Parse all input variables related to selecting the columns of the datasets including the columns that must be
    used (use_cols), target column (target_col), etc."""

    def __init__(self, json_config, engine, data, sample):
        self._data = data
        self._sample = sample
        self._json_config = json_config
        self._engine = engine
        self.use_cols = self.get_use_cols()
        self.valid_cols = copy.deepcopy(self.use_cols)
        self.target_col = self.get_target_col()
        self.path_col = self.get_path_col()
        self.copy_cols = self.get_copy_cols()
        self.all_cols = self.get_all_cols()
        self.col_dtypes = get_value(self._json_config, None, "column", "dtype_params", "col_dtypes")

        self.dtype_activate = self.get_dtypes_activate()
        self.dtype_trial_nrows = self.get_dtype_trial_nrows()
        self.dtype_dict = self.get_dtype_dict()

        # these happen here so that we can pass the new column around and avoid validations errors
        self.date_cols_activate = get_value(self._json_config, False, "process", "date_cols_params", "activate")
        self.col_names_for_date_cols_items = self.get_col_names_for_date_cols_items()

        self.id_cols = self.get_id_cols()
        self.drop_cols = self.get_drop_cols()
        self.drop_from_train = self.get_drop_from_train()

    def get_use_cols(self):
        try:
            return self._json_config["column"]["use_cols"]
        except KeyError:
            if self._data.train_input_type == "file":
                warnings.warn("No use_cols has been specified in json configuration. Using all columns from the train "
                              "dataset.", UserWarning)
                use_cols = get_data(self._data.train_location,
                                    self._data.manifest,
                                    format=self._data.train_format,
                                    nrows=1,
                                    sep=self._data.train_delimiter,
                                    header=self._data.train_header,
                                    usecols=None).columns.tolist()
                return use_cols
            return []

    def get_copy_cols(self):
        try:
            copy_cols = self._json_config["column"]["copy_cols"]
            # we don't allow copying the target column because we don't load target when testing
            if any([col == self.target_col for col in copy_cols]):
                logging.critical("""
                The target columns cannot be included in copy_cols in the column section. Please update 
                your configuration file and retry. Exiting...
                """)
                sys.exit(1)

            # add the new columns to valid column names
            self.valid_cols.extend(list(copy_cols.values()))
            return copy_cols
        except KeyError:
            return {}

    def get_all_cols(self):
        if self._data.manifest:
            all_cols = get_data(self._data.train_location,
                                self._data.manifest,
                                format=self._data.train_format,
                                nrows=1,
                                sep=self._data.train_delimiter,
                                header=self._data.train_header,
                                usecols=None).columns.tolist()
            return all_cols

        return None

    def get_dtypes_activate(self):
        try:
            activate = self._json_config["column"]["dtype_params"]["activate"]
            return activate
        except KeyError:
            if self.col_dtypes:
                warnings.warn("col_dtypes was specified but load_with_dtypes was not set to true. Loading with "
                              "dtype won't be activated.", UserWarning)
            return False

    def get_dtype_trial_nrows(self):
        recommended_nrows = 200000
        try:
            dtype_trial_nrows = self._json_config["column"]["dtype_params"]["nrows"]
            if self.dtype_activate:
                if dtype_trial_nrows < recommended_nrows and self._data.train_nrows and dtype_trial_nrows < self._data.train_nrows:
                    warnings.warn("It is recommended to use {0} rows for trial loading but {1} rows was requested."
                                  .format(recommended_nrows, dtype_trial_nrows), UserWarning)
                    return dtype_trial_nrows
                if self._data.train_nrows and dtype_trial_nrows > self._data.train_nrows:
                    warnings.warn("{0} rows was requested for trial loading but {1} is used for training. Setting "
                                  "trial nrows to {1}".format(dtype_trial_nrows, self._data.train_nrows)
                                  .format(recommended_nrows, dtype_trial_nrows), UserWarning)
                    return self._data.train_nrows
        except KeyError:
            if self._data.train_nrows and self._data.train_nrows < recommended_nrows:
                return self._data.train_nrows
            return recommended_nrows

    def get_dtype_dict(self):
        if self.dtype_activate:
            dtype_dict = data_worker_get_dtype_dict(self._data.meta_data, self.use_cols, self.col_dtypes)
            return dtype_dict

    def get_target_col(self):
        try:
            target_col = self._json_config["column"]["target_col"]
            # if train_test_split is active, we don't need to know if the target column exists in validation_cols or not
            # because we will use the train data which would definitely include the target
            # also if the query in validation query is activated, we don't need to get the validation columns
            # finally, we only need to get the columns if the input_type is "file"
            if self._data.validation_score_activate and not self._sample.split_activate and not self._data.validation_query_activate and self._data.validation_input_type == "file":
                # we only do this validation if we have the csv format. For other formats, we'd have to load the
                # entire data, which could slow things down. If there's an issue, it will surface later
                if self._data.validation_format == "csv":
                    all_validation_cols = self.get_all_validation_cols()
                    if target_col not in all_validation_cols:
                        logging.error("score_predictions is set to true but target_col is not in validation data. "
                                      "Exiting...")
                        sys.exit(1)
                # if the input_type is not file, we can simply add the target_col to valid_cols
            if (self._data.train_input_type != "file" or self._data.validation_input_type != "file") and target_col not in self.valid_cols:
                self.valid_cols.append(target_col)
            return target_col
        except KeyError:
            if self._data.validation_input_type == "file":
                logging.critical("target_col cannot be undefined. Exiting...")
                sys.exit(1)
            target_col = "target"
            self.valid_cols.append(target_col)
            return target_col

    def get_path_col(self):
        if self._engine == "ImageClassifier":
            path_col = "path"
            try:
                path_col = self._json_config["column"]["path_col"]
            finally:
                self.valid_cols.append(path_col)
                return path_col

    def get_all_validation_cols(self):
        cols = get_data(self._data.validation_location,
                        self._data.manifest,
                        nrows=1,
                        sep=self._data.validation_delimiter,
                        header=self._data.validation_header,
                        usecols=None).columns.tolist()
        return cols

    def get_col_names_for_date_cols_items(self):
        try:
            date_cols = self._json_config["process"]["date_cols_params"]["date_cols"]
            col_names_for_date_cols_items = []
            if self.date_cols_activate and date_cols:
                for col, date_item in date_cols.items():
                    # make sure the user can make requests on the new columns after they've been created
                    for item in date_item:
                        col_names_for_date_cols_items.append("{col}_{item}".format(col=col, item=item))

            self.valid_cols.extend(col_names_for_date_cols_items)
            return col_names_for_date_cols_items
        except KeyError:
            return []

    def get_id_cols(self):
        try:
            id_cols = self._json_config["column"]["id_cols"]
            return id_cols
        except KeyError:
            return []

    def get_drop_cols(self):
        try:
            drop_cols = self._json_config["column"]["drop_cols"]
            return drop_cols
        except KeyError:
            return []

    def get_drop_from_train(self):
        try:
            drop_from_train = self._json_config["column"]["drop_from_train"]
            return drop_from_train
        except KeyError:
            return []
