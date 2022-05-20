# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import logging
import warnings
from datetime import datetime
from learner.configuration.supported_items import SUPPORTED_IMBALANCED_METHODS, SUPPORTED_SPLIT_METHODS
from learner.data_worker.data_loader import get_value
from learner.configuration.workspace import WorkspaceConfiguration
from learner.validator.input_validator import validate_date_format


class SampleConfiguration:
    def __init__(self, json_config, engine, workspace: WorkspaceConfiguration):
        self._json_config = json_config
        self._engine = engine
        self._workspace = workspace

        self.split_data = self.get_split_data()
        self.imbalanced_activate = self.get_imbalanced_activate()
        self.imbalanced_method = self.get_imbalanced_method()
        self.imbalanced_random_state = get_value(self._json_config, 42, "sample", "imbalanced_params", "random_state")

        self.split_activate = get_value(self._json_config, False, "sample", "train_test_split_params", "activate")
        self.split_method = self.get_split_method()
        self.split_save_train_data = get_value(self._json_config, False, "sample", "train_test_split_params", "save_train_data")

        self.split_test_size = self.get_split_test_size()

        self.split_random_state = get_value(self._json_config, None, "sample", "train_test_split_params", "random_state")
        self.split_shuffle = get_value(self._json_config, True, "sample", "train_test_split_params", "shuffle")
        self.split_random_stratify = get_value(self._json_config, None, "sample", "train_test_split_params", "stratify")

        self.split_sort_col = get_value(self._json_config, None, "sample", "train_test_split_params", "col")
        self.split_sort_nan_position = self.get_split_sort_nan_position()
        self.split_test_on_after = self.get_split_test_on_after()
        self.split_train_before = self.get_split_train_before()

    @property
    def json_config(self):  # pragma: no cover
        return self._json_config

    @property
    def engine(self):
        return self._engine

    @property
    def output(self):
        return self._workspace

    def get_split_data(self):
        if self.engine in ("DeepClassifier", "DeepRegressor"):
            return False
        return True

    def get_imbalanced_activate(self):
        try:
            activate = self._json_config["sample"]["imbalanced_params"]["activate"]
            acceptable_engines = ("Classifier",)
            if activate and self.engine not in acceptable_engines:
                warnings.warn("imbalanced_params were activated but the engine is not {acceptable_engines}. "
                              "Deactivating the imbalanced_params".format(acceptable_engines=acceptable_engines),
                              UserWarning)
                return False
            return activate
        except KeyError:
            return False

    def get_imbalanced_method(self):
        try:
            method = self._json_config["sample"]["imbalanced_params"]["method"].lower()
            if self.imbalanced_activate and method not in SUPPORTED_IMBALANCED_METHODS.values():
                try:
                    return SUPPORTED_IMBALANCED_METHODS[method[0]]
                except KeyError:
                    logging.error("Invalid method in imbalanced_params, supported methods are {supported_methods}"
                                  .format(supported_methods=SUPPORTED_IMBALANCED_METHODS.values()))
                    sys.exit(1)
            return method
        except KeyError:
            return "undersampling"

    def get_split_method(self):
        try:
            method = self._json_config["sample"]["train_test_split_params"]["method"].lower()
            if self.split_activate and method not in SUPPORTED_SPLIT_METHODS.values():
                try:
                    return SUPPORTED_SPLIT_METHODS[method[0]]
                except KeyError:
                    logging.critical("""Invalid method in train_test_split_params, supported methods are 
                                     {supported_methods}""".format(supported_methods=SUPPORTED_SPLIT_METHODS.values()))
                    sys.exit(1)
            return method
        except KeyError:
            return "random"

    def get_split_sort_nan_position(self):
        supported_nan_position = {"f": "first", "l": "last"}
        try:
            nan_position = self._json_config["sample"]["train_test_split_params"]["nan_position"].lower()
            if self.split_activate and self.split_method == "sort" and supported_nan_position.values():
                try:
                    return supported_nan_position[nan_position[0]]
                except KeyError:
                    logging.critical(f"""Invalid value nan_position of train_test_split_params, accepted values are  
                                     {supported_nan_position.values()}""")
        except KeyError:
            return "last"

    def get_split_test_size(self):
        try:
            test_size = self._json_config["sample"]["train_test_split_params"]["test_size"]
            if self.split_activate:
                if test_size < 0:
                    logging.critical("The test_size in train_test_split_params cannot be negative")
                    sys.exit(1)
            # when the test size is larger than one, that means the user has defined the number of samples they want
            # not the fraction of data
            if test_size > 1:
                return int(test_size)
            return test_size
        except KeyError:
            return 0.2

    def get_split_test_on_after(self):
        date_format = "%Y-%m-%d"
        try:
            test_after = self._json_config["sample"]["train_test_split_params"]["test_on_after"]
            if self.split_activate and self.split_method == "sort":
                validate_date_format(date=test_after, date_format=date_format,
                                     field_name="test_on_after")
            test_after = datetime.strptime(test_after, date_format)
            return test_after
        except KeyError:
            return None

    def get_split_train_before(self):
        date_format = "%Y-%m-%d"
        try:
            train_before = self._json_config["sample"]["train_test_split_params"]["train_before"]
            if self.split_activate and self.split_method == "sort":
                validate_date_format(date=train_before, date_format=date_format,
                                     field_name="train_before")
            train_before = datetime.strptime(train_before, date_format)
            if not self.split_test_on_after:
                self.split_test_on_after = train_before
            return train_before
        except KeyError:
            return self.split_test_on_after

