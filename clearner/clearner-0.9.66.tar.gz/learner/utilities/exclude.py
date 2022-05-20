# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import functools

from learner.validator.input_validator import remove_subset_list


def exclude(name=None):
    """Accept a named argument and update that argument by deleting the items in the exclude_list and then run the
    function.

    :param name: a named argument in a function that will be decorated
    :return: a decorator function
    """
    def exclude_decorator(method):
        @functools.wraps(wrapped=method)
        def exclude_values(*args, **kwargs):
            try:
                kwargs[name] = remove_subset_list(kwargs[name], kwargs["exclude_list"])
            except KeyError:
                pass
            result = method(*args, **kwargs)
            return result
        return exclude_values
    return exclude_decorator
