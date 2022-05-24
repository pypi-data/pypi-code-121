#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `rebotics_sdk` package."""

import pytest
from click.testing import CliRunner



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


def test_roles_invoke():
    runner = CliRunner()
    from rebotics_sdk.cli.retailer import api

    result = runner.invoke(api, ['roles'])
    assert result.exit_code == 0


def test_processing_action_group_invoke():
    runner = CliRunner()
    from rebotics_sdk.cli.retailer import api

    result = runner.invoke(api, ['processing-action'])

    result = runner.invoke(api, ['processing-action', 'download'])


def test_configure_command():
    runner = CliRunner()
    # result = runner.invoke(api, ['-r', 'local', 'configure'])
