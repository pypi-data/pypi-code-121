#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `forcefield` package."""

import seamm_ff_util  # noqa: F401


def test_angle_explicit(pcff):
    """Test of angle parameters, which shuould fine explicit ones"""

    expected = {
        "K2": "46.0608",
        "K3": "0.0000",
        "K4": "0.0000",
        "Theta0": "106.9999",
        "reference": "8",
    }

    i = "h"
    j = "c"
    k = "br"
    ptype, key, form, parameters = pcff.angle_parameters(i, j, k)
    assert ptype == "explicit"
    assert key == ("br", "c", "h")
    assert parameters == expected


def test_angle_explicit_kji(pcff):
    """known angle parameters, ordered backwards"""
    i = "h"
    j = "c"
    k = "br"
    ptype, key, form, parameters = pcff.angle_parameters(i, j, k)
    ptype2, key2, form, parameters2 = pcff.angle_parameters(k, j, i)
    assert ptype2 == "explicit"
    assert key2 == ("br", "c", "h")
    assert parameters == parameters2


def test_angle_equivalent(pcff):
    """Simple test of angle parameters using equivalencies"""
    expected = {
        "K2": "35.1558",
        "K3": "-12.4682",
        "K4": "0.0000",
        "Theta0": "117.9400",
        "reference": "1",
    }

    i = "c5"
    j = "c5"
    k = "hp"
    ptype, key, form, parameters = pcff.angle_parameters(i, j, k)
    assert ptype == "equivalent"
    assert key == ("cp", "cp", "h")
    assert parameters == expected


def test_angle_auto(pcff):
    """test of angle parameters using automatic parameters"""
    expected = {"K2": "80.0000", "Theta0": "120.0000", "reference": "2"}

    i = "c5"
    j = "c5"
    k = "br"
    ptype, key, form, parameters = pcff.angle_parameters(i, j, k)
    assert ptype == "automatic"
    assert key == ("*7", "cp_", "c_")
    assert parameters == expected
