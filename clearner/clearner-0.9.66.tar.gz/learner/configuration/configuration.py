# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for parsing the instructions from the configuration file."""

import sys
import logging
from pprint import pformat

from learner.setup.setup import Setup
from learner.configuration.supported_items import *
from learner.configuration.data import DataConfiguration
from learner.configuration.column import ColumnConfiguration
from learner.configuration.process import ProcessConfiguration
from learner.configuration.validation import ValidationConfiguration
from learner.configuration.workspace import WorkspaceConfiguration
from learner.configuration.model import ModelsConfiguration
from learner.configuration.segmenter import SegmenterConfiguration
from learner.configuration.recommender import RecommenderConfiguration
from learner.configuration.similarities import SimilaritiesConfiguration
from learner.configuration.outlier import OutlierConfiguration
from learner.configuration.feature_engineering import FeatureEngineeringConfiguration
from learner.configuration.sample import SampleConfiguration
from learner.configuration.analysis import AnalysisConfiguration
from learner.configuration.connection import ConnectionConfiguration
from learner.configuration.communication import CommunicationConfiguration
from learner.configuration.combine import CombineConfiguration
from learner.validator.column_validator import ColumnValidator
from learner.validator.model_validator import ModelValidator


class Configuration(Setup):
    """Parse the json configuration and make assignments for all input variables that Learner supports. Some variables
    may not be defined in the configuration file. In that case, Learner uses default values and throws an error if that
    variable is not optional. Each section of the configuration fils is handled by a nested class."""

    def __init__(self, json_config_file=None):
        super().__init__(json_config_file)
        self.log_configuration_file()
        self.engine = self.get_engine()
        self.workspace = WorkspaceConfiguration(self._json_config, self.output_path, self.verbose_level, self.output_name)
        self.sample = SampleConfiguration(self._json_config, self.engine, self.workspace)
        self.data = DataConfiguration(self._json_config, self.workspace, self.sample, self.engine, self.sep_timetag)
        self.column = ColumnConfiguration(self._json_config, self.engine, self.data, self.sample)
        self.process = ProcessConfiguration(self._json_config, self.data, self.column, self.sample, self.engine)
        self.validation = ValidationConfiguration(self._json_config)
        self.segmenter = SegmenterConfiguration(self._json_config, self.process, self.column)
        self.model = ModelsConfiguration(self._json_config, self.sep_timetag, self.workspace, self.data, self.engine, self.segmenter)
        self.recommender = RecommenderConfiguration(self._json_config)
        self.similarities = SimilaritiesConfiguration(self._json_config)
        self.outlier = OutlierConfiguration(self._json_config, self.column, self.data, self.process)
        self.feature_engineering = FeatureEngineeringConfiguration(self._json_config, self.column, self.process)
        self.analysis = AnalysisConfiguration(self._json_config, self.column, self.workspace, self.data, self.sep_timetag, self.engine)
        self.connection = ConnectionConfiguration(self._json_config, self.data)
        self.communication = CommunicationConfiguration(self._json_config, self.connection.credentials)
        self.combine = CombineConfiguration(self._json_config, self.model, self.sep_timetag, self.workspace, self.engine, self.data)
        column_validator = ColumnValidator(self)
        column_validator.validate_columns()
        model_validator = ModelValidator(self)
        model_validator.validate_models()
        logging.info("Successfully prepared the configuration...")

    def get_engine(self):
        # remove the underscore
        engine = "".join(self._json_config["engine"].split("_"))
        # make sure the engine name is case-insensitive
        for eng in SUPPORTED_ENGINES:
            if engine.lower() == eng.lower():
                engine = eng
        if engine not in SUPPORTED_ENGINES:
            logging.error("Invalid engine, supported engines are %s. Exiting...", SUPPORTED_ENGINES)
            sys.exit(1)
        return engine

    def log_configuration_file(self):
        logging.info(f"---Printing the content of the configuration file: {self.config_filename} ---")
        # we do not want to log the license key for security reasons
        self._json_config.pop("license_key", self._json_config)
        logging.info(pformat(self._json_config))
        logging.info("---Finished printing the content of the configuration file---")

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['connection']
        return state
