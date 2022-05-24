from functools import wraps
from typing import Type

from ..meta import all_as_kwargs
from ..meta.typing import GenericDecorator, GenericCallable


def ensure_error_type(error_type: Type[Exception],
                      format_message: str = "Unhandled exception of type {0.__class__.__name__}: "
                                            "{0}") -> GenericDecorator:
    """
    Decorator which ensures any exceptions coming from the called function
    are of the given error-type. Any exceptions that the function raises
    that are already of the correct type (or a sub-type) are passed through
    normally, any other errors are chained with an error of the given type.

    :param error_type:      The type of error to ensure.
    :param format_message:  The message to format if an exception of another type occurs.
                            Can include format strings involving any arguments passed to
                            the function (by name only), and the positional argument 0
                            which is the exception that occurred.
    :return:                The decorator function.
    """
    def decorator(function: GenericCallable) -> GenericCallable:
        @wraps(function)
        def with_ensured_error_type(*args, **kwargs):
            try:
                # Call the function
                return function(*args, **kwargs)
            except error_type:
                # Re-raise any exception of the requested error-type
                raise
            except Exception as e:
                # Wrap any other exception in the requested error-type
                all_kwargs = all_as_kwargs(function, *args, **kwargs)
                raise error_type(format_message.format(e, **all_kwargs)) from e

        return with_ensured_error_type

    return decorator
