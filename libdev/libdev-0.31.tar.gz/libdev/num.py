"""
Numbers functionality
"""

def is_float(value: str) -> bool:
    """ Check value for float """

    try:
        float(value)
    except (ValueError, TypeError):
        return False

    return True

def to_num(value: str) -> bool:
    """ Convert value to int or float """

    if isinstance(value, str):
        value = float(value)

    if not value % 1:
        value = int(value)

    return value
