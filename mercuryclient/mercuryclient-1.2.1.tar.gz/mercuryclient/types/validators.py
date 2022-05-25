def normalize_str(value: str) -> str:
    """
    Method to normalize strings. Raises value error if after stripping and removing
    newlines, string is empty

    :param value: String
    :type value: str
    :return: Normalized string
    :rtype: str
    """
    # Remove leading and trailing spaces
    value = value.strip()
    # Remove newlines
    value = "".join(value.splitlines())

    if not value:
        raise ValueError("string cannot be empty")

    return value
