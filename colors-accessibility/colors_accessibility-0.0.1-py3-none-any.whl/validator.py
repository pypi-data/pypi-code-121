from dataclasses import dataclass
from typing import Union

from colors_accessibility.utils import check_if_values_are_positive, check_if_correct_hex_value, check_if_values_are_numeric, \
    check_if_correct_hsl_values
from colors_accessibility.utils.decorators import validate_parameters
from colors_accessibility.utils.errors import ExceededMaximumValueError, IncorrectColorSpaceError, IncorrectInputLengthError, \
    IncorrectHexLengthError
from colors_accessibility.utils.registry import Registry
from colors_accessibility.data.configuration_data import CONFIGURATION_DATA


@dataclass
class Validator:
    color_space_validators = Registry()

    @staticmethod
    @validate_parameters
    def validate_color_space(color_space: str) -> bool:
        if color_space.lower() not in CONFIGURATION_DATA.get('implemented'):
            raise IncorrectColorSpaceError(color_space, CONFIGURATION_DATA.get('implemented'))
        return True

    @staticmethod
    @validate_parameters
    def validate_input_length(color_space: str, values: Union[str, dict, list, tuple]) -> bool:
        if isinstance(values, str):
            values = [values]
        values_length = len(values)
        if values_length != CONFIGURATION_DATA.get('lengths').get(color_space):
            raise IncorrectInputLengthError(color_space, values_length)
        return True

    @staticmethod
    @color_space_validators.register('rgb')
    def validate_rgb_values(values: Union[list, tuple]) -> bool:
        if not values:
            raise IncorrectInputLengthError('rgb', 0)
        check_if_values_are_numeric(values)
        check_if_values_are_positive(values)
        exceeded_values = []
        for value in values:
            if value > CONFIGURATION_DATA.get('maximum_values').get('rgb'):
                exceeded_values.append(value)
        if exceeded_values:
            raise ExceededMaximumValueError(exceeded_values, CONFIGURATION_DATA.get('maximum_values').get('rgb'), 'rgb')
        return True

    @staticmethod
    @color_space_validators.register('hex')
    def validate_hex_values(values: Union[list, str]) -> bool:
        if type(values) == list:
            values = ''.join(values)
        value = values.replace('#', '')
        if len(value) not in [3, 6]:
            raise IncorrectHexLengthError(value)
        check_if_correct_hex_value(values)
        return True

    @staticmethod
    @color_space_validators.register('hsl')
    def validate_hsl_values(values: list) -> bool:
        check_if_correct_hsl_values(values)
        return True

    def validate_values(self, color_space: str, values: Union[list, tuple]) -> bool:
        self.validate_input_length(color_space, values)
        self.color_space_validators.functions.get(color_space)(values)
        return True

    def validate(self, color_space: str, values: Union[str, list, tuple]) -> bool:
        self.validate_color_space(color_space)
        self.validate_values(color_space, values)
        return True
