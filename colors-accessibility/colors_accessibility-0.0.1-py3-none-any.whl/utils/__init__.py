from decimal import Decimal
from typing import Any, Union
from string import hexdigits

from colors_accessibility.utils.errors import IncorrectArgumentsTypingError, IncorrectHexValueError, IncorrectHslValueError, \
    IncorrectValueTypeError, NegativeNumberError


def check_if_values_are_positive(
        values: Any
) -> bool:
    incorrect_values = []
    for value in values:
        if value < 0:
            incorrect_values.append(value)
    if incorrect_values:
        raise NegativeNumberError(incorrect_values)
    return True


def check_if_correct_hex_value(
        value: str
) -> bool:
    value = value.replace('#', '')
    incorrect_values = [
        character
        for character
        in value
        if character not in hexdigits
    ]
    if incorrect_values:
        raise IncorrectHexValueError(value, incorrect_values)
    return True


def check_if_correct_hsl_values(
        values: list
) -> bool:
    check_if_values_are_positive(values)
    hue, saturation, lightness = values
    incorrect_values = {}
    if not 0 <= hue <= 360:
        incorrect_values['hue'] = hue
    if not 0 <= saturation <= 1:
        incorrect_values['saturation'] = saturation
    if not 0 <= lightness <= 1:
        incorrect_values['lightness'] = lightness
    if incorrect_values:
        raise IncorrectHslValueError(incorrect_values)
    return True


def check_if_values_are_numeric(
        values: Union[list, tuple]
) -> bool:
    incorrect_values = {}
    for value in values:
        if not type(value) in [int, float, Decimal, str]:
            incorrect_values[value] = type(value).__name__
        if type(value) == str and not value.isnumeric():
            try:
                float(value)
            except ValueError:
                incorrect_values[value] = type(value).__name__
    if incorrect_values:
        raise IncorrectValueTypeError(incorrect_values)
    return True


def normalize_value(
        value: Any,
        factor: int = 255,
        decimal_places: int = 20
) -> float:
    if value >= 1:
        value /= factor
    return round(value, decimal_places)


def normalize_hsl_values(
        values: list
) -> list:
    if 0 < values[0] < 1:
        values[0] *= 360
    if 1 < values[1] <= 100:
        values[1] /= 100
    if 1 < values[2] <= 100:
        values[2] /= 100
    return values


def normalize_values(
        values: Union[list, tuple],
        factor: int = 255,
        decimal_places: int = 20
) -> list:
    return [normalize_value(value, factor, decimal_places) for value in values]


def convert_integer_to_hex(
        number: int
) -> str:
    hex_number = hex(number)[2:]
    if len(hex_number) == 1:
        hex_number = f'{hex_number}{hex_number}'
    return hex_number


def expand_values(
        values: list,
        factor: int = 255
) -> list:
    return [
        int(value * factor)
        if 0 < value <= 1
        else value
        for value
        in values
    ]


def expand_hsl_values(
        values: list
) -> list:
    if 0 < values[1] <= 1:
        values[1] *= 100
    if 0 < values[2] <= 1:
        values[2] *= 100
    return values


def associate_input_args_with_expected_types(
        args_values: tuple,
        argument_names: list
) -> dict:
    return {
        argument: value
        for value, argument
        in zip(args_values, argument_names)
    }


def update_non_empty_values(
        dictionary_to_update: dict,
        updates_dict: dict
) -> dict:
    for key, value in updates_dict.items():
        if not dictionary_to_update.get(key):
            dictionary_to_update[key] = value
    return dictionary_to_update
