# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Validate a json configuration file against a json schema."""

import sys
import re
from datetime import datetime
import logging
import numpy as np
import valideer as v


class InputValidator:

    def __init__(self, json_config, json_schema):
        """Accept a json configuration and a schema to instantiate an InputValidator object."""

        self._json_config = json_config
        self._json_schema = json_schema
        self.validate_input_file()

    @property
    def json_config(self):
        return self._json_config

    @property
    def json_schema(self):
        return self._json_schema

    def validate_input_file(self):
        """Wrapper to validation functions required to validate input file."""

        self.validate_config_structure()
        validate_subset_dict(self._json_schema, self._json_config)
        logging.info("---Successfully validated the file---")

    def validate_config_structure(self):
        """Validate the json file using the validate method of valideer.

        :return: None
        :raises: ValidationError if the validation is not successful
        """
        logging.info("Validating the skeleton of the file...")
        validator = v.parse(self._json_schema)
        try:
            validator.validate(self._json_config)
            logging.info("Successfully validated the skeleton of the file")

        except v.base.ValidationError as e:
            logging.exception("Input validation failed. Please check your input and try again... \n %s", str(e))
            raise


def validate_subset_cols(use_cols=None, subset_cols=None, subset_cols_name='subset_cols'):
    """Accept two lists, use_cols and subset_cols, and issue an error if subset_cols is not a subset of use_cols.

    :param use_cols: the parent list (this is usually the use_cols field in the configuration file)
    :param subset_cols: a subset of the use_cols. This is usually other fields in column section, e.g. fillnan_cols
    :param subset_cols_name: a string that will be used to print an output message
    :return: None
    """
    logging.info("Checking if %s exist in valid columns...", subset_cols_name)
    diff = set(subset_cols) - set(use_cols)
    if diff:
        logging.critical("The columns %s do not exist in valid columns. Exiting...", diff)
        sys.exit(1)


def validate_subset_list(parent_list=None, parent_name=None, subset_list=None, subset_name=None):
    """Check if a list is a subset of another list or not.

    :param parent_list: the parent list (the bigger list)
    :param parent_name: a string that indicates the name of the parent list
    :param subset_list: the subset list (the smaller list)
    :param subset_name: a string that indicates the name of the subset list
    :return: None
    """
    logging.info("Checking if %s exist in %s...", subset_name, parent_name)
    diff = set(subset_list) - set(parent_list)
    if diff:
        logging.critical("Invalid item(s): %s. Exiting...", diff)
        sys.exit(1)


def validate_intersection_cols(cols1=None, cols2=None, cols1_name="cols1", cols2_name="cols2"):
    """Accept two lists and issue an error if there is an intersection between the two.

    :param cols1: a list of columns of a category type
    :param cols2: a list of columns of a category type
    :param cols1_name: a string associated with the name of cols1 (this is used to print an output message)
    :param cols2_name: a string associated with the name of cols2 (this is used to print an output message)
    :return: None
    """
    logging.info("Checking whether %s and %s have an intersection...", cols1_name, cols2_name)
    if cols1 and cols2:
        inter = set(cols1).intersection(set(cols2))

        if inter:
            logging.critical("%s and %s both contain %s. These two must be mutually exclusive. Exiting...",
                          cols1_name, cols2_name, inter)
            sys.exit(1)


def validate_subset_dict(parent_dict=None, subset_dict=None, *args):
    """Accept two dictionaries, parent_dict and subset_dict, and issue an error if subset_dict has keys that
    do not exist in the parent_dict

    :param parent_dict: the parent dictionary that validation will be performed against
    :param subset_dict: the subset dictionary that needs to be validated
    :return: list of strings used to print an output message
    :raise: Error if sub-field(s) exist in config but not in schema due to a typo
    :raise: Warning if default values to be used
    """
    schema_keys = [re.sub('^\+', '', key) for key in parent_dict.keys()]
    diff = set(subset_dict.keys()) - set(schema_keys)

    if diff:
        logging.critical("Input validation failed. Make sure configuration json file matches the schema. "
                         "The error is %s:%s in config file are not contained in schema file. Exiting...",
                         ":".join(list(args)), diff)
        sys.exit(1)

    for key in parent_dict.keys():
        try:
            key_val = re.sub('^\+', '', key)
            if isinstance(parent_dict[key], dict) and parent_dict[key]:
                validate_subset_dict(parent_dict[key], subset_dict[key_val], key_val)
        except KeyError:
            logging.info(f"No parameters for the optional field '{key}' was provided. Learner will use the default "
                         f"values for all subfields.")


def remove_subset_list(parent_list, subset_list):
    """Accepts two lists and returns an updated parent list (without modifying the original). This function does not
    raise an error if the elements of the subset_list do not exist in the parent_list

    :param parent_list: the parent list the removing operation will be performed on
    :param subset_list: a subset_list that should be removed from the parent list if the elements exist in the parent list
    :return: an updated copy of parent list after removing subset_cols
    """
    tmp_list = parent_list[:]
    for col in subset_list:
        if col in tmp_list:
            tmp_list.remove(col)
    return tmp_list


def validate_in_range(numbers, minimum=-np.inf, maximum=np.inf):
    """Check if a number or a list of numbers fall within a range (inclusive). If not, issue an error. This function
    skips None in case it appears in the list, i.e. it does not raise an error for None

    :param numbers: a single number or a list of numbers
    :param minimum: the minimum value for defining the range
    :param maximum: the maximum value for defining the range
    :return: None
    """
    logging.info("Checking if the numbers are between {minimum} and {maximum}".format(minimum=minimum, maximum=maximum))
    # convert the numbers to list
    if not numbers:
        return
    if isinstance(numbers, (int, float)):
        numbers = [numbers]

    for number in numbers:
        # make sure we don't exit on None items
        if number is None:
            continue
        if not minimum <= number <= maximum:
            logging.error("The number {number} is not between {minimum} and {maximum}. Exiting...".
                          format(number=number,
                                 minimum=minimum,
                                 maximum=maximum))
            sys.exit(1)


def validate_type(object_, type_, object_name, type_name):
    """Get an object and validate its type. Provide a message to explain why the validation failed.

    :param object_: the object that we need to check its type
    :param type_: the type we want the object to have
    :param object_name: the name of the object. This will be used for logging purposes
    :param type_name: the name that we want to use for target type. This can be a user-friendly name
    :return: None
    """
    logging.info(f"Checking if the {object_name} is of type {type_name}")

    if not isinstance(object_, type_):
        logging.error(f"The {object_name} does not have the correct type. Expected {type_} got {type(object_)}")
        sys.exit(1)


def validate_date_format(date: str, date_format: str="%Y-%m-%d", field_name: str=None) -> None:
    """Accept a date and a date format to validate the format of the date. If the format of the date is invalid, issue
    an error. An optional field_name can also be provided for a more descriptive log. The field name would hint the
    user what field in the configuration file is being validated.

    :param date: a string that indicates a date
    :param date_format: the format to use for checking the format of the date
    :param field_name: the field name in the configuration file used for logging purposes
    :return: None
    """
    if field_name:
        logging.info(f"Validating the date format in {field_name} to make sure it follows the format: {date_format}")
    else:
        logging.info(f"Validating {date} to make sure it follows the format: {date_format}")

    try:
        datetime.strptime(date, date_format)
    except ValueError:
        logging.critical(f"The date '{date}' has an invalid format. The format should be {date_format}. Exiting...")
        sys.exit(1)
