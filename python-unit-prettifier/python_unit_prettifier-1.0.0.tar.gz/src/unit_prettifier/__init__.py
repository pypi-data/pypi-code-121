__author__ = """Aria Bagheri"""
__email__ = 'ariab9342@gmail.com'
__version__ = '1.0.0'

import math
from typing import Union


class UnitPrettifier:
    @staticmethod
    def prettify_bytes(value_bytes: Union[float, int], capital_units: bool = True,
                       short_form: bool = True) -> tuple[float, str]:
        short_form_units = ["b", "kb", "mb", "gb", "tb"]
        long_form_units = ["bytes", "kilobytes", "megabytes", "gigabytes", "terabytes"]

        index = min(math.floor(math.log(value_bytes, 1024)), 4)
        unit = short_form_units[index] if short_form else long_form_units[index]
        return value_bytes/(1024**index), unit.upper() if capital_units else unit

    @staticmethod
    def prettify_inch_ft(ft: Union[float, int], inch: Union[float, int]) -> str:
        return f"{ft}' {inch}\""

    @staticmethod
    def prettify_metric_weight(grams: Union[float, int], short_form: bool = True,
                               capital_units: bool = False) -> tuple[float, str]:
        short_form_units = ["pg", "ng", "µg", "mg", "g", "kg", "t", "Mt", "Gt"]
        long_form_units = ["picogram", "nanogram", "microgram", "milligram", "gram", "kilogram", "tonne", "megatonne",
                           "gigatonne"]

        index = min(4, max(-4, math.floor(math.log(grams, 1000))))
        unit = short_form_units[index + 4] if short_form else long_form_units[index + 4]
        return grams * 1000 ** index, unit.upper() if capital_units else unit

    @staticmethod
    def prettify_metric_length(m: Union[float, int], short_form: bool = True,
                               capital_units: bool = False) -> tuple[float, str]:
        short_form_units = ["mm", "cm", "dm", "m", "kam", "hm", "km"]
        long_form_units = ["milimeter", "centimeter", "decimeter", "meter", "dekameter", "hectometer", "kilometer"]

        index = min(3, max(-3, math.floor(math.log(m, 10))))
        unit = short_form_units[index + 3] if short_form else long_form_units[index + 3]

        return m / (10 ** index), unit.upper() if capital_units else unit

    @staticmethod
    def prettify_imperial_weight(ounces: Union[float, int], short_form: bool = True,
                                 use_uk_ton: bool = False) -> tuple[float, str]:
        short_form_units = ["oz", "lb", "ton (us)", "ton (uk)"]
        long_form_units = ["ounces", "pounds", "us ton(s)", "uk ton(s)"]

        pounds, ton_us, ton_uk = ounces / 16, ounces / 16 / 2000, ounces / 2240

        if ton_us > 1 or ton_uk > 1:
            return ton_uk if use_uk_ton else ton_us,\
                   (short_form_units if short_form else long_form_units)[2 + int(use_uk_ton)]
        if pounds > 1:
            return pounds, short_form_units[1] if short_form else long_form_units[1]
        return ounces, short_form_units[0] if short_form else long_form_units[0]

    @staticmethod
    def prettify_inches(inches: Union[float, int]) -> str:
        return f"{inches // 12}' {inches % 12}\""

    @staticmethod
    def inch_to_m(inches: Union[float, int]) -> float:
        return inches / 39.37

    @staticmethod
    def m_to_inch(m: Union[float, int]) -> float:
        return m * 39.37

    @staticmethod
    def inches_to_inch_ft(inches: Union[float, int]) -> tuple[int, float]:
        return inches // 12, inches % 12

    @staticmethod
    def kg_to_lb(kg: Union[float, int]) -> float:
        return 2.205 * kg

    @staticmethod
    def lb_to_kg(lb: Union[float, int]) -> float:
        return lb / 2.205

    @staticmethod
    def lb_to_oz(lb: Union[float, int]) -> float:
        return 16 * lb

    @staticmethod
    def oz_to_lb(oz: Union[float, int]):
        return oz / 16

    @staticmethod
    def kg_to_oz(kg: Union[float, int]) -> float:
        return UnitPrettifier.kg_to_lb(kg) * 16

    @staticmethod
    def oz_to_kg(oz: Union[float, int]) -> float:
        return UnitPrettifier.lb_to_kg(oz / 16)
