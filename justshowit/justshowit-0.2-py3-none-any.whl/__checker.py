import re

def is_valid_url(url:str) -> bool:
    """
    Attempt to check if `url` is valid.
    This function is taken more or less directly from the wonderful validators libary - https://github.com/kvesteri/validators.
    All credit goes to them.
    """

    ip_middle_octet = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
    ip_last_octet = r"(?:\.(?:0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5]))"
    regex = re.compile(
        r"^"
        r"(?:(?:https?|ftp)://)"
        r"(?:[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:]+"
        r"(?::[-a-z0-9._~%!$&'()*+,;=:]*)?@)?"
        r"(?:"
        r"(?P<private_ip>"
        r"(?:(?:10|127)" + ip_middle_octet + r"{2}" + ip_last_octet + r")|"
        r"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + r")|"
        r"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + r"))"
        r"|"
        r"(?P<private_host>"
        r"(?:localhost))"
        r"|"
        r"(?P<public_ip>"
        r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        r"" + ip_middle_octet + r"{2}"
        r"" + ip_last_octet + r")"
        r"|"
        r"\[("
        r"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"
        r"([0-9a-fA-F]{1,4}:){1,7}:|"
        r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
        r"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"
        r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"
        r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"
        r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"
        r"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"
        r":((:[0-9a-fA-F]{1,4}){1,7}|:)|"
        r"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"
        r"::(ffff(:0{1,4}){0,1}:){0,1}"
        r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
        r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"
        r"([0-9a-fA-F]{1,4}:){1,4}:"
        r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
        r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
        r")\]|"
        r"(?:(?:(?:xn--)|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*"
        r"[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]+)"
        r"(?:\.(?:(?:xn--)|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*"
        r"[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]+)*"
        r"(?:\.(?:(?:xn--[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]{2,})|"
        r"[a-z\u00a1-\uffff\U00010000-\U0010ffff]{2,}))"
        r")"
        r"(?::\d{2,5})?"
        r"(?:/[-a-z\u00a1-\uffff\U00010000-\U0010ffff0-9._~%!$&'()*+,;=:@/]*)?"
        r"(?:\?\S*)?"
        r"(?:#\S*)?"
        r"$",
        re.UNICODE | re.IGNORECASE
    )
    pattern = re.compile(regex)
    result = pattern.match(url)
    return result is not None


def in_jupyter():
    """
    Check if python is currently running in a jupyter enviroment.
    NOTE: This code is somewhat dubious, but I have tested it to the best of my abilities.
          But, please let me know if you have a more robust solution
    """

    try:
        shell = get_ipython().__class__.__name__ # This is supposed to be an unresolved reference anywhere outside jupyter
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?), going to assume that we are not in jupyter
    except NameError:
        return False  # Probably standard Python interpreter


def assert_type(to_check, expected_type, allow_none:bool=False):
    """
    Check object against expected type

    @param to_check: Object for type check
    @param expected_type: Expected type of `to_check`
    @param allow_none: Weather or not None is an accepted type or not
    """

    if not isinstance(allow_none, bool):
        raise ValueError(f"Expected `allow_None` to by of type bool, but received type `{type(allow_none)}`")
    if (to_check is None) and (expected_type is None):
        raise TypeError(f"`None` is not a valid type. If you're trying to check if `type(to_check) == None` try set"
                        f" `expected_type=type(None)` instead.")

    is_ok = isinstance(to_check, expected_type)
    if allow_none:
        is_ok = (to_check is None) or is_ok

    if not is_ok:
        raise TypeError(f"Expected type `{expected_type}`, but received type `{type(to_check)}`")


def assert_types(to_check:list, expected_types:list, allow_nones:list=None):
    """
    Check list of values against expected types

    @param to_check: List of values for type check
    @param expected_types: Expected types of `to_check`
    @param allow_nones: list of booleans or 0/1
    """

    # Checks
    assert_type(to_check, list)
    assert_type(expected_types, list)
    assert_type(allow_nones, list, allow_none=True)
    if len(to_check) != len(expected_types):
        raise ValueError("length mismatch between `to_check_values` and `expected_types`")

    # If `allow_nones` is None all values are set to False.
    if allow_nones is None:
        allow_nones = [False for _ in range(len(to_check))]
    else:
        if len(allow_nones) != len(to_check):
            raise ValueError("length mismatch between `to_check_values` and `allow_nones`")
        for i, element in enumerate(allow_nones):
            if element in [0, 1]:
                allow_nones[i] = element == 1 # the `== 1` is just to allow for zeros as False and ones as True

    # check if all elements are of the correct type
    for i, value in enumerate(to_check):
        assert_type(value, expected_types[i], allow_nones[i])


def assert_in(to_check, check_in):
    """
    Check if the value `to_check` is present in `check_in`

    @param to_check: Value to be checked
    @param check_in: Values `to_check` is being checked against
    """
    try:
        is_in = to_check in check_in
    except Exception:
        raise RuntimeError(f"Failed to execute `to_check in check_in`")

    if not is_in:
        raise ValueError(f"Expected `{to_check}` to be in `{check_in}`, but it wasn't")