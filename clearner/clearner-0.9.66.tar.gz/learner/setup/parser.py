# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""A parser module responsible for parsing command line arguments and other parsing tasks as they emerge."""

import sys
import os
import ntpath


def get_filename_from_path(path):
    """Extract the filename from the filepath.

    :param path: the filepath
    :return: return the file name (after the final slash).
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_config_file():  # pragma: no cover
    """Get the path to the configuration file. If nothing is provided, use a sample configuration file from the config
     folder

    :return: the path to a configuration file
    """
    try:
        config_path = sys.argv[1]
        config_file = os.path.abspath(config_path)
        current_path = os.path.dirname(os.path.realpath(__file__))
        parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
        os.chdir(parent_path)
    except IndexError:
        config_file = "config/classifier.json"
    config_filename = get_filename_from_path(config_file)
    if os.path.exists(config_file):
        return config_file, config_filename
    return config_file, config_filename