# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
from math import e
import warnings
import logging

from learner.validator.input_validator import validate_intersection_cols, validate_subset_list
from learner.data_worker.data_loader import get_value
from learner.configuration.column import ColumnConfiguration
from learner.configuration.sample import SampleConfiguration
from learner.configuration.supported_items import DATE_ITEMS, SUPPORTED_ENGINES_FOR_TARGET_LOG_TRANSFORM, SUPPORTED_STEMMERS
from learner.validator.model_validator import DefaultValidatingDraft7Validator
from learner.configuration.defaults import IMAGE_TRANSFORM_PARAMS


class ProcessConfiguration:
    """Parse all input variables related to data processing."""

    def __init__(self, json_config, data, column: ColumnConfiguration, sample: SampleConfiguration, engine):
        self._json_config = json_config
        self._data = data
        self._column = column
        self._sample = sample
        self._engine = engine

        self.fillnan_activate = self.get_fillnan_activate()
        self.fillnan_mean_cols = get_value(self._json_config, [], "process", "fillnan_params", "mean_cols")
        self.fillnan_median_cols = get_value(self._json_config, [], "process", "fillnan_params", "median_cols")
        self.fillnan_mode_cols = get_value(self._json_config, [], "process", "fillnan_params", "mode_cols")
        self.fillnan_value_cols = self.get_fillnan_value_cols()
        self.fillnan_value = get_value(self._json_config, 0, "process", "fillnan_params", "value")

        self.dummies_activate = self.get_dummies_activate()
        self.dummies_cols = self.get_dummies_cols()

        self.to_numeric_activate = self.get_to_numeric_activate()
        self.to_numeric_cols = self.get_to_numeric_cols()

        self.label_encoding_activate = self.get_label_encoding_activate()
        self.label_encoding_cols = self.get_label_encoding_cols()
        self.label_encode_target = self.get_label_encode_target()

        self.tuplize_activate = get_value(self._json_config, False, "process", "tuplize_params", "activate")
        self.tuplize_cols = self.get_tuplize_cols()

        self.date_cols_activate = self._column.date_cols_activate
        self.date_cols_params = self.get_date_cols_params()

        self.standard_scaler_activate = get_value(self._json_config, False, "process", "standard_scaler_params", "activate")
        self.standard_scaler_cols = self.get_standard_scaler_cols()

        self.min_max_scaler_activate = get_value(self._json_config, False, "process", "min_max_scaler_params", "activate")
        self.min_max_scaler_cols = self.get_min_max_scaler_cols()

        self.memory_optimization = get_value(self._json_config, False, "process", "memory_optimization")

        self.log_transform_target_activate = self.get_log_transform_target_activate()
        self.log_transform_target_base = get_value(self._json_config, e, "process", "log_transform_target", "base")
        self.log_transform_target_shift = get_value(self._json_config, 0, "process", "log_transform_target", "shift")
        self.log_transform_target_params = self.get_log_transform_target_params()
        self.log_transform_target_predict_actuals = self.get_log_transform_target_predict_actuals()
        self.log_transform_target_score_actuals = self.get_log_transform_target_score_actuals()

        self.lemmatize_activate = get_value(self._json_config, False, "process", "lemmatize_params", "activate")
        self.lemmatize_cols_params = self.get_lemmatize_cols_params()

        self.stem_activate = get_value(self._json_config, False, "process", "stem_params", "activate")
        self.stem_cols_params = self.get_stem_cols_params()

        self.count_vectorize_activate = get_value(self._json_config, False, "process", "count_vectorize_params", "activate")
        self.count_vectorize_cols_params = self.get_count_vectorize_cols_params()

        self.tfidf_activate = get_value(self._json_config, False, "process", "tfidf_params", "activate")
        self.tfidf_cols_params = self.get_tfidf_cols_params()

        self.image_transform_params = self.get_image_transform_params()

    def get_fillnan_activate(self):
        try:
            activate = self._json_config["process"]["fillnan_params"]["activate"]
            if not activate:
                warnings.warn("fillnan_activate was set to false, this may lead to errors...", UserWarning)
            return activate
        except KeyError:
            warnings.warn("Using the default value, false, for fillnan_activate, this may lead to errors...", UserWarning)
            return False

    def get_fillnan_value_cols(self):
        value_cols = {}
        try:
            value_cols = self._json_config["process"]["fillnan_params"]["value_cols"]
        except KeyError:
            value_cols = {}
        finally:
            basic_operations_names = self.get_basic_operations_names()
            log_transform_names = self.get_log_transform_names()
            self._column.valid_cols.extend(basic_operations_names + log_transform_names)
            if self.fillnan_activate:
                self._validate_update_fillnan_cols(value_cols)
            return value_cols

    def get_basic_operations_names(self):
        try:
            basic_operations_params = self._json_config["feature_engineering"]["basic_operations_params"]
            names = []
            for item in basic_operations_params:
                try:
                    names.append(item["name"])
                except KeyError:
                    pass
            return names
        except KeyError:
            return []

    def get_log_transform_names(self):
        try:
            log_transform_params = self._json_config["feature_engineering"]["log_transform_params"]
            names = []
            for item in log_transform_params:
                try:
                    names.append(item["name"])
                except KeyError:
                    pass
            return names
        except KeyError:
            return []

    def _validate_update_fillnan_cols(self, fillnan_cols):
        if self.fillnan_mean_cols:
            validate_intersection_cols(cols1=self.fillnan_mean_cols, cols2=fillnan_cols.keys(),
                                       cols1_name="mean cols", cols2_name="value cols")
            if self.fillnan_median_cols:
                validate_intersection_cols(cols1=self.fillnan_mean_cols, cols2=self.fillnan_median_cols,
                                           cols1_name="mean cols", cols2_name="median cols")
            if self.fillnan_mode_cols:
                validate_intersection_cols(cols1=self.fillnan_mean_cols, cols2=self.fillnan_mode_cols,
                                           cols1_name="mean cols", cols2_name="mode cols")

        if self.fillnan_median_cols:
            validate_intersection_cols(cols1=self.fillnan_median_cols, cols2=fillnan_cols.keys(),
                                       cols1_name="median cols", cols2_name="value cols")
            if self.fillnan_mean_cols:
                validate_intersection_cols(cols1=self.fillnan_median_cols, cols2=self.fillnan_mean_cols,
                                           cols1_name="median cols", cols2_name="mean cols")
            if self.fillnan_mode_cols:
                validate_intersection_cols(cols1=self.fillnan_median_cols, cols2=self.fillnan_mode_cols,
                                           cols1_name="median cols", cols2_name="mode cols")

        if self.fillnan_mode_cols:
            validate_intersection_cols(cols1=self.fillnan_mode_cols, cols2=fillnan_cols.keys(),
                                       cols1_name="mode cols", cols2_name="value cols")
            if self.fillnan_mean_cols:
                validate_intersection_cols(cols1=self.fillnan_mode_cols, cols2=self.fillnan_mean_cols,
                                           cols1_name="mode cols", cols2_name="mean cols")
            if self.fillnan_median_cols:
                validate_intersection_cols(cols1=self.fillnan_mode_cols, cols2=self.fillnan_median_cols,
                                           cols1_name="mode cols", cols2_name="median cols")

    def get_dummies_activate(self):
        try:
            activate = self._json_config["process"]["dummies_params"]["activate"]
            if not activate:
                warnings.warn("dummies_activate was set to false, this may lead to errors...", UserWarning)
            return activate
        except KeyError:
            warnings.warn("Using the default value, false, for dummies_activate, this may lead to errors...",
                          UserWarning)
            return False

    def get_dummies_cols(self):
        cat_cols = set()
        try:
            cat_cols = set(self._json_config["process"]["dummies_params"]["cols"])
            # for deep learning engines, on-hot encoding does not make sense because embedding basically does it
            if self._engine in ["DeepClassifier", "DeepRegressor"] and self.dummies_activate:
                logging.critical("You are using a deep learning engine. All categorical columns should be defined in "
                                 "label_encoding_params section for embedding. Please update the configuration file "
                                 "and try again. Exiting...")
                sys.exit(1)
        finally:
            if not cat_cols and self._data.meta_data:
                logging.info("No dummies cols was defined in the configuration file. Trying to get them from the "
                             "meta_data file...")
                for col in self._data.meta_data["column"]:
                    if col in self._column.use_cols:
                        if self._data.meta_data["column"][col]["type"] == "dummy":
                            cat_cols.add(col)
            return list(cat_cols)

    def get_to_numeric_activate(self):
        try:
            activate = self._json_config["process"]["to_numeric_params"]["activate"]
            if not activate:
                warnings.warn("to_numeric_activate was set to false, this may lead to errors...", UserWarning)
            return activate
        except KeyError:
            warnings.warn("Using the default value, false, for to_numeric_activate, this may lead to errors...",
                          UserWarning)
            return False

    def get_to_numeric_cols(self):
        try:
            num_cols = self._json_config["process"]["to_numeric_params"]["cols"]
            return num_cols
        except KeyError:
            return []

    def get_label_encoding_activate(self):
        try:
            activate = self._json_config["process"]["label_encoding_params"]["activate"]
            if not activate:
                warnings.warn("label_encoding_activate was set to false, this may lead to errors...", UserWarning)
            return activate
        except KeyError:
            warnings.warn("Using the default value, false, for label_encoding_activate, this may lead to errors...",
                          UserWarning)
            return False

    def get_label_encoding_cols(self):
        try:
            label_encode_cols = self._json_config["process"]["label_encoding_params"]["cols"]
            if self.label_encoding_activate and self.dummies_activate:
                validate_intersection_cols(cols1=self.dummies_cols, cols2=label_encode_cols,
                                           cols1_name='dummies cols', cols2_name='label_encoding cols')
            return label_encode_cols
        except KeyError:
            return []

    def get_label_encode_target(self):
        if self._engine in ["Classifier", "DeepClassifier"] and self.label_encoding_activate and self._column.target_col in self.label_encoding_cols:
            return True
        return False

    def get_tuplize_cols(self):
        try:
            tuplize_cols = self._json_config["process"]["tuplize_params"]["cols"]
            return tuplize_cols
        except KeyError:
            return None

    def get_date_cols_params(self):
        try:
            date_cols = self._json_config["process"]["date_cols_params"]["cols_params"]
            if self.date_cols_activate and date_cols:
                for col, date_item in date_cols.items():
                    # validate requested date items
                    validate_subset_list(DATE_ITEMS,
                                         "acceptable date items",
                                         subset_list=date_item,
                                         subset_name="requested items")

                # we know that date columns cannot be reached to the training
                diff = set(date_cols) - set(self._column.drop_from_train)
                if diff:
                    warnings.warn("The columns(s) {0} exist in date cols but not in drop_from_train. Updating"
                                  "drop_from_train to include date cols".format(diff), UserWarning)
                    self._column.drop_from_train = list(set(self._column.drop_from_train).union(set(date_cols)))

            return date_cols
        except KeyError:
            return False

    def get_standard_scaler_cols(self):
        try:
            standard_scaler_cols = self._json_config["process"]["standard_scaler_params"]["cols"]
            if self.standard_scaler_activate:
                # we need to add these columns to numeric_cols
                logging.info("Adding standard_scaler columns to numeric_cols if they are not already included")
                self.to_numeric_cols = list(set(self.to_numeric_cols).union(set(standard_scaler_cols)))
                self.to_numeric_activate = True
            return standard_scaler_cols
        except KeyError:
            return None

    def get_min_max_scaler_cols(self):
        try:
            min_max_scaler_cols = self._json_config["process"]["min_max_scaler_params"]["cols"]
            if self.min_max_scaler_activate:
                # we need to add these columns to numeric_cols
                logging.info("Adding min_max_scaler columns to numeric_cols if they are not already included")
                self.to_numeric_cols = list(set(self.to_numeric_cols).union(set(min_max_scaler_cols)))
                self.to_numeric_activate = True
            return min_max_scaler_cols
        except KeyError:
            return None

    def get_log_transform_target_activate(self):
        try:
            activate = self._json_config["process"]["log_transform_target"]["activate"]
            if activate:
                validate_subset_list(parent_list=SUPPORTED_ENGINES_FOR_TARGET_LOG_TRANSFORM,
                                     parent_name="acceptable engines for target log transform",
                                     subset_list=[self._engine],
                                     subset_name="defined engine")
            return activate
        except KeyError:
            return False

    def get_log_transform_target_params(self):
        if self.log_transform_target_activate:
            return [{"activate": True,
                     "base": self.log_transform_target_base,
                     "col": self._column.target_col,
                     "name": self._column.target_col,
                     "shift": self.log_transform_target_shift}]
        return []

    def get_log_transform_target_predict_actuals(self):
        if not self.log_transform_target_activate:
            return False
        try:
            predict_actuals = self._json_config["process"]["log_transform_target"]["predict_actuals"]
            if predict_actuals and not self._data.test_prediction_activate:
                logging.critical("prediction_params in test_params was not activated but predict_actuals in "
                                 "log_transform_target was set to true. Learner doesn't know how to proceed. "
                                 "Please update your configuration file and try again. Exiting...")
                sys.exit(1)
            return predict_actuals
        except KeyError:
            return False

    def get_log_transform_target_score_actuals(self):
        if not self.log_transform_target_activate:
            return False
        try:
            score_actuals = self._json_config["process"]["log_transform_target"]["score_actuals"]
            if score_actuals and not self._data.validation_score_activate:
                logging.critical("scoring_params in validation_params was not activated but score_actuals in "
                                 "log_transform_target was set to true. Learner doesn't know how to proceed. "
                                 "Please update your configuration file and try again. Exiting...")
                sys.exit(1)
            return score_actuals
        except KeyError:
            return False

    def get_lemmatize_cols_params(self):
        lemmatize_default_params = {"pos": ["v"]}
        try:
            cols_params = self._json_config["process"]["lemmatize_params"]["cols_params"]
            self._validate_lemmatize_params(cols_params, lemmatize_default_params)
            return cols_params
        except KeyError:
            if self.lemmatize_activate:
                logging.critical("lemmatize_params was activated but cols_params was not defined. You can either "
                                 "deactivate this feature or define cols_params. Exiting...")
                sys.exit(1)
            return []

    def _validate_lemmatize_params(self, cols_params, default_params):
        for col_param in cols_params:
            # make sure all the keys are valid
            validate_subset_list(parent_list=list(default_params.keys()) + ["name"],
                                 parent_name="acceptable fields in lemmatize cols_params",
                                 subset_list=col_param.keys(),
                                 subset_name="provided fields")

            if "name" not in col_param:
                logging.critical(f"each dictionary in cols_params in the lemmatize_params of the process section "
                                 f"should define the column name using the 'name' field. Exiting...")
                sys.exit(1)
            # make sure pos is valid
            if "pos" in col_param:
                validate_subset_list(parent_list=['a', 'r', 'n', 'v'],
                                     parent_name=f"valid pos for lemmatizer",
                                     subset_list=col_param["pos"],
                                     subset_name=f"defined pos for lemmatizer")

            # if the parameter is defined use it, otherwise use the default value
            for param, default_value in default_params.items():
                col_param[param] = col_param.get(param, default_value)

    def get_stem_cols_params(self):
        stem_default_params = {"type": "PosterStemmer",
                               "options": {}}
        try:
            cols_params = self._json_config["process"]["stem_params"]["cols_params"]
            self._validate_stem_params(cols_params, stem_default_params)
            return cols_params
        except KeyError:
            if self.stem_activate:
                logging.critical("stem_params was activated but cols_params was not defined. You can either "
                                 "deactivate this feature or define cols_params. Exiting...")
                sys.exit(1)
            return []

    def _validate_stem_params(self, cols_params, default_params):
        for col_param in cols_params:
            # make sure all the keys are valid
            validate_subset_list(parent_list=list(default_params.keys()) + ["name"],
                                 parent_name="acceptable fields in stem cols_params",
                                 subset_list=col_param.keys(),
                                 subset_name="provided fields")

            if "name" not in col_param:
                logging.critical(f"each dictionary in cols_params in the stem_params of the process section "
                                 f"should define the column name using the 'name' field. Exiting...")
                sys.exit(1)
            # make sure pos is valid
            if "type" in col_param:
                validate_subset_list(parent_list=SUPPORTED_STEMMERS,
                                     parent_name=f"valid type for stemmer",
                                     subset_list=[col_param["type"]],
                                     subset_name=f"defined pos for stemmer")

            # if the parameter is defined use it, otherwise use the default value
            for param, default_value in default_params.items():
                col_param[param] = col_param.get(param, default_value)

    def get_count_vectorize_cols_params(self):
        count_vectorize_default_params = {
            "strip_accents": None,
            "lowercase": True,
            "stop_words": None,
            "token_pattern": r"(?u)\b\w\w+\b",
            "ngram_range": [1, 1],
            "analyzer": "word",
            "max_df": 1.0,
            "min_df": 1,
            "max_features": None,
            "binary": False
        }
        try:
            cols_params = self._json_config["process"]["count_vectorize_params"]["cols_params"]
            self._validate_count_vectorize_and_tfidf_params(cols_params, count_vectorize_default_params, type_="count_vectorize")
            return cols_params
        except KeyError:
            if self.count_vectorize_activate:
                logging.critical("count_vectorize_params was activated but cols_params was not defined. You can either "
                                 "deactivate this feature or define cols_params. Exiting...")
                sys.exit(1)
            return []

    def get_tfidf_cols_params(self):
        tfidf_default_params = {
            "strip_accents": None,
            "lowercase": True,
            "stop_words": None,
            "token_pattern": r"(?u)\b\w\w+\b",
            "ngram_range": [1, 1],
            "analyzer": "word",
            "max_df": 1.0,
            "min_df": 1,
            "max_features": None,
            "binary": False,
            "norm": "l2",
            "use_idf": True,
            "smooth_idf": True,
            "sublinear_tf": False
        }
        try:
            cols_params = self._json_config["process"]["tfidf_params"]["cols_params"]
            self._validate_count_vectorize_and_tfidf_params(cols_params, tfidf_default_params, type_="tfidf")
            return cols_params
        except KeyError:
            if self.tfidf_activate:
                logging.critical("tfidf_params was activated but cols_params was not defined. You can either "
                                 "deactivate this feature or define cols_params. Exiting...")
                sys.exit(1)
            return []

    @staticmethod
    def _validate_count_vectorize_and_tfidf_params(count_vectorize_cols_params, default_params, type_):
        for col_param in count_vectorize_cols_params:
            if "name" not in col_param:
                logging.critical(f"each dictionary in cols_params in the {type_}_params of the process section "
                                 f"should define the column name using the 'name' field. Exiting...")
                sys.exit(1)
            # make sure analyzer is valid
            if "analyzer" in col_param:
                validate_subset_list(parent_list=['word', 'char', 'char_wb'],
                                     parent_name=f"valid analyzer for {type_}",
                                     subset_list=[col_param["analyzer"]],
                                     subset_name=f"defined analyzer for {type_}")
            # make sure strip_accent is valid
            if "strip_accent" in col_param:
                validate_subset_list(parent_list=['ascii', 'unicode'],
                                     parent_name=f"valid strip_accent values for {type_}",
                                     subset_list=[col_param["strip_accent"]],
                                     subset_name=f"defined strip_accent value for {type_}")

            # make sure norm is valid. This is only relevant for tfidf but we don't need to check that
            if "norm" in col_param:
                validate_subset_list(parent_list=['l1', 'l2'],
                                     parent_name=f"valid strip_accent values for {type_}",
                                     subset_list=[col_param["norm"]],
                                     subset_name=f"defined strip_accent value for {type_}")

            # if the parameter is defined use it, otherwise use the default value
            for param, default_value in default_params.items():
                col_param[param] = col_param.get(param, default_value)

            # make sure ngram_range has only two items in it
            length = len(col_param["ngram_range"])
            if length != 2:
                logging.critical(f"ngram_range in cols_params of {type_}_params should contain two integers, "
                                 f"found  {length} integers. Please update your configuration file and try again."
                                 f"Exiting...")
                sys.exit(1)
            # make sure min_n is not larger than max_n
            if col_param["ngram_range"][0] > col_param["ngram_range"][1]:
                logging.critical(f"The first number in the ngram_range {type_}_params should be smaller than "
                                 f"the second one. Please update your configuration file and try again. Exiting...")
                sys.exit(1)

    def get_image_transform_params(self):
        try:
            params = self._json_config["process"]["image_transform_params"]
            DefaultValidatingDraft7Validator(IMAGE_TRANSFORM_PARAMS).validate(params)
            image_transform_params = []
            for param in params:
                if param["activate"] is True:
                    image_transform_params.append(param)
            return image_transform_params
        except KeyError:
            return []
