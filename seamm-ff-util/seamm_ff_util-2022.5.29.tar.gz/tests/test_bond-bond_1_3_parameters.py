#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_ff_util` package."""

import seamm_ff_util  # noqa: F401


def test_bond_bond_1_3_explicit(pcff):
    """Test of bond_bond parameters, which should fine explicit ones"""

    expected = {"K": "-3.4826", "reference": "1", "R10": "1.1010", "R30": "1.4170"}

    i = "h"
    j = "c"
    k = "cp"
    l = "cp"  # noqa: E741
    ptype, key, form, parameters = pcff.bond_bond_1_3_parameters(i, j, k, l)
    assert ptype == "explicit"
    assert key == ("h", "c", "cp", "cp")
    assert parameters == expected


def test_bond_bond_1_3_explicit_kji(pcff):
    """known bond_bond parameters, ordered backwards"""
    i = "h"
    j = "c"
    k = "cp"
    l = "cp"  # noqa: E741
    ptype, key, form, parameters = pcff.bond_bond_1_3_parameters(i, j, k, l)
    ptype2, key2, form, parameters2 = pcff.bond_bond_1_3_parameters(l, k, j, i)
    assert ptype2 == "explicit"
    assert key2 == ("h", "c", "cp", "cp")
    assert parameters == parameters2


def test_bond_bond_1_3_equivalent(pcff):
    """Simple test of bond_bond parameters using equivalencies"""
    expected = {"K": "-3.4826", "reference": "1", "R10": "1.1010", "R30": "1.4170"}

    i = "h"
    j = "c1"
    k = "cp"
    l = "cp"  # noqa: E741
    ptype, key, form, parameters = pcff.bond_bond_1_3_parameters(i, j, k, l)
    assert ptype == "equivalent"
    assert key == ("h", "c", "cp", "cp")
    assert parameters == expected
