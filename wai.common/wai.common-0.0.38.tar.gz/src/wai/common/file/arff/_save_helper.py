from . import constants


def quoted(string: str) -> str:
    """
    Quotes a string if it contains spaces.

    :param string:  The string to optionally quote.
    :return:        The (possibly quoted) string.
    """
    return '"' + string + '"' if "'" in string else \
        "'" + string + "'" if '"' in string else \
        '"' + string + '"' if ' ' in string or \
                              string == constants.MISSING_VALUE_SYMBOL or \
                              constants.COMMENT_SYMBOL in string else \
        string
