from dataclasses import dataclass, field
from typing import Union

from colors_accessibility.utils import normalize_hsl_values, normalize_values, expand_values, convert_integer_to_hex, expand_hsl_values
from colors_accessibility.utils.classes import ColorRepresentation, ColorRepresentations
from colors_accessibility.utils.errors import TypeCastingError
from colors_accessibility.utils.registry import Registry
from colors_accessibility.validator import Validator
from colors_accessibility.data.configuration_data import CONFIGURATION_DATA


@dataclass
class Color:
    color_space: str
    color_values: Union[str, dict, list, tuple]
    implemented_color_spaces: list = field(default_factory=lambda: CONFIGURATION_DATA.get('implemented'))

    validator: Validator = Validator()

    conversion_registry: Registry = Registry()
    processing_registry: Registry = Registry()
    setter_registry: Registry = Registry()
    to_rgb_registry: Registry = Registry()
    to_hex_registry: Registry = Registry()
    to_hsl_registry: Registry = Registry()
    to_dict_registry: Registry = Registry()

    def __str__(self):
        return f"Color(color_space='{self.color_space}', color_values='{self.color_values}')"

    def __repr__(self):
        return f"Color(color_space='{self.color_space}', color_values='{self.color_values}')"

    def cast_to_type(self):
        types_mapping = {
            'rgb': float,
            'hsl': float
        }
        incorrect_values = []
        correct_values = []
        for value in self.color_values:
            try:
                correct_values.append(types_mapping.get(self.color_space)(value))
            except (TypeError, ValueError):
                incorrect_values.append(value)
        if incorrect_values:
            raise TypeCastingError(incorrect_values, str(types_mapping.get(self.color_space)))
        self.color_values = correct_values

    def format_hex(self):
        if type(self.color_values) == list:
            self.color_values = ''.join(self.color_values)
        color_value = self.color_values.replace('#', '')
        if len(color_value) == 3:
            self.color_values = f"#{''.join([character * 2 for character in self.color_values[1:]])}"

    @processing_registry.register('rgb')
    def process_rgb(self):
        self.cast_to_type()
        self.validator.validate('rgb', self.color_values)
        self.color_values = normalize_values(self.color_values, 255)

    @processing_registry.register('hex')
    def process_hex(self):
        self.validator.validate('hex', self.color_values)
        self.format_hex()

    @processing_registry.register('hsl')
    def process_hsl(self):
        self.cast_to_type()
        self.color_values = normalize_hsl_values(self.color_values)
        self.validator.validate('hsl', self.color_values)
        if 0 < self.color_values[0] < 1:
            self.color_values[0] = int(self.color_values[0] * 360)

    def process(self, color_space: str):
        if type(self.color_values) == dict:
            self.color_values = list(self.color_values.values())
        self.processing_registry.functions.get(color_space)(self)

    def __post_init__(self):
        self.original_values = self.color_values
        self.original_color_space = self.color_space
        self.color_space = self.color_space.lower()
        self.process(self.color_space)

    def process_hsl_values(self, number: int) -> float:
        k = (number + self.color_values[0] / 30) % 12
        a = self.color_values[1] * min([self.color_values[2], 1 - self.color_values[2]])
        return self.color_values[2] - a * max([-1, min([k - 3, 9 - k, 1])])

    @to_hex_registry.register('rgb')
    def rgb_to_hex(self):
        color_values = expand_values(self.color_values)
        hex_representation = '#'
        for value in color_values:
            value = convert_integer_to_hex(int(value))
            hex_representation += value
        return hex_representation

    @to_hex_registry.register('hsl')
    def hsl_to_hex(self):
        original_values = self.color_values
        rgb_representation = self.hsl_to_rgb()
        self.color_values = rgb_representation
        hex_representation = self.rgb_to_hex()
        self.color_values = original_values
        return hex_representation

    @to_rgb_registry.register('hex')
    def hex_to_rgb(self):
        hex_value = self.color_values.replace('#', '')
        return [
            int(hex_value[index: index + 2], 16)
            for index
            in range(0, len(hex_value), 2)
        ]

    @to_rgb_registry.register('hsl')
    def hsl_to_rgb(self) -> list:
        rgb_representation = [
            round(self.process_hsl_values(0) * 255),
            round(self.process_hsl_values(8) * 255),
            round(self.process_hsl_values(4) * 255)
        ]
        return rgb_representation

    @to_hsl_registry.register('rgb')
    def rgb_to_hsl(self, rounding_factor: int = 2) -> list:
        red_value, green_value, blue_value = expand_values(self.color_values)
        red_value /= 255
        green_value /= 255
        blue_value /= 255
        max_value = max(red_value, green_value, blue_value)
        min_value = min(red_value, green_value, blue_value)
        lightness = (max_value + min_value) / 2
        if max_value == min_value:
            saturation = 0
            hue = 0
        else:
            saturation = lightness < 0.5 and (max_value - min_value) / (max_value + min_value) or (
                    max_value - min_value) / (2 - max_value - min_value)
            if red_value == max_value:
                hue = (green_value - blue_value) / (max_value - min_value)
            elif green_value == max_value:
                hue = 2 + (blue_value - red_value) / (max_value - min_value)
            else:
                hue = 4 + (red_value - green_value) / (max_value - min_value)
        hue *= 60
        if hue < 0:
            hue += 360
        return [round(hue, 0), round(saturation, rounding_factor), round(lightness, rounding_factor)]

    @to_hsl_registry.register('hex')
    def hex_to_hsl(self) -> list:
        original_values = self.color_values
        rgb_representation = self.hex_to_rgb()
        self.color_values = rgb_representation
        hsl_representation = self.rgb_to_hsl()
        self.color_values = original_values
        return hsl_representation

    @conversion_registry.register('hex')
    def to_hex(self):
        if self.color_space == 'hex':
            return self.color_values
        return self.to_hex_registry.functions.get(self.color_space)(self)

    @conversion_registry.register('rgb')
    def to_rgb(self):
        if self.color_space == 'rgb':
            return self.color_values
        return normalize_values(self.to_rgb_registry.functions.get(self.color_space)(self), 255)

    @conversion_registry.register('hsl')
    def to_hsl(self):
        if self.color_space == 'hsl':
            return self.color_values
        return self.to_hsl_registry.functions.get(self.color_space)(self)

    @setter_registry.register('rgb')
    def set_to_rgb(self):
        self.color_values = self.to_rgb()
        self.color_space = 'rgb'

    @setter_registry.register('hex')
    def set_to_hex(self):
        self.color_values = self.to_hex()
        self.color_space = 'hex'

    @setter_registry.register('hsl')
    def set_to_hsl(self):
        self.color_values = self.to_hsl()
        self.color_space = 'hsl'

    def set_to(self, color_space: str):
        color_space = color_space.lower()
        self.validator.validate_color_space(color_space)
        self.setter_registry.functions.get(color_space)(self)

    def calculate_relative_luminance(self, new_estimated_threshold: bool = False) -> float:
        rgb_representation = self.color_values if self.color_space == 'rgb' else self.to_rgb()
        rgb_representation = normalize_values(rgb_representation, 255)
        threshold = 0.03928 if not new_estimated_threshold else 0.04045
        calculated_color_weights = [
            color_value / 12.92
            if color_value <= threshold
            else ((color_value + 0.055) / 1.055) ** 2.4
            for color_value
            in rgb_representation
        ]
        relative_luminance = 0.2126 * calculated_color_weights[0] \
                             + 0.7152 * calculated_color_weights[1] \
                             + 0.0722 * calculated_color_weights[2]
        return relative_luminance

    def convert(self, color_space: str):
        color_values = getattr(self, f'to_{color_space}')()
        self.color_values = color_values
        self.color_space = color_space

    @to_dict_registry.register('rgb')
    def rgb_to_dict(self):
        return {
            'red': self.color_values[0],
            'green': self.color_values[1],
            'blue': self.color_values[2]
        }

    @to_dict_registry.register('hex')
    def hex_to_dict(self):
        return {
            'hex': self.color_values
        }

    @to_dict_registry.register('hsl')
    def hsl_to_dict(self):
        return {
            'hue': self.color_values[0],
            'saturation': self.color_values[1],
            'lightness': self.color_values[2]
        }

    def to_dict(self):
        return self.to_dict_registry.functions.get(self.color_space)(self)

    def get_representations(self, color_space: str = None):
        original_color_space = self.color_space
        original_color_values = self.color_values
        color_representations = {}
        if not color_space:
            color_space = self.color_space
        if color_space in ['rgb', 'all']:
            self.convert('rgb')
            normalized = self.color_values if original_color_space != 'rgb' else original_color_values
            extended = expand_values(normalized)
            dictionary = self.to_dict()
            color_representations['rgb'] = ColorRepresentation(normalized, extended, dictionary)
        if color_space in ['hex', 'all']:
            self.convert('hex')
            normalized = self.color_values if original_color_space != 'hex' else original_color_values
            extended = normalized
            dictionary = self.to_dict()
            color_representations['hex'] = ColorRepresentation(normalized, extended, dictionary)
        if color_space in ['hsl', 'all']:
            self.convert('hsl')
            normalized = self.color_values if original_color_space != 'hsl' else original_color_values
            extended = expand_hsl_values(normalized)
            dictionary = self.to_dict()
            color_representations['hsl'] = ColorRepresentation(normalized, extended, dictionary)
        return ColorRepresentations(**color_representations)
