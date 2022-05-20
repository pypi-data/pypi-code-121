# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import os
import warnings
import logging
from pathlib import Path
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

from learner.validator.input_validator import InputValidator, validate_subset_list
from learner.data_worker.data_loader import get_meta_data as data_worker_get_meta_data
from learner.configuration.workspace import WorkspaceConfiguration
from learner.configuration.sample import SampleConfiguration
from learner.configuration.supported_items import (SUPPORTED_DB_TYPES, SUPPORTED_SCORE_TYPES, SUPPORTED_INPUT_TYPES,
                                                   SUPPORTED_FILE_FORMATS)
from learner.data_worker.data_loader import get_value
from learner.setup.setup import load_json
from learner.utilities.templates import TRAIN_VALIDATION_SPLIT


class DataConfiguration:
    """Parse all input variables in the file section including the location of the train/test files, nrows, etc."""

    def __init__(self, json_config, workspace: WorkspaceConfiguration, sample: SampleConfiguration, engine, sep_timetag):
        self._json_config = json_config
        self._workspace = workspace
        self._sample = sample
        self._engine = engine
        self.sep_timetag = sep_timetag

        self.train_format = self.get_train_format()
        self.validation_format = self.get_validation_format()
        self.test_format = self.get_test_format()

        self.sample_validation_filename = TRAIN_VALIDATION_SPLIT.format(output_name=self.output.name,
                                                                        dtype="validation",
                                                                        sep_timetag=self.sep_timetag,
                                                                        format=self.validation_format)

        self.sample_train_filename = TRAIN_VALIDATION_SPLIT.format(output_name=self.output.name,
                                                                   dtype="train",
                                                                   sep_timetag=self.sep_timetag,
                                                                   format=self.train_format)

        self.train_location = get_value(self._json_config, None, "data", "train_params", "location")
        self.validation_location = self.get_validation_location()
        self.test_location = get_value(self._json_config, None, "data", "test_params", "location")

        self.train_input_type = self.get_train_input_type()
        self.validation_input_type = self.get_validation_input_type()
        self.test_input_type = self.get_test_input_type()

        self.meta_data_file = get_value(self._json_config, None, "data", "meta_data_file")
        self.meta_data_schema_file = get_value(self._json_config,
                                               str(Path(__file__).resolve().parents[1] / "schema" / "meta_data.schema.json"),
                                               "data",
                                               "meta_data_schema_file")
        self.meta_data_schema = load_json(self.meta_data_schema_file)
        self.meta_data = self.get_meta_data()
        self.manifest = get_value(self._json_config, None, "data", "manifest")

        self.train_delimiter = self.get_train_delimiter()
        self.validation_delimiter = self.get_validation_delimiter()
        self.test_delimiter = self.get_test_delimiter()

        self.train_nrows = get_value(self._json_config, None, "data", "train_params", "nrows")
        self.validation_nrows = get_value(self._json_config, None, "data", "validation_params", "nrows")
        self.test_nrows = get_value(self._json_config, None, "data", "test_params", "nrows")

        self.train_header = self.get_train_header()
        self.validation_header = self.get_validation_header()
        self.test_header = self.get_test_header()

        self.train_sample_size = self.get_train_sample_size()
        self.validation_sample_size = self.get_validation_sample_size()
        self.test_sample_size = self.get_test_sample_size()

        self.train_sample_seed = get_value(self._json_config, 42, "data", "train_params", "sample_seed")
        self.validation_sample_seed = get_value(self._json_config, 42, "data", "validation_params", "sample_seed")
        self.test_sample_seed = get_value(self._json_config, 42, "data", "test_params", "sample_seed")

        self.test_chunksize = self.get_test_chunksize()

        self.train_query_activate = self.get_train_query_activate()
        self.validation_query_activate = self.get_validation_query_activate()
        self.test_query_activate = self.get_test_query_activate()

        self.train_db_type = self.get_train_db_type()
        self.validation_db_type = self.get_validation_db_type()
        self.test_db_type = self.get_test_db_type()

        self.train_query_file = self.get_train_query_file()
        self.validation_query_file = self.get_validation_query_file()
        self.test_query_file = self.get_test_query_file()

        self.train_query = self.get_train_query()
        self.validation_query = self.get_validation_query()
        self.test_query = self.get_test_query()

        self.train_query_save_to_file = get_value(self._json_config, False, "data", "train_params", "query_params", "save_to_file")
        self.validation_query_save_to_file = get_value(self._json_config, False, "data", "validation_params", "query_params", "save_to_file")
        self.test_query_save_to_file = get_value(self._json_config, False, "data", "test_params", "query_params", "save_to_file")

        self.validation_prediction_type = None
        self.validation_score_activate = self.get_validation_score_activate()
        self.validation_score_types = self.get_validation_score_types()
        self.validation_add_timetag = get_value(self._json_config, True, "data", "validation_params", "scoring_params", "add_timetag")
        self.validation_column_name = get_value(self._json_config, "prediction", "data", "validation_params", "scoring_params", "column_name")
        self.validation_join_cols = self.get_validation_join_cols()

        self.test_prediction_activate = self.get_test_prediction_activate()
        self.test_prediction_type = self.get_test_prediction_type()
        self.test_add_timetag = get_value(self._json_config, True, "data", "test_params", "prediction_params", "add_timetag")
        self.test_clean_up = get_value(self._json_config, True, "data", "test_params", "prediction_params", "clean_up")
        self.test_column_name = get_value(self._json_config, "prediction", "data", "test_params", "prediction_params", "column_name")

        self.train_batch_size = get_value(self._json_config, 64, "data", "train_params", "batch_size")
        self.validation_batch_size = get_value(self._json_config, 64, "data", "validation_params", "batch_size")
        self.test_batch_size = get_value(self._json_config, 64, "data", "test_params", "batch_size")

    @property
    def output(self):  # pragma: no cover
        return self._workspace

    @property
    def sample(self):
        return self._sample

    def get_validation_location(self):
        try:
            location = self._json_config["data"]["validation_params"]["location"]
            if self.sample.split_activate:
                logging.critical("train_test_split was activated and validation location was also provided. "
                                 "Your intention is not clear to Learner. Please either remove the validation location "
                                 "or set train_test_split to false. Exiting...")
                sys.exit(1)
            return location
        except KeyError:
            if self.sample.split_activate:
                return self.output.data_directory + self.sample_validation_filename
            return None

    def get_train_input_type(self):
        # we don't need to validate the location here because it happens somewhere else and the need for validation
        # depends on other parameters
        if self.train_location and os.path.exists(self.train_location):
            if os.path.isfile(self.train_location):
                return "file"
            elif os.path.isdir(self.train_location):
                return "folder"

    def get_validation_input_type(self):
        # we don't need to validate the location here because it happens somewhere else and the need for validation
        # depends on other parameters
        if self.validation_location and self.validation_location:
            if os.path.exists(self.validation_location):
                if os.path.isfile(self.validation_location):
                    return "file"
                elif os.path.isdir(self.validation_location):
                    return "folder"

    def get_test_input_type(self):
        # we don't need to validate the location here because it happens somewhere else and the need for validation
        # depends on other parameters
        if self.test_location and self.test_location:
            if os.path.exists(self.test_location):
                if os.path.isfile(self.test_location):
                    return "file"
                elif os.path.isdir(self.test_location):
                    return "folder"

    def get_meta_data(self):
        if self.meta_data_file:
            self.meta_data = data_worker_get_meta_data(self.meta_data_file)
            logging.info("---Validating the meta data---")
            InputValidator(self.meta_data, self.meta_data_schema)
            return self.meta_data
        return None

    def get_train_delimiter(self):
        try:
            delimiter = self._json_config["data"]["train_params"]["delimiter"]
            if delimiter == "" or delimiter == " ":
                warnings.warn("An empty string was passed for train delimiter, using the default delimiter ','",
                              UserWarning)
                return ","
            return delimiter
        except KeyError:
            return ","

    def get_validation_delimiter(self):
        try:
            delimiter = self._json_config["data"]["validation_params"]["delimiter"]
            if delimiter == "" or delimiter == " ":
                warnings.warn("An empty string was passed for validation delimiter, using the default delimiter ','",
                              UserWarning)
                return ","
            return delimiter
        except KeyError:
            logging.info(f"The delimiter for validation data was not defined. Setting it to train delimiter {self.train_delimiter}")
            return self.train_delimiter

    def get_test_delimiter(self):
        try:
            delimiter = self._json_config["data"]["test_params"]["delimiter"]
            if delimiter == "" or delimiter == " ":
                warnings.warn("An empty string was passed for test delimiter, using the default delimiter ','",
                              UserWarning)
                return ","
            return delimiter
        except KeyError:
            logging.info(f"The delimiter for test data was not defined. Setting it to train delimiter {self.train_delimiter}")
            return self.train_delimiter

    def get_train_header(self):
        if self.manifest:
            return None
        else:
            try:
                return self._json_config["data"]["train_params"]["header"]
            except KeyError:
                return 0

    def get_validation_header(self):
        if self.manifest:
            return None
        else:
            try:
                return self._json_config["data"]["validation_params"]["header"]
            except KeyError:
                logging.info(f"The header for validation data was not defined. Setting it to train header {self.train_header}")
                return self.train_header

    def get_test_header(self):
        if self.manifest:
            return None
        else:
            try:
                return self._json_config["data"]["test_params"]["header"]
            except KeyError:
                logging.info(f"The header for test data was not defined. Setting it to train header {self.train_header}")
                return self.train_header

    def get_train_format(self):
        try:
            format_ = self._json_config["data"]["train_params"]["format"]
            validate_subset_list(parent_list=SUPPORTED_FILE_FORMATS, parent_name="supported file formats",
                                 subset_list=[format_], subset_name="defined file format")
            return format_
        except KeyError:
            return "csv"

    def get_validation_format(self):
        try:
            format_ = self._json_config["data"]["validation_params"]["format"]
            validate_subset_list(parent_list=SUPPORTED_FILE_FORMATS, parent_name="supported file formats",
                                 subset_list=[format_], subset_name="defined file format")
            return format_
        except KeyError:
            return "csv"

    def get_test_format(self):
        try:
            format_ = self._json_config["data"]["test_params"]["format"]
            validate_subset_list(parent_list=SUPPORTED_FILE_FORMATS, parent_name="supported file formats",
                                 subset_list=[format_], subset_name="defined file format")
            return format_
        except KeyError:
            return "csv"

    def get_train_sample_size(self):
        try:
            sample_size = self._json_config["data"]["train_params"]["sample_size"]
            if self.train_nrows is not None:
                warnings.warn("Both nrows and sample_size are defined for train data. Skipping nrows and using sample_size...",
                              UserWarning)
            return sample_size
        except KeyError:
            return None

    def get_validation_sample_size(self):
        try:
            sample_size = self._json_config["data"]["validation_params"]["sample_size"]
            if self.validation_nrows is not None:
                warnings.warn("Both nrows and sample_size are defined for validation data. Skipping nrows and using sample_size...",
                              UserWarning)
            return sample_size
        except KeyError:
            return None

    def get_test_sample_size(self):
        try:
            sample_size = self._json_config["data"]["test_params"]["sample_size"]
            if self.test_nrows is not None:
                warnings.warn("Both nrows and sample_size are defined for test data. Skipping nrows and using sample_size...",
                              UserWarning)
            return sample_size
        except KeyError:
            return None

    def get_test_chunksize(self):
        try:
            min_chunksize = 20000
            chunksize = self._json_config["data"]["test_params"]["chunksize"]
            if chunksize < min_chunksize:
                warnings.warn(f"chunksize was set to {chunksize} which is smaller than {min_chunksize}. Using chunksize = {min_chunksize} "
                              "for making predictions...", UserWarning)
                return min_chunksize
            return chunksize
        except KeyError:
            return 200000

    def get_train_query_activate(self):
        try:
            activate = self._json_config["data"]["train_params"]["query_params"]["activate"]
            if activate and "query" not in SUPPORTED_INPUT_TYPES[self._engine]:
                logging.critical(f"train query_params was activated for {self._engine} but this engine does not support "
                                 f"queries. Please update your configuration file and try again. Exiting...")
                sys.exit(1)
            if activate and self.train_location:
                logging.critical("train location was provided and train query_params was also activated. Learner "
                                 "does not know how to proceed in this situation. Please provide one of these "
                                 "options. Exiting...")
                sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_validation_query_activate(self):
        try:
            activate = self._json_config["data"]["validation_params"]["query_params"]["activate"]
            if activate and "query" not in SUPPORTED_INPUT_TYPES[self._engine]:
                logging.critical(f"validation query_params was activated for {self._engine} but this engine does not support "
                                 f"queries. Please update your configuration file and try again. Exiting...")
                sys.exit(1)
            if activate and self.validation_location:
                logging.critical("validation location was provided and validation query_params was also activated. "
                                 "Learner does not know how to proceed in this situation. Please provide one of these "
                                 "options. Exiting...")
                sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_test_query_activate(self):
        try:
            activate = self._json_config["data"]["test_params"]["query_params"]["activate"]
            if activate and "query" not in SUPPORTED_INPUT_TYPES[self._engine]:
                logging.critical(f"test query_params was activated for {self._engine} but this engine does not support "
                                 f"queries. Please update your configuration file and try again. Exiting...")
                sys.exit(1)
            if activate and self.test_location:
                logging.critical("""
                test location was provided and test query_params was also activated. Learner does not know how to 
                proceed in this situation. Please provide one of these options. Exiting...
                """)
                sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_train_db_type(self):
        if self.train_query_activate:
            try:
                db_type = self._json_config["data"]["train_params"]["query_params"]["db_type"].lower()
                validate_subset_list(parent_list=SUPPORTED_DB_TYPES, parent_name="supported db types",
                                     subset_list=[db_type], subset_name="defined db type")
                return db_type
            except KeyError:
                return "presto"

    def get_validation_db_type(self):
        if self.validation_query_activate:
            try:
                db_type = self._json_config["data"]["validation_params"]["query_params"]["db_type"].lower()
                validate_subset_list(parent_list=SUPPORTED_DB_TYPES, parent_name="supported db types",
                                     subset_list=[db_type], subset_name="defined db type")
                return db_type
            except KeyError:
                return "presto"

    def get_test_db_type(self):
        if self.test_query_activate:
            try:
                db_type = self._json_config["data"]["test_params"]["query_params"]["db_type"].lower()
                validate_subset_list(parent_list=SUPPORTED_DB_TYPES, parent_name="supported db types",
                                     subset_list=[db_type], subset_name="defined db type")
                return db_type
            except KeyError:
                return "presto"

    def get_train_query_file(self):
        if self.train_query_activate:
            try:
                query_file = self._json_config["data"]["train_params"]["query_params"]["query_file"]
                if not os.path.isfile(query_file):
                    logging.critical("query_file is defined in the train_params section but it does not point to "
                                     "a valid file. Please update the configuration file and try again. Exiting...")
                    sys.exit(1)
                return query_file
            except KeyError:
                return None

    def get_validation_query_file(self):
        if self.validation_query_activate:
            try:
                query_file = self._json_config["data"]["validation_params"]["query_params"]["query_file"]
                if not os.path.isfile(query_file):
                    logging.critical("query_file is defined in the validation_params section but it does not point to "
                                     "a valid file. Please update the configuration file and try again. Exiting...")
                    sys.exit(1)
                return query_file
            except KeyError:
                return None

    def get_test_query_file(self):
        if self.test_query_activate:
            try:
                query_file = self._json_config["data"]["test_params"]["query_params"]["query_file"]
                if not os.path.isfile(query_file):
                    logging.critical("query_file is defined in the test_params section but it does not point to "
                                     "a valid file. Please update the configuration file and try again. Exiting...")
                    sys.exit(1)
                return query_file
            except KeyError:
                return None

    def get_train_query(self):
        if self.train_query_activate:
            try:
                return self._json_config["data"]["train_params"]["query_params"]["query"]
            except KeyError:
                # get the query from the query_file if it was provided
                if self.train_query_file:
                    spec = spec_from_loader("query_file", SourceFileLoader("query_file", self.train_query_file))
                    query_file = module_from_spec(spec)
                    spec.loader.exec_module(query_file)
                    try:
                        return query_file.train_query.strip()
                    except Exception as e:
                        logging.critical(f"Learner is not able to load the train_query from the query file. "
                                         f"The error is {e}. Exiting...")
                        sys.exit(1)
                logging.critical("""
                Learner was instructed to get train data using a query but no query or query_file was provided.
                Please update the configuration file and retry. Exiting...
                """)
                sys.exit(1)

    def get_validation_query(self):
        if self.validation_query_activate:
            try:
                return self._json_config["data"]["validation_params"]["query_params"]["query"]
            except KeyError:
                # get the query from the query_file if it was provided
                if self.validation_query_file:
                    spec = spec_from_loader("query_file", SourceFileLoader("query_file", self.validation_query_file))
                    query_file = module_from_spec(spec)
                    spec.loader.exec_module(query_file)
                    try:
                        return query_file.validation_query.strip()
                    except Exception as e:
                        logging.critical(f"Learner is not able to load the validation_query from the query file. "
                                         f"The error is {e}. Exiting...")
                        sys.exit(1)
                logging.critical("""
                Learner was instructed to get validation data using a query but no query or query_file was provided.
                Please update the configuration file and retry. Exiting...
                """)
                sys.exit(1)

    def get_test_query(self):
        if self.test_query_activate:
            try:
                return self._json_config["data"]["test_params"]["query_params"]["query"]
            except KeyError:
                # get the query from the query_file if it was provided
                if self.test_query_file:
                    spec = spec_from_loader("query_file", SourceFileLoader("query_file", self.test_query_file))
                    query_file = module_from_spec(spec)
                    spec.loader.exec_module(query_file)
                    try:
                        return query_file.test_query.strip()
                    except Exception as e:
                        logging.critical(f"Learner is not able to load the test_query from the query file. "
                                         f"The error is {e}. Exiting...")
                        sys.exit(1)
                logging.critical("""
                Learner was instructed to get test data using a query but no query or query_file was provided.              
                Please update the configuration file and retry. Exiting...
                """)
                sys.exit(1)

    def get_validation_score_activate(self):
        try:
            score = self._json_config["data"]["validation_params"]["scoring_params"]["activate"]
            if score and not self.sample.split_activate and not self.validation_query_activate and not self.validation_location:
                logging.error("It was requested to score the validation data but no query or location is provided "
                              "for the validation data, and train data is not being split. Please update the "
                              "configuration file and try again. Exiting...")
                sys.exit(1)
            return score
        except KeyError:
            return False

    def get_validation_score_types(self):
        score_types_dict = {}
        try:
            score_types_list = self._json_config["data"]["validation_params"]["scoring_params"]["types"]
            if score_types_list:
                if self.validation_score_activate is False:
                    warnings.warn("score types is not empty and scoring_params is not activated.", UserWarning)
                    return {}
                for score_type in score_types_list:
                    if isinstance(score_type, dict):
                        try:
                            score_types_dict[score_type["type"]] = score_type["params"]
                        except KeyError:
                            logging.exception("When passing a dictionary as an item to score_types, both type and "
                                              "params key must be present. The value of params can be a empty "
                                              "dictionary. Scoring type can also be a single string if you there "
                                              "is no extra parameters for the score type Exiting...")
                            sys.exit(1)
                    elif isinstance(score_type, str):
                        score_types_dict[score_type] = {}
                    else:
                        logging.error("Elements in score types must be either a string or a dictionary. "
                                      "Exiting...")
                        sys.exit(1)
        except KeyError:
            if self.validation_score_activate:
                warnings.warn("scoring_params was activated but no score types was defined.", UserWarning)
                self.validation_score_activate = False
            return score_types_dict

        self.validate_score_types(score_types_dict)
        self.update_validation_prediction_type(score_types_dict)
        return score_types_dict

    def get_validation_join_cols(self):
        try:
            join_cols = self._json_config["data"]["validation_params"]["scoring_params"]["join_cols"]
        except KeyError:
            join_cols = []
        return join_cols

    def validate_score_types(self, score_types_dict):
        if self.validation_score_activate:
            for score_type, params in score_types_dict.items():
                if score_type not in SUPPORTED_SCORE_TYPES[self._engine]:
                    if "file" in params:
                        self._get_score_function(score_type, params)
                    else:
                        logging.error("Invalid types in 'scoring_params', supported score types for %s engine "
                                      "are %s. Exiting...", self._engine, sorted(SUPPORTED_SCORE_TYPES[self._engine]))
                        sys.exit(1)

    def _get_score_function(self, score_type, params):
        spec = spec_from_loader("score_file", SourceFileLoader("score_file", params["file"]))
        score_file = module_from_spec(spec)
        spec.loader.exec_module(score_file)
        try:
            params["function"] = getattr(score_file, score_type)
        except Exception as e:
            logging.critical(f"Learner is not able to load the score function from the score file. "
                             f"The error is {e}. Exiting...")
            sys.exit(1)

    def update_validation_prediction_type(self, score_types_dict):
        required_pred_type = set()
        if self.validation_score_activate:
            for score_type, params in score_types_dict.items():
                if "file" not in params:
                    required_pred_type.add(SUPPORTED_SCORE_TYPES[self._engine][score_type])
                    if len(required_pred_type) > 1:
                        self.validation_prediction_type = "all"
                    else:
                        self.validation_prediction_type = list(required_pred_type)[0]

    def get_test_prediction_activate(self):
        try:
            activate = self._json_config["data"]["test_params"]["prediction_params"]["activate"]
            if activate:
                if self.test_location:
                    if ("folder" in SUPPORTED_INPUT_TYPES[self._engine] and not os.path.exists(self.test_location)) or \
                       ("folder" not in SUPPORTED_INPUT_TYPES[self._engine] and not os.path.isfile(self.test_location)):
                        logging.error("prediction_params was activated but the test_location does not point "
                                      "to a valid location. Exiting...")
                        sys.exit(1)
                elif not self.test_query_activate and "query" in SUPPORTED_INPUT_TYPES[self._engine]:
                    logging.error("prediction_params was activated . However, no location or query was Provided. "
                                  "Exiting...")
                    sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_test_prediction_type(self):
        supported_prediction_types = ['proba', 'class', 'all']
        try:
            prediction_type = self._json_config["data"]["test_params"]["prediction_params"]["type"]
            # guess the prediction_type based on the first few characters
            if prediction_type.lower().startswith('c'):
                prediction_type = "class"
            if prediction_type.lower().startswith('p'):
                prediction_type = "proba"
            if prediction_type.lower().startswith('a'):
                prediction_type = "all"

            if not any(prediction_type.lower().startswith(p_type) for p_type in supported_prediction_types):
                logging.error("Prediction type provided is invalid. Please choose from the following options: %s",
                              supported_prediction_types)
                sys.exit(1)
            return prediction_type
        except KeyError:
            return "proba"

