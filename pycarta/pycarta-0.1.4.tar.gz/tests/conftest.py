# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for pycarta.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest


def pytest_addoption(parser):
    parser.addoption("--workspace", action="store", default="Carta Development")
    parser.addoption("--template", action="store", default="pytest")
    parser.addoption("--name", action="store", default=None)


@pytest.fixture
def workspace(request):
    return request.config.getoption("workspace")


@pytest.fixture
def template(request):
    return request.config.getoption("template")


@pytest.fixture
def name(request):
    return request.config.getoption("name")
