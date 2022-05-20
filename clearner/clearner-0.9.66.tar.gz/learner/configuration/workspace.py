# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import logging
import os
import sys

from learner.data_worker.data_loader import get_value


class WorkspaceConfiguration:
    """Parse all input variables related to the workspace section including the name of the files and the method
    for saving the files."""

    def __init__(self, json_config, output_path, verbose_level, output_name):
        self._json_config = json_config

        self.path = output_path
        self.verbose_level = verbose_level
        self.name = output_name
        self.concat_output = get_value(self._json_config, True, "workspace", "concat_output")
        self.data_directory = self.get_data_directory()
        self.s3_activate = get_value(self._json_config, False, "workspace", "s3_params", "activate")
        self.s3_path = self.get_s3_path()

    def get_data_directory(self):  # pragma: no cover
        # create a directory called "data" under output.path to save the split data there. Currently, this is the first
        # place that needs to handle this. This may change in the future.
        data_directory = self.path + "data/"
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        return data_directory

    def get_s3_path(self):
        try:
            path = self._json_config["workspace"]["s3_params"]["path"]
            if self.s3_activate and not path.startswith("s3://"):
                logging.critical("s3 was activated but 'path' does not start with 's3://'. Please update your "
                                 "configuration file and try again. Exiting...")
                sys.exit(1)
            return path
        except KeyError:
            if self.s3_activate:
                logging.critical("s3_params was activated but 'path' is not defined. Please update your configuration "
                                 "file and try again. Exiting...")
                sys.exit(1)
            return None
