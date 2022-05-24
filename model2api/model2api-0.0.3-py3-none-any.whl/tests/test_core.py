from cgi import test
import re
from fastapi import File
from pydantic import BaseModel
import pytest
from fastapi.datastructures import UploadFile
from model2api import core
import sys


class DummyClass(BaseModel):
    test: str = "test"


@pytest.mark.parametrize(
    "actual, expected",
    [("helloWorld", "Hello World"), ("one_other_example", "One Other Example")],
)
def test_name_to_title(actual, expected):
    assert core.name_to_title(actual) == expected


@pytest.mark.parametrize(
    "actual, expected",
    [
        (UploadFile, True),
        (File, False),
        (str, False),
        (DummyClass, True),
    ],
)
def test_is_compatible_type(actual, expected):
    assert core.is_compatible_type(actual) == expected


@pytest.mark.parametrize(
    "actual",
    [
        ("datetime.datetime"),
        ("datetime:datetime"),
    ],
)
def test_get_callable(actual):
    callable = core.get_callable(actual)
    assert "datetime" in sys.modules
    assert callable.__name__ == "datetime"
    assert callable(year=2022, month=5, day=22) is not None


def test_get_callable_expect_error():
    with pytest.raises(ValueError, match=r".*MUST specify the function..*"):
        core.get_callable("datetime datetime")


@pytest.mark.parametrize(
    "clz",
    [
        (DummyClass),
        (UploadFile),
    ],
)
def test_get_input_type(clz):
    def function_test(input: clz):
        pass

    output = core.get_input_type(function_test)
    assert issubclass(output, clz)


def test_get_input_type_error():
    def function_test(input: str):
        pass

    with pytest.raises(ValueError, match=r".*MUST be a subclass.*"):
        core.get_input_type(function_test)


@pytest.mark.parametrize(
    "clz",
    [
        (DummyClass),
        (UploadFile),
    ],
)
def test_get_output_type(clz):
    def function_test() -> clz:
        pass

    output = core.get_output_type(function_test)
    assert issubclass(output, clz)


def test_get_output_type_error():
    def function_test() -> str:
        pass

    with pytest.raises(ValueError, match=r".*MUST be a subclass.*"):
        core.get_output_type(function_test)


def test_predictor():
    def function_test(input: DummyClass) -> DummyClass:
        """this is the doc"""
        return input

    predictor = core.Predictor(function_test)
    print(predictor(DummyClass(test="test_")))

    assert predictor.name == "Function Test"
    assert issubclass(predictor.input_type, BaseModel)
    assert issubclass(predictor.output_type, BaseModel)
    assert predictor.description == "this is the doc"

    assert predictor(dict(test="test_")).test == "test_"
    assert predictor(DummyClass(test="test_")).test == "test_"
    assert predictor({"test": "test_"}).test == "test_"
