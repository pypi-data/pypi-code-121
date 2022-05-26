def isnumber(value):
    """Check if the target value is a number.

    Args:
        value ():  The input under test

    Returns:
        (bool): True if the target is a number. False otherwise.
    """

    # Note boolean can be converted to number so it has to be avoided
    if isinstance(value, bool):
        return False

    try:
        float(value)
        return True
    except ValueError:
        return False
