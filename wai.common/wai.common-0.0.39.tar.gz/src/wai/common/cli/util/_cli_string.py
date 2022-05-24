from shlex import quote, split

from .._typing import OptionsList, is_options_list


def to_cli_string(options_list: OptionsList) -> str:
    """
    Forms an options list into a single CLI string.

    :param options_list:    The options list.
    :return:                The CLI string.
    """
    # Make sure it is an options list
    if not is_options_list(options_list):
        raise ValueError(f"Expected options list, got: {options_list}")

    options_list = [option if '"' in option else option.replace("'", '"')
                    for option in options_list]

    return " ".join(quote(option) for option in options_list)


def from_cli_string(cli_string: str) -> OptionsList:
    """
    Splits a CLI string into an options list.

    :param cli_string:  The CLI string.
    :return:            The options list.
    """
    return split(cli_string)
