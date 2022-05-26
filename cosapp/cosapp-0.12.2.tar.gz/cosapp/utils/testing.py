"""Utility functions for testing purposes"""
import numpy
from contextlib import contextmanager


def assert_keys(dictionary, *keys):
    """Utility function to test dictionary keys"""
    if set(dictionary.keys()) != set(keys):
        actual = list(dictionary.keys())
        raise KeyError(f"actual: {actual}; expected: {list(keys)}") 


def assert_all_type(collection, dtype):
    """Asserts that all the elements of a collecion are of a given type"""
    def assert_type(name, value):
        if not isinstance(value, dtype):
            actual = type(value).__name__
            raise TypeError(
                f"{name} is of type {actual}; expected {dtype.__name__}"
            ) 
    if isinstance(collection, dict):
        for key, value in collection.items():
            assert_type(f"element with key '{key}'", value)
    else:
        for i, value in enumerate(collection):
            assert_type(f"element #{i}", value)

def rel_error(actual, expected):
    res = lambda a, b: abs(a) if b == 0 else abs(a / b - 1)
    if isinstance(expected, (list, tuple, numpy.ndarray)):
        return numpy.array([res(a, b) for a, b in zip(actual, expected)])
    else:
        return res(actual, expected)


def get_args(*args, **kwargs):
    """Utility function to collect args and kwargs in a tuple"""
    return args, kwargs


@contextmanager
def no_exception():
    """Context manager to assert that a block does not raise any exception"""
    try:
        yield

    except Exception as error:
        raise AssertionError(f"Unexpected exception raised: {error!r}")


@contextmanager
def not_raised(ExpectedException):
    """Context manager to assert that a block does not raise `ExpectedException`"""
    # https://gist.github.com/oisinmulvihill/45c14271fad7794a4a52516ecb784e69
    try:
        yield

    except ExpectedException as error:
        raise AssertionError(f"Raised {error!r} exception when it should not!")

    except Exception as error:
        raise AssertionError(f"Unexpected exception raised: {error!r}")
