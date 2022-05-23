from typing import Iterable, Union

from .._typing import OptionsList


def get_options_sub_list(options_list: OptionsList, options: Iterable[str]) -> OptionsList:
    """
    Gets the part of the options list which corresponds to
    the given option/s.

    :param options_list:    The original options list.
    :param options:         The options to extract.
    :return:                The sub-list of options.
    """
    # Get the set of option names
    option_names = set(options)

    # Convert option names to option references
    options = list(getattr(type(self), option) for option in option_names)

    # Convert references to option strings
    option_strings = set(option.option_string for option in options)

    # Get the slices of the options list corresponding to the option
    options_sub_list = []
    slice_started: bool = False
    for string in self._options_list:
        # See if we are in a valid slice
        if string.startswith("--"):
            slice_started = string in option_strings

        # Add the string to the sub-list if it's part of a valid slice
        if slice_started:
            options_sub_list.append(string)

    return options_sub_list
