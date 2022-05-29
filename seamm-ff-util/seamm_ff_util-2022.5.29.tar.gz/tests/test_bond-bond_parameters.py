#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_ff_util` package."""

import seamm_ff_util  # noqa: F401


def test_bond_bond_explicit(pcff):
    """Test of bond_bond parameters, which should fine explicit ones"""

    expected = {"K": "3.3872", "reference": "1", "R20": "1.1010", "R10": "1.5300"}

    i = "h"
    j = "c"
    k = "c"
    ptype, key, form, parameters = pcff.bond_bond_parameters(i, j, k)
    assert ptype == "explicit"
    assert key == ("c", "c", "h")
    assert parameters == expected


def test_bond_bond_explicit_kji(pcff):
    """known bond_bond parameters, ordered backwards"""
    i = "c"
    j = "c"
    k = "h"
    ptype, key, form, parameters = pcff.bond_bond_parameters(i, j, k)
    ptype2, key2, form, parameters2 = pcff.bond_bond_parameters(k, j, i)
    assert ptype2 == "explicit"
    assert key2 == ("c", "c", "h")
    assert parameters == parameters2


def test_bond_bond_equivalent(pcff):
    """Simple test of bond_bond parameters using equivalencies"""
    expected = {"K": "3.3872", "reference": "1", "R20": "1.1010", "R10": "1.5300"}

    i = "h"
    j = "c"
    k = "c1"
    ptype, key, form, parameters = pcff.bond_bond_parameters(i, j, k)
    assert ptype == "equivalent"
    assert key == ("c", "c", "h")
    assert parameters == expected
