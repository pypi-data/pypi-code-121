from functools import wraps

from .utils import is_decorated_method
from ..exceptions import StorageClientException


def validate_lambda(lambda_function, error_message):
    def decorator(function):
        @wraps(function)
        def inner(*args, **kwargs):
            if is_decorated_method(function, args):
                lambda_res = lambda_function(args[0])
            else:
                lambda_res = lambda_function()

            if not lambda_res:
                raise StorageClientException(f"Validation failed during {function.__qualname__}(): {error_message}")
            return function(*args, **kwargs)

        return inner

    return decorator
