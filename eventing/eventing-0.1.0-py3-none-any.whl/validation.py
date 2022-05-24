from functools import wraps
from inspect import signature
from typing import Any, Callable


def validate_arguments(*validators: Callable[..., None]):
    """Decorator to run argument validators before running function.

    Inspects the signature of the decorated function which when called will
    run all validators with the argument(s) they request to validate. The
    validators will be passed with only the arguments with the same name.
    These are expected to raise if argument is invalid or return.

    Args:
        *validators: Functions with non-positional-only arguments with the name
            as the arguments they intend to validate. These, and only these,
            will be passed to it to either raise an exception or do nothing.
    """

    def inner(f):
        sig = signature(f)
        validator_arg_names_pairs = (
            (v, signature(v).parameters.keys()) for v in validators
        )

        @wraps(f)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)

            for validator, arg_names in validator_arg_names_pairs:
                v_kwargs = {
                    arg_name: bound_args.arguments[arg_name]
                    for arg_name in arg_names
                }
                validator(**v_kwargs)
            return f(*args, **kwargs)

        return wrapper

    return inner


def event_name_validator(event_name: Any) -> None:
    if not isinstance(event_name, str):
        raise TypeError("event name must be a string")
    if event_name == "":
        raise ValueError("event name must not be empty")
    return None
