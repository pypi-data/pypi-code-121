import json
from collections.abc import Iterable
from cerberus import Validator
from cerberus.errors import ValidationError
from dotpyle.utils import constants

class ConfigChecker:
    """
    Class to check the validity of the config file.
    """

    def __init__(self, config_file=constants.CONFIG_SCHEMA_PATH):
        """
        Initialize the ConfigChecker class.

        :param config_file: The path to the config file.
        """
        self.config_file = config_file
        self.schema = self.load_schema()
        self.validator = Validator(self.schema)

    def load_schema(self):
        """
        Load the schema definition file.

        :return: The schema definition.
        """
        with open(self.config_file, "r") as schema_file:
            return json.load(schema_file)

    def check_config(self, config: str) -> Iterable[ValidationError]:
        """
        Check the config file against the schema.

        :param config: The config file.
        :return: The list of errors.
        """

        self.validator.validate(config)
        return self.validator.errors
