from functools import wraps
from colors_accessibility.utils import associate_input_args_with_expected_types
from typing import get_args, get_type_hints
from colors_accessibility.utils.errors import IncorrectArgumentsTypingError


def validate_parameters(function: callable):
    @wraps(function)
    def wrapper(*args, **kwargs):
        arguments_typing = get_type_hints(function)
        arguments_typing = {
            key: get_args(value) or [value]
            for key, value
            in arguments_typing.items()
        }
        args_typing = associate_input_args_with_expected_types(args, list(arguments_typing.keys()))
        input_typings = {**kwargs, **args_typing}
        incorrect_arguments_typing = {
            key: type(value)
            for key, value
            in input_typings.items()
            if key in arguments_typing and type(value) not in arguments_typing.get(key)
        }
        correct_arguments_typing = {
            key: (value[0] if type(value) == list else value)
            for key, value
            in arguments_typing.items()
            if key in incorrect_arguments_typing
        }
        if incorrect_arguments_typing:
            raise IncorrectArgumentsTypingError(correct_arguments_typing, incorrect_arguments_typing)
        return function(*args, **kwargs)
    return wrapper
