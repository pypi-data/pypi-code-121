from inspect import getfullargspec, ismethod
from typing import Callable


def function_args_to_kwargs(function, args, kwargs):
    func_args = getfullargspec(function)[0]
    kwargs.update(dict(zip(func_args, args)))


def format_loc_path_index(index):
    return f"[{index}]" if isinstance(index, int) else f"['{index}']"


def format_loc(error_loc_data):
    error_loc_data = [loc_data for loc_data in error_loc_data if loc_data != "__root__"]

    if len(error_loc_data) == 0:
        return ""

    loc_data_start, *rest_loc_data = error_loc_data

    return "{loc_data_start}{loc_data_tail} - ".format(
        loc_data_start=loc_data_start, loc_data_tail="".join(format_loc_path_index(idx) for idx in rest_loc_data)
    )


def get_formatted_validation_error(e, prefix=""):
    return "".join(f"\n {prefix}{format_loc(error['loc'])}{error['msg']}" for error in e.errors())


def is_decorated_method(function: Callable, args: list):
    return len(args) and args[0] and ismethod(getattr(args[0], function.__name__, None))
