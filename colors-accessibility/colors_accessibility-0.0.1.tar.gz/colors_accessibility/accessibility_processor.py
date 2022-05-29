from dataclasses import dataclass

from .color import Color
from .utils import update_non_empty_values
from .data.configuration_data import CONFIGURATION_DATA


@dataclass
class AccessibilityProcessor:
    foreground_color: Color
    background_color: Color

    def __post_init__(
            self
    ):
        self.foreground_color.color_values = self.foreground_color.to_rgb()
        self.foreground_color.color_space = 'rgb'
        self.background_color.color_values = self.background_color.to_rgb()
        self.background_color.color_space = 'rgb'

    @staticmethod
    def get_luminance_values(
            foreground_color: Color,
            background_color: Color
    ) -> tuple:
        return foreground_color.calculate_relative_luminance(), background_color.calculate_relative_luminance()

    @staticmethod
    def calculate_contrast(
            foreground_luminance: float,
            background_luminance: float
    ) -> float:
        maximum_color_relative_luminance = max(foreground_luminance, background_luminance)
        minimum_color_relative_luminance = min(foreground_luminance, background_luminance)
        color_contrast = (maximum_color_relative_luminance + 0.05) / (minimum_color_relative_luminance + 0.05)
        return color_contrast

    def calculate(
            self
    ):
        foreground_luminance, background_luminance = self.get_luminance_values(self.foreground_color,
                                                                               self.background_color)
        contrast = self.calculate_contrast(foreground_luminance, background_luminance)
        return contrast

    def get_parameter_signature(
            self,
            parameter: str,
            color_to_change: str,
            value: float = 0.01
    ) -> int:
        value *= 5
        original_contrast = self.calculate_contrast(self.foreground_color.calculate_relative_luminance(),
                                                    self.background_color.calculate_relative_luminance())
        parameter_index = 1 if parameter == 'saturation' else 2
        color_to_change_values = self.foreground_color.to_hsl() \
            if color_to_change == 'foreground' \
            else self.background_color.to_hsl()
        color_to_change_values[parameter_index] += value
        color_to_change_values[parameter_index] = max(0, min(color_to_change_values[parameter_index], 1))
        changed_color = Color('hsl', color_to_change_values)
        if color_to_change == 'foreground':
            contrast = self.calculate_contrast(changed_color.calculate_relative_luminance(),
                                               self.background_color.calculate_relative_luminance())
        else:
            contrast = self.calculate_contrast(self.foreground_color.calculate_relative_luminance(),
                                               changed_color.calculate_relative_luminance())
        return 1 if contrast >= original_contrast else -1

    def get_parameters_signatures(
            self,
            parameter: str,
            color_to_change: str,
            value: float = 0.01
    ) -> dict:
        parameters_signatures = {}
        if parameter == 'saturation' or 'both':
            saturation_signature = self.get_parameter_signature('saturation', color_to_change, value)
            parameters_signatures.update({
                1: saturation_signature
            })
        if parameter == 'lightness' or 'both':
            lightness_signature = self.get_parameter_signature('lightness', color_to_change, value)
            parameters_signatures.update({
                2: lightness_signature
            })
        return parameters_signatures

    @staticmethod
    def increment_color_hsl_values(
            color: Color,
            parameter: str,
            parameters_signatures: dict,
            value: float = 0.01
    ) -> Color:
        hsl_values = color.to_hsl()
        indexes_to_update = []
        if parameter in ['saturation', 'both']:
            indexes_to_update.append(1)
        if parameter in ['lightness', 'both']:
            indexes_to_update.append(2)
        for index in indexes_to_update:
            value *= parameters_signatures.get(index)
            if index == 1 and (CONFIGURATION_DATA.get('hsl_check_values_ranges').get('saturation').get('max')
                               <= hsl_values[index] or hsl_values[index]
                               <= CONFIGURATION_DATA.get('hsl_check_values_ranges').get('saturation').get('min')):
                value = 0
            if index == 2 and (CONFIGURATION_DATA.get('hsl_check_values_ranges').get('lightness').get('max')
                               <= hsl_values[index] or hsl_values[index]
                               <= CONFIGURATION_DATA.get('hsl_check_values_ranges').get('lightness').get('min')):
                value = 0
            hsl_values[index] += value
        return Color('hsl', hsl_values)

    @staticmethod
    def update_wcag_requirements(
            contrast: float,
            foreground_color_values: list = None,
            background_color_values: list = None
    ) -> dict:
        if foreground_color_values:
            foreground_color_values = [round(value, 2) for value in foreground_color_values]
        if background_color_values:
            background_color_values = [round(value, 2) for value in background_color_values]
        values = [color_values for color_values in [foreground_color_values, background_color_values] if color_values]
        wcag_requirements_fulfilled = {}
        if contrast >= 3:
            wcag_requirements_fulfilled.update({
                'large_aa': values
            })
        if contrast >= 4.5:
            wcag_requirements_fulfilled.update({
                'normal_aa': values
            })
            wcag_requirements_fulfilled.update({
                'large_aaa': values
            })
        if contrast >= 7:
            wcag_requirements_fulfilled.update({
                'normal_aaa': values
            })
        return wcag_requirements_fulfilled

    @staticmethod
    def check_borders_reached(
            color: Color,
            borders_reached: dict
    ) -> dict:
        hsl_color_values = color.to_hsl()
        if CONFIGURATION_DATA.get('hsl_check_values_ranges').get('saturation').get('max') <= hsl_color_values[1] \
                or hsl_color_values[1] <= CONFIGURATION_DATA.get('hsl_check_values_ranges').get('saturation').get(
                'min'):
            borders_reached.update({
                'saturation': True
            })
        if CONFIGURATION_DATA.get('hsl_check_values_ranges').get('lightness').get('max') <= hsl_color_values[2] \
                or hsl_color_values[2] <= CONFIGURATION_DATA.get('hsl_check_values_ranges').get('lightness').get('min'):
            borders_reached.update({
                'lightness': True
            })
        return borders_reached

    @staticmethod
    def check_borders_reached_for_both(
            color: Color,
            color_type: str,
            borders_reached: dict
    ) -> dict:
        hsl_color_values = color.to_hsl()
        if CONFIGURATION_DATA.get('hsl_check_values_ranges').get('saturation').get('max') <= hsl_color_values[1] \
                or hsl_color_values[1] <= CONFIGURATION_DATA.get('hsl_check_values_ranges').get('saturation').get(
                'min'):
            color_key = 'saturation_foreground' if color_type == 'foreground' else 'saturation_background'
            borders_reached.update({
                color_key: True
            })
        if CONFIGURATION_DATA.get('hsl_check_values_ranges').get('lightness').get('max') <= hsl_color_values[2] \
                or hsl_color_values[2] <= CONFIGURATION_DATA.get('hsl_check_values_ranges').get('lightness').get('min'):
            color_key = 'lightness_foreground' if color_type == 'foreground' else 'lightness_background'
            borders_reached.update({
                color_key: True
            })
        return borders_reached

    def update_wcag_colors_for_single_color(
            self,
            changed_color: Color,
            constant_color: Color,
            wcag_colors: dict
    ) -> dict:
        contrast = self.calculate_contrast(
            changed_color.calculate_relative_luminance(),
            constant_color.calculate_relative_luminance()
        )
        fulfilled_requirements = self.update_wcag_requirements(contrast, changed_color.to_hsl())
        wcag_compliant_colors = update_non_empty_values(wcag_colors, fulfilled_requirements)
        return wcag_compliant_colors

    def update_wcag_colors_for_both_colors(
            self,
            foreground_color: Color,
            background_color: Color,
            wcag_colors: dict
    ) -> dict:
        contrast = self.calculate_contrast(
            foreground_color.calculate_relative_luminance(),
            background_color.calculate_relative_luminance()
        )
        fulfilled_requirements = self.update_wcag_requirements(
            contrast, foreground_color.to_hsl(), background_color.to_hsl())
        wcag_compliant_colors = update_non_empty_values(wcag_colors, fulfilled_requirements)
        return wcag_compliant_colors

    def find_wcag_compliant_single_color_change(
            self,
            color_to_change: str,
            parameter: str,
            value: float = 0.01
    ) -> dict:
        wcag_compliant_colors = {}
        borders_reached = {
            'saturation': True if parameter == 'lightness' else False,
            'lightness': True if parameter == 'saturation' else False
        }
        parameters_signatures = self.get_parameters_signatures(parameter, color_to_change, value)
        background_color = Color(self.background_color.original_color_space, self.background_color.original_values)
        background_color.set_to_hsl()
        changed_color = self.foreground_color \
            if color_to_change == 'foreground' \
            else background_color
        constant_color = background_color \
            if color_to_change == 'foreground' \
            else self.foreground_color
        wcag_compliant_colors = self.update_wcag_colors_for_single_color(
            changed_color, constant_color, wcag_compliant_colors
        )
        while True:
            changed_color = self.increment_color_hsl_values(changed_color, parameter, parameters_signatures)
            borders_reached = self.check_borders_reached(changed_color, borders_reached)
            if borders_reached.get('saturation') and borders_reached.get('lightness'):
                break
            wcag_compliant_colors = self.update_wcag_colors_for_single_color(
                changed_color, constant_color, wcag_compliant_colors
            )
        return wcag_compliant_colors

    def find_wcag_compliant_both_colors_changes(
            self,
            parameter: str,
            value: float = 0.01
    ) -> dict:
        wcag_compliant_colors = {}
        borders_reached = {
            'saturation_foreground': True if parameter == 'lightness' else False,
            'lightness_foreground': True if parameter == 'saturation' else False,
            'saturation_background': True if parameter == 'lightness' else False,
            'lightness_background': True if parameter == 'saturation' else False
        }
        # Get parameter signatures
        foreground_parameters_signatures = self.get_parameters_signatures(parameter, 'foreground', value)
        background_parameters_signatures = {key: -1 * value for key, value in foreground_parameters_signatures.items()}
        # Set foreground and background colors
        changed_foreground_color = self.foreground_color
        changed_background_color = Color(self.background_color.original_color_space,
                                         self.background_color.original_values)
        changed_background_color.set_to_hsl()
        # Check if original colors are already compliant, if so add them to the dictionary
        wcag_compliant_colors = self.update_wcag_colors_for_both_colors(
            changed_foreground_color, changed_background_color, wcag_compliant_colors)
        # Run while loop until color pair is compliant, break it once both colors parameters reach their bounds and
        # return the dictionary with found color pairs
        while True:
            changed_foreground_color = self.increment_color_hsl_values(
                changed_foreground_color, parameter, foreground_parameters_signatures)
            changed_background_color = self.increment_color_hsl_values(
                changed_background_color, parameter, background_parameters_signatures)
            borders_reached = self.check_borders_reached_for_both(
                changed_foreground_color, 'foreground', borders_reached)
            borders_reached = self.check_borders_reached_for_both(
                changed_background_color, 'background', borders_reached)
            if borders_reached.get('saturation_foreground') and borders_reached.get('lightness_foreground') \
                    and borders_reached.get('saturation_background') and borders_reached.get('lightness_background'):
                break
            wcag_compliant_colors = self.update_wcag_colors_for_both_colors(
                changed_foreground_color, changed_background_color, wcag_compliant_colors)
        return wcag_compliant_colors

    def get_representation_single_color(self, color_to_change: str, parameter: str, value: float = 0.01) -> dict:
        colors_data = self.find_wcag_compliant_single_color_change(color_to_change, parameter, value)
        if not colors_data:
            return {}
        representation = {
            key: [
                Color('hsl', values)
                for values
                in values_list
            ]
            for key, values_list
            in colors_data.items()
        }
        return representation

    def get_representation_multiple_color(self, parameter: str, value: float = 0.01) -> dict:
        colors_data = self.find_wcag_compliant_both_colors_changes(parameter, value)
        representation = {
            key: [
                Color('hsl', values)
                for values
                in values_list
            ]
            for key, values_list
            in colors_data.items()
        }
        return representation

    def get_all_wcag_compliant_color(self, value: float = 0.01) -> dict:
        wcag_compliant_colors = {
            'saturation': {
                'foreground': None,
                'background': None,
            },
            'lightness': {
                'foreground': None,
                'background': None,
            }
        }
        for parameter in ['saturation', 'lightness']:
            wcag_compliant_colors[parameter]['foreground'] = self.get_representation_single_color(
                'foreground', parameter, value
            )
            wcag_compliant_colors[parameter]['background'] = self.get_representation_single_color(
                'background', parameter, value
            )
            wcag_compliant_colors[parameter]['both'] = self.get_representation_multiple_color(
                parameter, value
            )
        return wcag_compliant_colors
