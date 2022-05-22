"""
Module include some string's easy-to-use methods
"""


def string_padding(string, length, symbol):
    """
    This method will return new string with gaping
    :param string: The original string
    :param length: total new string length
    :param symbol: The char to gaping with

    return: str -> '<symbol * gaping/2> string <symbol * gaping/2>'
    """
    new_str = string.center(len(string) + 2, ' ').center(length, symbol)
    return new_str


def pad_with_stars(string, length=100):
    """
    Method is wrapping string_padding method and create centric new string with stars
    """
    return string_padding(string, length, '*')


def pad_with_minus(string, length=100):
    """
    Method is wrapping string_padding method and create centric new string with minuses
    """
    return string_padding(string, length, '-')


# todo -> implement with padding on just one side - > not center str.ljust()


