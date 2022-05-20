# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Setup the configuration prior to instantiation of a Configuration object. The setup include loading and validating
the json configuration file, configuring the logging setting, and getting a timetag."""
import os
import logging
from datetime import datetime

from learner.validator.input_validator import InputValidator
from learner.setup.logger import Logger, load_json
from learner.validator.input_validator import validate_type


class Setup(Logger, InputValidator):
    """Get the timetag, load and validate the json configuration file and configure the logging settings."""
    def __init__(self, json_config_file):
        """Get a timetag and read the configuration file to validate the configuration file and configure
        logging settings."""
        # get the path and name of the configuration file
        from learner.setup.parser import get_config_file
        config_filepath, config_filename = get_config_file()
        self._json_config_file = json_config_file if json_config_file else config_filepath
        self.timetag = self.get_timetag()
        self._config_filename = config_filename if config_filename else config_filename
        self._json_config = load_json(self._json_config_file)
        self.sep_timetag = self.get_sep_timetag()
        self._schema_file = self.get_schema_file()
        self._json_schema = load_json(self._schema_file)

        # setup logging
        super().__init__(self._json_config, self.sep_timetag)
        # call the parent initializer to validate the configuration file against the schema
        logging.info("---Validation of the configuration file begins---")
        super(Logger, self).__init__(self._json_config, self._json_schema)

    @property
    def json_config_file(self):
        return self._json_config_file

    @property
    def json_config(self):
        return self._json_config

    @property
    def config_filename(self):
        return self._config_filename

    @property
    def schema_file(self):
        return self._schema_file

    @property
    def json_schema(self):
        return self._json_schema

    def get_schema_file(self):
        try:
            return self._json_config["schema_file"]
        except KeyError:  # pragma: no cover
            default_schema = os.path.join(os.path.dirname(__file__),
                                          "..",
                                          "schema",
                                          "schema.json")
            return default_schema

    @staticmethod
    def get_timetag(date_time=datetime.now()):  # pragma: no cover

        return date_time.strftime("%Y-%m-%d-%H-%M")

    def get_sep_timetag(self):
        try:
            add_timetag = self._json_config["workspace"]["add_timetag"]
            validate_type(add_timetag, bool, object_name="add_timetag", type_name="boolean")
            if not add_timetag:
                return ""
            return f"_{self.timetag}"
        except KeyError:
            return f"_{self.timetag}"
