""" Objects operations file """
import datetime


def convert_to_string(input_value):
    """
    :param input_value:
    :return:
    """
    return input_value.__str__()


def datetime2str(value: datetime.datetime):
    """
    :param value:
        datetime instance object.
    :return:
        str with the conversion
    """
    if not isinstance(value, datetime.datetime):
        raise TypeError("Value is not datetime.")

    return value.__str__()
