import configparser
import collections
import logging
import re
import sys


class Object:
    """
    Base Object class for all objects in our system.

    Responsible For
    1. Logger Configuration (via get_logger)
    2. Conversion of data format (via create_dict, flatten, string_to_int, string_to_float, )
    3. Standard template substitution (via replace_text)
    4.

    """
    @staticmethod
    def get_logger():

        # Read application configuration
        # config = configparser.ConfigParser()
        # config.read(f"{sys.path[0]}/system/config.ini")
        #
        # # create _logger
        # logging.basicConfig(level=config['General']['log_level'], format='%(asctime)s - %(levelname)s: %(message)s')
        # _logger = logging.getLogger(config['General']['application_name'])

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("debug.log"),
                logging.StreamHandler()
            ]
        )

        return logging.getLogger()

    @staticmethod
    def create_dict(list_of_dict, keys, value_key):
        """
        Converts a list of dictionaries into a dictionary
        :param list_of_dict: List of dictionary values we want to convert
        :param keys: The first key is considered the top level key and all subsequent keys are used to insert values
        :param value_key: Key in each dictionary that will be used for the values
        :return:
        """
        result = {}
        for dict_item in list_of_dict:
            top_key_value = dict_item[keys[0]]
            if top_key_value not in result:
                result[top_key_value] = {}

            for key in keys[1:]:
                key_value = dict_item[key]
                result[top_key_value][key_value] = dict_item[value_key]

        return result

    def flatten(self, dictionary, parent_key='', sep='_'):
        items = []
        for k, v in dictionary.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(self.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def replace_text(text, key, value):
        """
        Substitutes a tag into a template.

        :return:
        """
        return text.replace(f"<!--[{key}]-->", str(value))

    @staticmethod
    def string_to_int(s):
        try:
            return int(s)
        except ValueError:
            return int('0')

    @staticmethod
    def string_to_float(s):
        try:
            return float(s)
        except ValueError:
            return float('0.00')

    @staticmethod
    def to_camel_case(text):
        """

        :param text: Text to convert to camel case
        :return:
        """
        # Replace the under bar character with a space character
        camel_case = re.sub("_", " ", text)
        camel_case = re.sub("-", " ", camel_case)

        # Capitalize each word we found in the class name
        camel_case = re.sub(r'\w+', lambda m: m.group(0).capitalize(), camel_case)

        # Remove the spaces to get the proper class name
        camel_case = re.sub(" ", "", camel_case)
        return camel_case
