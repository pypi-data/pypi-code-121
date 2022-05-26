from unittest.mock import call, patch

import pytest
from cli.helpers.utils import filter_dict, get_or_prompt

from sym.flow.cli.errors import InvalidChoiceError


@pytest.fixture
def mock_prompt():
    yield "Pick one"


def test_filter_dict():
    d = {"a": 1, "b": 2}

    filtered_d = filter_dict(d, lambda v: v > 1)
    assert filtered_d == {"b": 2}


@patch("inquirer.list_input")
def test_get_or_prompt_invokes_inquirer(mock_inquire, mock_prompt):
    get_or_prompt(value=None, prompt=mock_prompt, choices=["foo", "bar"])
    # choices are sorted before invoking inquire
    mock_inquire.assert_has_calls([call(mock_prompt, choices=["bar", "foo"])])


@patch("click.echo")
def test_get_or_prompt_auto_selects(mock_echo, mock_prompt):
    # value = None, but only one choice available. Auto selects
    result = get_or_prompt(value=None, prompt=mock_prompt, choices=["foo"])
    assert result == "foo"
    mock_echo.assert_has_calls([call(f"{mock_prompt}: Using 'foo'")])


def test_get_or_prompt_invalid_choice(mock_prompt):
    with pytest.raises(InvalidChoiceError):
        get_or_prompt(value="bad", prompt=mock_prompt, choices=["foo"])


def test_get_or_prompt(mock_prompt):
    # value exists and is valid
    assert get_or_prompt(value="foo", prompt=mock_prompt, choices=["foo", "bar"]) == "foo"
