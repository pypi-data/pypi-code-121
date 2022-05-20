"""
Color Module. Contains a class for managing a Color.
"""

from typing import Tuple
from colorsys import hsv_to_rgb, rgb_to_hsv

CoordsTuple = tuple[int, int]
ColorsDict = dict[CoordsTuple, "Color"]
RGBTuple = Tuple[int, int, int]
HSVTuple = RGBTuple
RGBATuple = Tuple[int, int, int, int]

HEX_CHARS = "0123456789abcdefABCDEF"


class Color:
    """
    A color that can be represented in RGB, RGBA, HSV, etc...
    """

    @staticmethod
    def check_rgb(value: int) -> bool:
        """
        Checks if a RGB value is between 0 and 255.
        """

        return 0 <= value <= 255


    @staticmethod
    def check_percentage_value(value: int) -> bool:
        """
        Checks if an alpha/hsv value is between 0 and 100.
        """

        return 0 <= value <= 100


    @staticmethod
    def _check_hex_prefix(hex_str: str) -> bool:
        """
        Checks if a hexadecimal string starts with '#'.
        """

        return hex_str.startswith('#')


    @staticmethod
    def _check_hex_chars(hex_str: str) -> bool:
        """
        Checks if all characters of a string are
        valid hexadecimal characters.
        """

        for char in hex_str:
            if char not in HEX_CHARS:
                return False
        return True


    @staticmethod
    def _check_hex_format(hex_str: str, expected_len: int) -> bool:
        """
        Checks if the string is a correct hexadecimal number with
        the correct prefix and expected length.
        """

        if not len(hex_str) == expected_len or not Color._check_hex_prefix(hex_str):
            return False

        return Color._check_hex_chars(hex_str[1:])


    @staticmethod
    def check_hex_rgb(hex_rgb: str) -> bool:
        """
        Returns 'True' if hex if a string of the pattern
        '#rgb'.

        Otherwise, returns 'False'.
        """

        return Color._check_hex_format(hex_rgb, 4)


    @staticmethod
    def check_hex_rgba(hex_rgba: str) -> bool:
        """
        Returns 'True' if hex if a string of the pattern
        '#rgba'.

        Otherwise, returns 'False'.
        """

        return Color._check_hex_format(hex_rgba, 5)


    @staticmethod
    def check_hex_rrggbb(hex_rrggbb: str) -> bool:
        """
        Returns 'True' if hex if a string of the pattern
        '#rrggbb'.

        Otherwise, returns 'False'.
        """

        return Color._check_hex_format(hex_rrggbb, 7)


    @staticmethod
    def check_hex_rrggbbaa(hex_rrggbbaa: str) -> bool:
        """
        Returns 'True' if hex if a string of the pattern
        '#rrggbbaa'.

        Otherwise, returns 'False'.
        """

        return Color._check_hex_format(hex_rrggbbaa, 9)


    @staticmethod
    def dec_float_to_int(rgb_floats: tuple[float, float, float]) -> RGBTuple:
        """
        Converts a tuple of RGB values in float form to its integer variant.
        """

        return tuple(int(color * 255) for color in rgb_floats)


    @staticmethod
    def hex_to_dec(hex_n: str, count: int) -> Tuple[int, ...]:
        """
        Converts a hexadecimal string to a tuple of integrs.
        """

        dec = []
        length = len(hex_n) - 1 # One less because of the prefix.

        for i in range(0, length, count):

            hex_number = hex_n[1:][i:i+count]
            dec.append(int(hex_number, 16))

        return tuple(dec)


    @classmethod
    def from_hsv(cls, hue: int, saturation: int, value: int) -> "Color":
        """
        Creates the color from HSV properties.
        """

        if not Color.check_percentage_value(saturation):
            raise ValueError(f"Saturation is {saturation}. It should be between 0 and 100.")

        if not Color.check_percentage_value(value):
            raise ValueError(f"Saturation is {value}. It should be between 0 and 100.")

        hue %= 360 # hue is in degrees, and its values can be circular

        red, green, blue = Color.dec_float_to_int(hsv_to_rgb(hue / 360,
                                                             saturation / 100,
                                                             value / 100))

        return cls(red, green, blue)


    @classmethod
    # pylint: disable=unbalanced-tuple-unpacking
    def from_hex(cls, hex_value: str) -> "Color":
        """
        Creates the color from a string with the following formats
        """

        red, green, blue, alpha = 0, 0, 0, 100

        if Color.check_hex_rgb(hex_value):
            red, green, blue = Color.hex_to_dec(hex_value, 1)
        elif Color.check_hex_rgba(hex_value):
            red, green, blue, alpha = Color.hex_to_dec(hex_value, 1)
        elif Color.check_hex_rrggbb(hex_value):
            red, green, blue = Color.hex_to_dec(hex_value, 2)
        elif Color.check_hex_rrggbbaa(hex_value):
            red, green, blue, alpha = Color.hex_to_dec(hex_value, 2)
        else:
            raise ValueError(f"{hex_value} is not a valid hexadecimal value.")

        return cls(red, green, blue, alpha)


    def __init__(self, red: int, green: int, blue: int, alpha: int=100) -> None:
        """
        Initializes an instance of 'Color'.

        `red`, `green` and `blue` should be integers of values between 0 and 255.
        `alpha` should be an integer between 0 and 100.
        """

        for comp in (red, green, blue):
            if not Color.check_rgb(comp):
                raise ValueError(f"Component has value {comp}. It should be between 0 and 255.")

        if not Color.check_percentage_value(alpha):
            raise ValueError(f"Alpha component has value {alpha}. It should be between 0 and 100.")

        # RGBA
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

        # HSV
        hue, sat, val = rgb_to_hsv(self.red, self.green, self.blue)
        self.hue = hue * 360
        self.saturation = sat * 100
        self.value = val * 100


    @property
    def rgb(self) -> RGBTuple:
        """
        Returns the red, green and blue
        components of the color.
        """

        return self.red, self.green, self.blue


    @property
    def rgba(self) -> RGBATuple:
        """
        Returns the red, green, blue and alpha
        components of the color.
        """

        return self.red, self.green, self.blue, self.alpha


    @property
    def alpha_255(self) -> int:
        """
        Retunrs `self.alpha` as an integer between 0 and 255,
        rather than between 0 and 100.
        """

        return int((self.alpha / 100) *  255)


    @property
    def hsv(self) -> HSVTuple:
        """
        Returns the hue, saturation and value
        components of the color.
        """

        return self.hue, self.saturation, self.value


    @property
    def hex(self) -> str:
        """
        Converts the color to a #rrggbb format.
        """

        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"


    @property
    def hex_alpha(self) -> str:
        """
        Converts the color to a #rrggbbaa format.
        """

        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}{self.alpha_255:02x}"
