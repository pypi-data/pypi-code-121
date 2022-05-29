def convert_float_to_decimal(f=0.0, precision=2):
    """
    Convert a float to string of decimal.
    precision: by default 2.
    If no arg provided, return "0.00".

    Parameters
    ----------
    f : float
        The float to be converted.
    precision : int
        The number of decimal places.

    Returns
    -------
    str
        The converted string.

    Examples
    --------
    >>> convert_float_to_decimal(1.23456789, 2)
    '1.23'
    >>> convert_float_to_decimal(1.23456789, 3)
    '1.235'
    >>> convert_float_to_decimal(1.23456789, 4)
    '1.2346'
    """
    return ("%." + str(precision) + "f") % f


def format_file_size(size, sizeIn, sizeOut, precision=0):
    """
    Convert file size to a string representing its value in B, KB, MB and GB.
    The convention is based on sizeIn as original unit and sizeOut
    as final unit.

    Parameters
    ----------
    size : float
        The size to be converted.
    sizeIn : str
        The original unit of the size.
    sizeOut : str
        The final unit of the size.
    precision : int
        The number of decimal places.

    Returns
    -------
    str
        The converted string.

    Examples
    --------
    >>> format_file_size(1.23456789, "B", "B", 0)
    '1.23 B'
    >>> format_file_size(1.23456789, "B", "KB", 0)
    '1.23 KB'
    >>> format_file_size(1.23456789, "B", "MB", 0)
    '1.23 MB'
    """
    assert sizeIn.upper() in {"B", "KB", "MB", "GB"}, "sizeIn type error"
    assert sizeOut.upper() in {"B", "KB", "MB", "GB"}, "sizeOut type error"
    if sizeIn == "B":
        if sizeOut == "KB":
            return convert_float_to_decimal((size / 1024.0), precision)
        elif sizeOut == "MB":
            return convert_float_to_decimal((size / 1024.0 ** 2), precision)
        elif sizeOut == "GB":
            return convert_float_to_decimal((size / 1024.0 ** 3), precision)
    elif sizeIn == "KB":
        if sizeOut == "B":
            return convert_float_to_decimal((size * 1024.0), precision)
        elif sizeOut == "MB":
            return convert_float_to_decimal((size / 1024.0), precision)
        elif sizeOut == "GB":
            return convert_float_to_decimal((size / 1024.0 ** 2), precision)
    elif sizeIn == "MB":
        if sizeOut == "B":
            return convert_float_to_decimal((size * 1024.0 ** 2), precision)
        elif sizeOut == "KB":
            return convert_float_to_decimal((size * 1024.0), precision)
        elif sizeOut == "GB":
            return convert_float_to_decimal((size / 1024.0), precision)
    elif sizeIn == "GB":
        if sizeOut == "B":
            return convert_float_to_decimal((size * 1024.0 ** 3), precision)
        elif sizeOut == "KB":
            return convert_float_to_decimal((size * 1024.0 ** 2), precision)
        elif sizeOut == "MB":
            return convert_float_to_decimal((size * 1024.0), precision)
