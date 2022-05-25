#!/usr/bin/env python

"""Tests for `julian_to_datetime` function."""

import datetime

import pytest

from src.zos_utilities import julian_to_datetime


def test_five_digits():
    input_date = '05132'

    correct_ouput = datetime.datetime(2005, 5, 12)

    assert julian_to_datetime.julian_to_datetime(input_date) == correct_ouput


def test_seven_digits():
    input_date = '2012313'

    correct_output = datetime.datetime(2012, 11, 8)

    assert julian_to_datetime.julian_to_datetime(input_date) == correct_output


def test_six_digits():
    inputdate = '012313'

    with pytest.raises(julian_to_datetime.UtilityException):
        julian_to_datetime.julian_to_datetime(inputdate)


def test_invalid_date():
    inputdate = '1943742'

    with pytest.raises(ValueError):
        julian_to_datetime.julian_to_datetime(inputdate)
