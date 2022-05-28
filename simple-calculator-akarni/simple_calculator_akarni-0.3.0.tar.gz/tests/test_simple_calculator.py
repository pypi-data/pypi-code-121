#!/usr/bin/env python

"""Tests for `simple_calculator` package."""

import pytest


from simple_calculator import simple_calculator



@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string

def test_add():
    result = simple_calculator.add(3,4)
    assert result == 7

def test_subtract():
    result = simple_calculator.subtract(4,3)
    assert result == 1
