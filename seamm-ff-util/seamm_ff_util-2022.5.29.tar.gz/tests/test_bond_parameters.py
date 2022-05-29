#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_ff_util` package."""

import seamm_ff_util  # noqa: F401


def test_bond_explicit(pcff):
    """Simple test of known bond parameters"""
    expected = {
        "K2": "345.0000",
        "K3": "-691.8900",
        "K4": "844.6000",
        "R0": "1.1010",
        "reference": "8",
    }

    i = "c"
    j = "h"
    ptype, key, form, parameters = pcff.bond_parameters(i, j)
    assert ptype == "explicit"
    assert key == ("c", "h")
    assert parameters == expected


def test_bond_explicit_ji(pcff):
    """Simple test of known bond parameters, ordered backwards"""
    i = "c"
    j = "h"
    ptype, key, form, parameters = pcff.bond_parameters(i, j)
    ptype2, key2, form, parameters2 = pcff.bond_parameters(j, i)
    assert ptype2 == "explicit"
    assert key2 == ("c", "h")
    assert parameters == parameters2


def test_bond_equivalent(pcff):
    """Simple test of bond parameters using equivalencies"""
    expected = {
        "K2": "372.8251",
        "K3": "-803.4526",
        "K4": "894.3173",
        "R0": "1.0982",
        "reference": "8",
    }

    i = "c5"
    j = "hp"
    ptype, key, form, parameters = pcff.bond_parameters(i, j)
    assert ptype == "equivalent"
    assert key == ("cp", "h")
    assert parameters == expected


def test_bond_auto(pcff):
    """Simple test of bond parameters using automatic parameters"""
    expected = {"K2": "223.6000", "R0": "1.9200", "reference": "2"}

    i = "c5"
    j = "br"
    ptype, key, form, parameters = pcff.bond_parameters(i, j)
    assert ptype == "automatic"
    assert key == ("br_", "cp_")
    assert parameters == expected
