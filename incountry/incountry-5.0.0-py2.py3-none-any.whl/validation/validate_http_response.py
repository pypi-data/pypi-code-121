from functools import wraps
from pydantic import ValidationError

from .utils import get_formatted_validation_error
from ..exceptions import StorageServerResponseValidationException


def validate_http_response_wrapper(function, model, http_response, **kwargs):
    try:
        return model.validate(kwargs).dict()
    except ValidationError as e:
        errors_report = get_formatted_validation_error(e)
        error_text = f"HTTP Response validation failed during {function.__qualname__}():{errors_report}"
        raise StorageServerResponseValidationException(message=error_text, http_response=http_response) from None


def validate_http_response(model):
    def decorator(function):
        @wraps(function)
        def inner(*args, **kwargs):
            (content, http_response) = function(*args, **kwargs)
            validation_res = validate_http_response_wrapper(function, model, http_response, **{"body": content})
            return (validation_res["body"], http_response)

        return inner

    return decorator
