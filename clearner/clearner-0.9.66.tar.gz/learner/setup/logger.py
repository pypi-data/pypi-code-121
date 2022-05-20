# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""logger is responsible for preparing the logging configuration. The Logger module parses the relevant information
from the configuration file and updates the default values of the logging configuration."""

import sys
import os
import json
import commentjson
import warnings
import logging.config


class Logger:
    """Get the sep_timetag and configure the logging settings using the information passed through the configuration
     file."""
    def __init__(self, json_config, sep_timetag):
        """Instantiate the Logger object using a sep_timetag and a jaosn configuration file.

        :param json_config: the path to the configuration file
        :param sep_timetag: the sep + timetag
        """

        self._json_config = json_config
        self.sep_timetag = sep_timetag
        self.output_path = self.get_output_path()
        self.output_name = self.get_output_name()
        self.create_log_file = self.get_create_log_file()
        self.verbose_level = self.get_verbose_level()
        self.setup_logging(os.path.join(os.path.dirname(__file__),
                                        "..",
                                        "schema",
                                        "logging.json"))

    @property
    def json_config(self):
        return self._json_config

    def get_output_path(self):
        try:
            path = self._json_config["workspace"]["path"]
            assert isinstance(path, str), "path must be a string"
            if path:
                if os.path.isdir(path) is False:
                    warnings.warn("The path provided is not an existing directory, attempting to create the  "
                                  "directory...")
                    try:
                        os.makedirs(path)
                    except PermissionError:  # pragma: no cover
                        print("ERROR: Could not create the directory. Please modify the path variable in the output "
                              "section of the configuration file")
                        sys.exit(1)
                    except FileNotFoundError:
                        print("ERROR: File not found. Please modify the path variable in the output section of the "
                              "configuration file")
                        sys.exit(1)
                    except Exception:  # pragma: no cover
                        print("ERROR: Please modify the path variable in the output section of the configuration file")
                        sys.exit(1)
                return os.path.abspath(path) + "/"
        except KeyError:
            return "./"

    def get_output_name(self):
        try:
            name = self._json_config["workspace"]["name"]
            assert isinstance(name, str), "name in output section must be a string"
            return name
        except KeyError:
            return "output"

    def get_create_log_file(self):
        try:
            create_log_file = self._json_config["workspace"]["create_log_file"]
            assert isinstance(create_log_file, bool), "create_log_file must be a boolean"
            return create_log_file
        except KeyError:
            return True

    def get_verbose_level(self):
        """Set the verbose level from the configuration file or set a default value. Users can specify just the first
        letter of the verbose level and Learner will correct the values.

        :return: returns and sets the verbose level, default in "INFO"
        """
        supported_verbose_levels = {"D": "DEBUG", "I": "INFO", "W": "WARNING", "E": "ERROR", "C": "CRITICAL"}
        try:
            verbose_level = self._json_config["workspace"]["verbose_level"]
            assert isinstance(verbose_level, str), "verbose level must be a string"
            verbose_level = verbose_level.upper()
            if verbose_level not in supported_verbose_levels.values():
                try:
                    return supported_verbose_levels[verbose_level[0]]
                except KeyError:
                    logging.exception("The verbose level %s is not understood", verbose_level)
                    sys.exit(1)
            return verbose_level
        except KeyError:
            return "INFO"

    def setup_logging(self, logging_path='./schema/logging.json'):
        """Setup the logging by reading the default configuration file and updating the values using the values passed
        to the configuration file

        :param logging_path: the path to the default logging configuration file
        :return: None
        """
        log_directory = self._create_log_directory()
        logging_config = load_json(logging_path)
        self._update_logger_config(logging_config, log_directory)
        logging.captureWarnings(True)
        logging.config.dictConfig(logging_config)

    def _create_log_directory(self):
        """Create a directory to save the log files there

        :return: the path to the log directory
        """
        log_directory = self.output_path + "log/"
        if self.create_log_file:
            if not os.path.exists(log_directory):  # pragma: no cover
                os.makedirs(log_directory)
        return log_directory

    def _update_logger_config(self, logger_config, log_directory):
        """Update the logger configuration using the verbose_level passed through the configuration file as well as
        create_log_file flag

        :param logger_config: a dictionary containing the logging configuration
        :param log_directory: the path to the log directory
        :return: None
        """
        logger_config["loggers"][""]["level"] = self.verbose_level
        if self.create_log_file:  # pragma: no cover
            logger_config["handlers"]["file"]["filename"] = log_directory + self.output_name + str(self.sep_timetag) + ".txt"
        else:
            del logger_config["handlers"]["file"]
            logger_config["loggers"][""]["handlers"] = ["console"]


def load_json(source):
    """Load the json file.

    :param source: the path to a json file
    :return: the loaded json object
    """
    try:
        # first try to use the builtin library to load the file assuming it doesn't contain any comments. If it fails,
        # we'll use commentjson to load the file
        with open(source, "r") as stream:
            json_config = json.load(stream)
    except Exception:
        with open(source, "r") as stream:
            json_config = commentjson.load(stream)
    return json_config
