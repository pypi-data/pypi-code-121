from functools import wraps

from .exceptions import ResultNotAccessibleException


class Result:
    def __init__(self, **kwargs):
        self.result = kwargs


class ResultWrapper:
    @classmethod
    def make_failed(cls, error_information=None):
        return cls(True, error_information)

    @classmethod
    def make_succeeded(cls, **kwargs):
        return cls(False, None, **kwargs)

    def __init__(self, failed, error_information, **kwargs):
        self.failed = failed
        self.error_information = error_information
        self._result = kwargs

    def __getattr__(self, item):
        if self.failed:
            raise ResultNotAccessibleException("Call failed. You cannot access results. Access 'error_information' for additional error data")
        if item in self._result.keys():
            return self._result.get(item)
        raise AttributeError("Item not found")


def wrap_result(exceptions=None):
    if exceptions is None:
        exceptions = tuple()
    if not isinstance(exceptions, tuple):
        raise TypeError(
            f"exceptions has to of type 'tuple', not {str(type(exceptions))}"
        )

    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if isinstance(result, dict):
                    result = Result(**result)

                if result is None:
                    result = Result()

                if not isinstance(result, Result):
                    raise TypeError(
                        "Functions that are decorated using 'wrap_result' have to return either a Dictionary"
                        " or an Instance of 'Result'"
                    )
                return ResultWrapper.make_succeeded(**result.result)
            except exceptions as e:
                if hasattr(e, "args"):
                    return ResultWrapper.make_failed(error_information=e.args)
                return ResultWrapper.make_failed(error_information=e)

        return decorator

    return wrapper
