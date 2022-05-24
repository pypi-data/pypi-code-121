from typing import Callable, Dict, List, Union
from functools import wraps
from inspect import signature

from pydantic import BaseModel, ValidationError


from .utils import function_args_to_kwargs, get_formatted_validation_error, is_decorated_method
from ..exceptions import (
    InputValidationException,
    StorageException,
    StorageServerException,
    StorageCountryNotSupportedException,
)


def get_validated_data(function, model, validation_exception=InputValidationException, **kwargs):
    try:
        return model.validate(kwargs).dict(exclude_unset=True, by_alias=True)
    except ValidationError as e:
        errors_report = get_formatted_validation_error(e)
        error_text = "Validation failed during {}():{}".format(function.__qualname__, errors_report)
        raise validation_exception(error_text) from None


def format_extra_fields_error(extra_fields):
    return "".join(f" \n  {field_name} - extra fields not permitted" for field_name in extra_fields)


def get_validated_function_input_for_models(
    function: Callable,
    args: list,
    kwargs: dict,
    models: List[Union[BaseModel, Dict]],
    forbid_extra_non_model_attributes: bool = True,
):

    new_kwargs = dict(kwargs)
    function_args_to_kwargs(function, args, new_kwargs)

    if is_decorated_method(function, args):
        self_attribute_name = next(iter(signature(function).parameters.keys()))

        class_instance = args[0]
        model_fields_set = {self_attribute_name}
    else:
        class_instance = None
        model_fields_set = set()

    for model in models:
        if isinstance(model, dict):
            condition_function = model.get("condition", None)
            if condition_function and not condition_function(class_instance):
                continue

            res_model = model["model"]
            validation_exception = model.get("validation_exception", InputValidationException)
        else:
            res_model = model
            validation_exception = InputValidationException

        model_fields_set.update([field.alias for field in res_model.__fields__.values()])

        validated_data_dict = get_validated_data(
            function=function,
            model=res_model,
            validation_exception=validation_exception,
            **new_kwargs,
        )

        for key in new_kwargs:
            if key in validated_data_dict:
                new_kwargs[key] = validated_data_dict[key]

    if forbid_extra_non_model_attributes and not set(new_kwargs).issubset(model_fields_set):
        raise InputValidationException(
            f"Validation failed during {function.__qualname__}():"
            f"{format_extra_fields_error(new_kwargs.keys() - model_fields_set)}"
        )

    return new_kwargs


def validate_model(*models: List[Union[BaseModel, Dict]], forbid_extra_non_model_attributes: bool = True):
    def decorator(function):
        @wraps(function)
        def inner(*args, **kwargs):
            new_kwargs = get_validated_function_input_for_models(
                function, args, kwargs, models, forbid_extra_non_model_attributes
            )

            exception_context_str = f"during {function.__qualname__}()"

            try:
                return function(**new_kwargs)
            except StorageServerException as e:
                if isinstance(e, StorageCountryNotSupportedException):
                    raise StorageCountryNotSupportedException(
                        message=f"server exception {exception_context_str}", country=e.country
                    ) from e
                raise type(e)(
                    message=f"Server exception {exception_context_str}",
                    url=e.url,
                    status_code=e.status_code,
                    method=e.method,
                    scope=e.scope,
                    http_response=e.http_response,
                ) from e
            except StorageException:
                raise
            except Exception as e:
                raise StorageException(f"{e.__class__.__qualname__} {exception_context_str}") from e

        return inner

    return decorator
