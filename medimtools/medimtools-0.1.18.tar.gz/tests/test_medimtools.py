#!/usr/bin/env python

"""Tests for `medimtools` package."""

import pytest

from click.testing import CliRunner

from medimtools import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_viz():
    import SimpleITK as sitk
    import numpy as np
    from medimtools.viz.sitk import quick_view

    image = sitk.Image(256, 256, 32, sitk.sitkInt16)
    assert type(quick_view(image)) == np.ndarray


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "medimtools.cli.main" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
