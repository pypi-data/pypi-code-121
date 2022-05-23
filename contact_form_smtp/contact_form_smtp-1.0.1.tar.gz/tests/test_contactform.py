#!/usr/bin/env python

"""Tests for `contactform` package."""

from click.testing import CliRunner

from contact_form_smtp import __version__, cli


def test_version():
    """Test reading version and module name"""
    assert __version__
    assert isinstance(__version__, str)


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()

    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0, result
    assert "Show this message and exit." in result.output
