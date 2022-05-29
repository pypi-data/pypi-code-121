from decimal import Decimal
from typing import Union, List

from colors_accessibility.data.configuration_data import CONFIGURATION_DATA


class ExceededMaximumValueError(Exception):
    def __init__(
            self,
            values: List[Union[int, float, Decimal]],
            maximum_value: int,
            color_space: str
    ):
        self.values = ",\n\t".join([
            f'{value}'
            for value
            in values
        ])
        self.maximum_value = maximum_value
        self.color_space = color_space

    def __str__(self):
        return f'The maximum value for values in "{self.color_space}" color space is ' \
               f'"{CONFIGURATION_DATA.get("maximum_values").get(self.color_space)}". ' \
               f'Incorrect input values:\n\t{self.values}.'


class IncorrectArgumentsTypingError(Exception):
    def __init__(self, expected_typing_mapping: dict, incorrect_typing_mapping: dict):
        self.expected_typing_mapping = expected_typing_mapping
        self.incorrect_typing_mapping = incorrect_typing_mapping

    def __str__(self):
        arguments_message = ',\n\t'.join([
            f'{key}: {self.incorrect_typing_mapping.get(key)} -> {self.expected_typing_mapping.get(key)}'
            for key
            in self.incorrect_typing_mapping.keys()
        ])
        return f'Some of the provided arguments have incorrect typings. Incorrect arguments:\n\t{arguments_message}.'


class IncorrectColorSpaceError(Exception):
    def __init__(self, color_space_name: str, implemented_color_spaces: list):
        self.color_space_name = color_space_name
        self.implemented_color_spaces = self.values = ",\n\t".join([
            f'{value}'
            for value
            in implemented_color_spaces
        ])

    def __str__(self):
        return f'The color name space must be one of: {self.implemented_color_spaces}. ' \
               f'Input color space: "{self.color_space_name}".'


class IncorrectHexLengthError(Exception):
    def __init__(self, hex_value: str):
        self.hex_value = hex_value

    def __str__(self):
        return f'The hex value "{self.hex_value}" must be of length 3 or 6. (# sign is optional and does not count ' \
               f'toward length of value).Provided value: "{self.hex_value}" has length of {len(self.hex_value)}.'


class IncorrectHexValueError(Exception):
    def __init__(self, hex_value: str, incorrect_values: list):
        self.hex_value = hex_value
        self.incorrect_values = incorrect_values

    def __str__(self):
        return f'The hex value "{self.hex_value}" must be a valid hex value.\n' \
               f'Provided value: {self.hex_value} is not a valid hex value.\n' \
               f'Incorrect characters in input: {", ".join(self.incorrect_values)}.'


class IncorrectHslValueError(Exception):
    def __init__(self, incorrect_values_mapping: dict):
        self.incorrect_values_mapping = incorrect_values_mapping

    def __str__(self):
        message = ',\n\t'.join([
            f'{key}: {self.incorrect_values_mapping.get(key)}'
            for key
            in self.incorrect_values_mapping.keys()
        ])
        return f'The provided HSL values must be within the range of hue: [0-360], saturation: [0-1]  as % or [0-100]' \
               f' as absolute value, lightness: [0-1] as % or [0-100] as absolute value.\n' \
               f'Incorrect values:\n\t{message}.'


class IncorrectInputLengthError(Exception):
    def __init__(self, color_space: str, input_length: int):
        self.color_space = color_space
        self.input_length = input_length

    def __str__(self):
        return f'The input length for "{self.color_space}" color space must be' \
               f' {CONFIGURATION_DATA.get("lengths").get(self.color_space)}. Input length: "{self.input_length}".'


class IncorrectValueTypeError(Exception):
    def __init__(self, values_with_incorrect_types: dict):
        self.values_with_incorrect_types = ",\n\t".join([
            f'{key}: {value}'
            for key, value
            in values_with_incorrect_types.items()
        ])

    def __str__(self):
        return f'The input value must of type "decimal", "float", "int" or "str" and be convertable to numeric.\n\t' \
               f'Incorrect values with corresponding types are:\n\t{self.values_with_incorrect_types}.'


class NegativeNumberError(Exception):
    def __init__(self, values: List[Union[int, float, Decimal]]):
        self.values = ",\n\t".join([
            f'{value}'
            for value
            in values
        ])

    def __str__(self):
        return f'The input values must be positive numerics. Incorrect input values:\n\t{self.values}.'


class TypeCastingError(Exception):
    def __init__(self, values: list, expected_type: str):
        self.values = values
        self.expected_type = expected_type

    def __str__(self):
        message = ',\n\t'.join([
            f'{value}: {type(value)}'
            for value
            in self.values
        ])
        return f'Some of the provided arguments cannot be casted to the type "{self.expected_type}". ' \
               f'Incorrect values:\n\t{message}.'
